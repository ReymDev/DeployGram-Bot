from __future__ import annotations

import asyncio
import hashlib
import io
import json
import logging
import os
import zipfile
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings, BASE_DIR
from models.project import Project, ProjectVersion, ProjectStats
from repositories.project import ProjectRepository, ProjectVersionRepository, ProjectStatsRepository
from repositories.user import UserRepository

try:
    from services.docker_manager import DockerManager
    _HAS_DOCKER = True
except ImportError:
    _HAS_DOCKER = False

logger = logging.getLogger(__name__)

ENTRY_FILES = ["main.py", "bot.py", "run.py", "app.py"]
PYTHON_VERSIONS = ("3.10", "3.11", "3.12")


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.project_repo = ProjectRepository(session)
        self.version_repo = ProjectVersionRepository(session)
        self.stats_repo = ProjectStatsRepository(session)
        self.docker = DockerManager() if _HAS_DOCKER else None

    def get_project_dir(self, project_id: int) -> Path:
        project_dir = BASE_DIR / "data" / "projects" / str(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir

    def _get_single_top_dir(self, project_dir: Path) -> str | None:
        dirs = [
            p
            for p in project_dir.iterdir()
            if p.is_dir() and p.name not in {".venv", "__pycache__"}
        ]
        if len(dirs) == 1:
            return dirs[0].name
        return None

    def _resolve_script_entry(self, project_dir: Path, entry_point: str) -> str | None:
        entry_point_norm = entry_point.replace("\\", "/")
        if (project_dir / entry_point_norm).is_file():
            return entry_point_norm

        top_dir = self._get_single_top_dir(project_dir)
        if top_dir and (project_dir / top_dir / entry_point_norm).is_file():
            return f"{top_dir}/{entry_point_norm}"

        # Fallback: if user specified only basename (e.g. "main.py"),
        # try to find it anywhere under the extracted project.
        basename = Path(entry_point_norm).name
        if basename == entry_point_norm and "/" not in entry_point_norm:
            for root, _, files in os.walk(project_dir):
                if basename in files:
                    rel = os.path.relpath(os.path.join(root, basename), project_dir)
                    return rel.replace("\\", "/")
        return None

    def _module_exists(self, project_dir: Path, module: str) -> bool:
        module_path = module.replace(".", "/")
        return (project_dir / f"{module_path}.py").is_file() or (
            project_dir / module_path / "__init__.py"
        ).is_file()

    def _resolve_module_env(
        self, project_dir: Path, entry_point: str, env_vars: dict[str, str]
    ) -> bool:
        """
        Returns True when module is resolvable.
        If code is nested in a single top-level directory, sets PYTHONPATH accordingly.
        """
        if self._module_exists(project_dir, entry_point):
            return True

        top_dir = self._get_single_top_dir(project_dir)
        if top_dir and self._module_exists(project_dir / top_dir, entry_point):
            env_vars.setdefault("PYTHONPATH", f"/app/{top_dir}")
            return True
        return False

    async def save_project_files(self, project_id: int, files_zip) -> bool:
        project_dir = self.get_project_dir(project_id)
        logger.info("Saving project files for project %d to %s", project_id, project_dir)

        def _save() -> bool:
            try:
                if isinstance(files_zip, bytes):
                    zip_data = files_zip
                elif isinstance(files_zip, io.BytesIO):
                    zip_data = files_zip.read()
                else:
                    zip_data = bytes(files_zip)

                if len(zip_data) == 0:
                    logger.error("ZIP data is empty for project %d!", project_id)
                    return False

                zip_path = project_dir / "project.zip"
                with open(zip_path, "wb") as f:
                    f.write(zip_data)

                with zipfile.ZipFile(io.BytesIO(zip_data), "r") as zf:
                    for member in zf.infolist():
                        target = (project_dir / member.filename).resolve()
                        if not str(target).startswith(str(project_dir.resolve())):
                            logger.warning("Zip slip detected: %s", member.filename)
                            return False
                    zf.extractall(project_dir)
                return True
            except Exception as e:
                logger.error("Failed to save project files for %d: %s", project_id, e, exc_info=True)
                return False

        return await asyncio.to_thread(_save)

    async def create_project(
        self,
        user_id: int,
        name: str,
        source_type: str,
        source_url: str | None = None,
        python_version: str = "3.12",
        entry_point: str = "main.py",
        entry_type: str = "script",
        server_id: int | None = None,
        files_zip: bytes | None = None,
    ) -> Project:
        project = await self.project_repo.create(
            user_id=user_id,
            name=name,
            source_type=source_type,
            source_url=source_url,
            python_version=python_version,
            entry_point=entry_point,
            entry_type=entry_type,
            server_id=server_id,
            status="stopped",
        )
        if files_zip:
            await self.save_project_files(project.id, files_zip)
        return project

    async def get_user_projects(self, user_id: int) -> list[Project]:
        return await self.project_repo.get_by_user_id(user_id)

    async def get_project(self, project_id: int) -> Project | None:
        return await self.project_repo.get_by_id(project_id)

    async def delete_project(self, project_id: int) -> bool:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            return False
        if project.docker_container_id and self.docker:
            await self.docker.remove_container(project.docker_container_id)
        return await self.project_repo.delete(project_id)

    async def start_project(self, project_id: int) -> tuple[bool, str]:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            return False, "Проект не найден"

        if project.docker_container_id:
            if self.docker:
                status = await self.docker.get_container_status(project.docker_container_id)
                if status.get("running"):
                    return True, "Контейнер уже запущен"
                await self.docker.remove_container(project.docker_container_id)

        user_repo = UserRepository(self.session)
        user = await user_repo.get_by_id(project.user_id)
        tariff = user.tariff if user else "free"

        version = await self.version_repo.get_latest(project_id)
        env_vars = {}
        if version and version.secrets:
            try:
                env_vars = json.loads(version.secrets)
            except (json.JSONDecodeError, TypeError):
                pass

        project_dir_path = self.get_project_dir(project_id)

        # Resolve entry point against the extracted filesystem structure.
        # This fixes common cases where the ZIP is wrapped into a single top-level folder.
        resolved_entry_point: str | None = project.entry_point
        if project.entry_type == "script":
            resolved_entry_point = self._resolve_script_entry(project_dir_path, project.entry_point)
            if resolved_entry_point is None:
                candidates: list[str] = []
                try:
                    for p in project_dir_path.rglob("*.py"):
                        candidates.append(p.relative_to(project_dir_path).as_posix())
                        if len(candidates) >= 10:
                            break
                except Exception:
                    pass
                details = ", ".join(candidates) if candidates else "—"
                return False, f"Точка входа {project.entry_point!r} не найдена в проекте. Доступные .py: {details}"
        else:
            if not self._resolve_module_env(project_dir_path, project.entry_point, env_vars):
                candidates: list[str] = []
                try:
                    for p in project_dir_path.rglob("*.py"):
                        candidates.append(p.relative_to(project_dir_path).as_posix())
                        if len(candidates) >= 10:
                            break
                except Exception:
                    pass
                details = ", ".join(candidates) if candidates else "—"
                return False, f"Модуль {project.entry_point!r} не найден в проекте. Доступные .py: {details}"

        if project.server_id:
            from repositories.server import ServerRepository
            from services.vps_agent import VPSClient
            server_repo = ServerRepository(self.session)
            server = await server_repo.get_by_id(project.server_id)
            if server is None:
                return False, "Сервер не найден"

            client = VPSClient(
                base_url=f"http://{server.ip}:{server.port}",
                api_key=server.api_key or "",
            )

            project_dir = project_dir_path
            zip_path = project_dir / "project.zip"

            if zip_path.exists():
                def _read_zip():
                    with open(zip_path, "rb") as f:
                        return f.read()
                zip_data = await asyncio.to_thread(_read_zip)
                await client.upload_project(project_id, zip_data)
            else:
                def _create_zip():
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                        for root, dirs, files in os.walk(project_dir):
                            for file in files:
                                if file == "project.zip":
                                    continue
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, project_dir)
                                zf.write(file_path, arcname)
                    return zip_buffer.getvalue()
                zip_data = await asyncio.to_thread(_create_zip)
                await client.upload_project(project_id, zip_data)

            result = await client.create_container({
                "project_id": project_id,
                "project_name": project.name,
                "python_version": project.python_version,
                "entry_point": resolved_entry_point or project.entry_point,
                "entry_type": project.entry_type,
                "tariff": tariff,
                "env_vars": env_vars,
            })
            if "error" in result:
                return False, result["error"]

            container_id = result.get("container_id", "")
            await client.start_container(container_id)
            await self.project_repo.update(project_id, docker_container_id=container_id, status="running")
            return True, "Проект запущен"
        else:
            if not self.docker:
                return False, "Docker недоступен"

            try:
                project_dir = str(project_dir_path)
                container_id = await self.docker.create_container(
                    project_id=project_id,
                    project_name=project.name,
                    python_version=project.python_version,
                    entry_point=resolved_entry_point or project.entry_point,
                    entry_type=project.entry_type,
                    tariff=tariff,
                    env_vars=env_vars,
                    project_dir=project_dir,
                )
                await self.docker.start_container(container_id)
                await self.project_repo.update(project_id, docker_container_id=container_id, status="running")
                return True, "Проект запущен"
            except Exception as e:
                logger.error("Failed to start project %d: %s", project_id, e)
                await self.project_repo.update(project_id, status="error")
                return False, f"Ошибка запуска: {e}"

    async def stop_project(self, project_id: int) -> tuple[bool, str]:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            return False, "Проект не найден"
        if not project.docker_container_id:
            await self.project_repo.update(project_id, status="stopped")
            return True, "Проект уже остановлен"

        if project.server_id:
            from repositories.server import ServerRepository
            from services.vps_agent import VPSClient
            server_repo = ServerRepository(self.session)
            server = await server_repo.get_by_id(project.server_id)
            if server:
                client = VPSClient(
                    base_url=f"http://{server.ip}:{server.port}",
                    api_key=server.api_key or "",
                )
                await client.stop_container(project.docker_container_id)
                await self.project_repo.update(project_id, status="stopped")
                return True, "Проект остановлен"

        if not self.docker:
            return False, "Docker недоступен"

        await self.docker.stop_container(project.docker_container_id)
        await self.project_repo.update(project_id, status="stopped")
        return True, "Проект остановлен"

    async def restart_project(self, project_id: int) -> tuple[bool, str]:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            return False, "Проект не найден"

        if project.docker_container_id and self.docker:
            await self.docker.stop_container(project.docker_container_id)
            await self.docker.remove_container(project.docker_container_id)

        success, msg = await self.start_project(project_id)
        if success:
            await self.project_repo.update(
                project_id, restart_count=project.restart_count + 1
            )
        return success, msg

    async def get_monitoring(self, project_id: int) -> dict:
        project = await self.project_repo.get_by_id(project_id)
        if project is None or not project.docker_container_id:
            return {"status": "stopped", "cpu": 0, "ram": 0, "disk": 0, "uptime": "—", "restarts": 0}

        if project.server_id:
            from repositories.server import ServerRepository
            from services.vps_agent import VPSClient
            server_repo = ServerRepository(self.session)
            server = await server_repo.get_by_id(project.server_id)
            if server:
                client = VPSClient(
                    base_url=f"http://{server.ip}:{server.port}",
                    api_key=server.api_key or "",
                )
                try:
                    status = await client.get_status(project.docker_container_id)
                    stats = await client.get_stats(project.docker_container_id)
                    return {
                        "status": "running" if status.get("running") else "stopped",
                        "cpu": stats.get("cpu_percent", 0),
                        "ram": stats.get("ram_mb", 0),
                        "disk": stats.get("disk_mb", 0),
                        "uptime": "—",
                        "restarts": project.restart_count,
                    }
                except Exception:
                    pass

        if not self.docker:
            return {"status": "stopped", "cpu": 0, "ram": 0, "disk": 0, "uptime": "—", "restarts": 0}

        status = await self.docker.get_container_status(project.docker_container_id)
        stats = await self.docker.get_container_stats(project.docker_container_id)

        return {
            "status": "running" if status.get("running") else "stopped",
            "cpu": stats.get("cpu_percent", 0),
            "ram": stats.get("ram_mb", 0),
            "disk": stats.get("disk_mb", 0),
            "uptime": "—",
            "restarts": project.restart_count,
        }

    async def get_logs(self, project_id: int, tail: int = 100) -> str:
        project = await self.project_repo.get_by_id(project_id)
        if project is None or not project.docker_container_id:
            return "Проект не запущен"

        if project.server_id:
            from repositories.server import ServerRepository
            from services.vps_agent import VPSClient
            server_repo = ServerRepository(self.session)
            server = await server_repo.get_by_id(project.server_id)
            if server:
                client = VPSClient(
                    base_url=f"http://{server.ip}:{server.port}",
                    api_key=server.api_key or "",
                )
                try:
                    result = await client.get_logs(project.docker_container_id, tail)
                    return result.get("logs", "")
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to get logs from VPS for project {project_id}: {e}")
                    return f"Ошибка получения логов: {str(e)}"

        if not self.docker:
            return "Docker недоступен"

        return await self.docker.get_container_logs(project.docker_container_id, tail)

    async def save_version(
        self,
        project_id: int,
        files_zip: bytes | None = None,
        requirements: str | None = None,
        entry_point: str | None = None,
        secrets: str | None = None,
        python_version: str | None = None,
    ) -> ProjectVersion:
        latest = await self.version_repo.get_latest(project_id)
        next_version = (latest.version_number + 1) if latest else 1

        files_hash = None
        if files_zip:
            files_hash = hashlib.sha256(files_zip).hexdigest()

        return await self.version_repo.create(
            project_id=project_id,
            version_number=next_version,
            files_hash=files_hash,
            requirements=requirements,
            entry_point=entry_point or "main.py",
            secrets=secrets,
            python_version=python_version or "3.12",
        )

    async def get_versions(self, project_id: int) -> list[ProjectVersion]:
        return await self.version_repo.get_by_project_id(project_id)

    async def restore_version(self, project_id: int, version_id: int) -> bool:
        version = await self.version_repo.get_by_id(version_id)
        if version is None or version.project_id != project_id:
            return False
        await self.project_repo.update(
            project_id,
            entry_point=version.entry_point,
            python_version=version.python_version,
        )
        return True

    async def get_stats_history(self, project_id: int, limit: int = 100) -> list[ProjectStats]:
        return await self.stats_repo.get_by_project_id(project_id, limit)

    async def save_stats(self, project_id: int, cpu: float, ram: float, disk: float):
        await self.stats_repo.create(
            project_id=project_id,
            cpu_percent=cpu,
            ram_mb=ram,
            disk_mb=disk,
        )

    async def test_project(
        self, files_zip: bytes, python_version: str, entry_point: str, entry_type: str
    ) -> tuple[bool, str]:
        if not self.docker:
            return False, "Docker недоступен"
        return await self.docker.test_container(files_zip, python_version, entry_point, entry_type)

    async def auto_find_entry(self, files_zip: bytes) -> str | None:
        try:
            with zipfile.ZipFile(io.BytesIO(files_zip), "r") as zf:
                names = [n for n in zf.namelist() if not n.endswith("/")]
                # Prefer exact filename matches, but return the full relative path,
                # so archives wrapped into a top-level directory work too.
                for entry in ENTRY_FILES:
                    for name in names:
                        if Path(name).name == entry:
                            return name.replace("\\", "/")
        except zipfile.BadZipFile:
            pass
        return None

    async def validate_project(self, files_zip: bytes) -> dict:
        errors = []
        has_requirements = False
        python_files = []

        try:
            with zipfile.ZipFile(io.BytesIO(files_zip), "r") as zf:
                names = zf.namelist()
                if not names:
                    errors.append("ZIP архив пуст")

                for name in names:
                    basename = Path(name).name
                    if basename == "requirements.txt":
                        has_requirements = True
                    if basename.endswith(".py"):
                        python_files.append(name)

                if not python_files:
                    errors.append("Не найдены Python файлы")

                for py_file in python_files:
                    try:
                        content = zf.read(py_file).decode("utf-8", errors="replace")
                        compile(content, py_file, "exec")
                    except SyntaxError as e:
                        errors.append(f"Синтаксическая ошибка в {py_file}: {e}")

        except zipfile.BadZipFile:
            errors.append("Невалидный ZIP файл")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "has_requirements": has_requirements,
            "python_files": python_files,
        }

    async def count_user_projects(self, user_id: int) -> int:
        return await self.project_repo.count_by_user(user_id)

    def _validate_path(self, path: str) -> str:
        """Validate and normalize file path to prevent path traversal attacks."""
        import os
        from pathlib import Path
        
        # Remove any null bytes
        path = path.replace('\0', '')
        
        # Normalize path
        path = os.path.normpath(path)
        
        # Ensure path starts with /app or is relative
        if not path.startswith('/app'):
            path = f"/app/{path.lstrip('/')}"
        
        # Resolve and check if still under /app
        try:
            normalized = str(Path(path).resolve())
            if not normalized.startswith('/app'):
                raise ValueError("Path traversal attempt detected")
        except Exception:
            raise ValueError("Invalid file path")
        
        return path

    async def list_files(self, project_id: int, path: str = "/app") -> list[str]:
        project = await self.project_repo.get_by_id(project_id)
        if not project or not project.docker_container_id:
            return []

        # Validate path to prevent path traversal
        try:
            safe_path = self._validate_path(path)
        except ValueError as e:
            logger.warning(f"Path validation failed for project {project_id}: {e}")
            return []

        if project.server_id:
            from repositories.server import ServerRepository
            from services.vps_agent import VPSClient
            server_repo = ServerRepository(self.session)
            server = await server_repo.get_by_id(project.server_id)
            if server:
                client = VPSClient(
                    base_url=f"http://{server.ip}:{server.port}",
                    api_key=server.api_key or "",
                )
                try:
                    result = await client.list_files(project_id, safe_path)
                    return result.get("files", [])
                except Exception:
                    return []

        if not self.docker:
            return []

        return await self.docker.list_files(project.docker_container_id, safe_path)

    async def read_file(self, project_id: int, file_path: str) -> str:
        project = await self.project_repo.get_by_id(project_id)
        if not project or not project.docker_container_id:
            return ""

        # Validate path to prevent path traversal
        try:
            safe_path = self._validate_path(file_path)
        except ValueError as e:
            logger.warning(f"Path validation failed for project {project_id}: {e}")
            return ""

        if project.server_id:
            from repositories.server import ServerRepository
            from services.vps_agent import VPSClient
            server_repo = ServerRepository(self.session)
            server = await server_repo.get_by_id(project.server_id)
            if server:
                client = VPSClient(
                    base_url=f"http://{server.ip}:{server.port}",
                    api_key=server.api_key or "",
                )
                try:
                    result = await client.read_file(project_id, safe_path)
                    return result.get("content", "")
                except Exception:
                    return ""

        if not self.docker:
            return ""

        return await self.docker.read_file(project.docker_container_id, safe_path)

    async def write_file(self, project_id: int, file_path: str, content: str) -> bool:
        project = await self.project_repo.get_by_id(project_id)
        if not project or not project.docker_container_id:
            return False

        # Validate path to prevent path traversal
        try:
            safe_path = self._validate_path(file_path)
        except ValueError as e:
            logger.warning(f"Path validation failed for project {project_id}: {e}")
            return False
        
        # Validate content size (max 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024
        if len(content.encode('utf-8')) > MAX_FILE_SIZE:
            logger.warning(f"File too large for project {project_id}: {len(content)} bytes")
            return False

        if project.server_id:
            from repositories.server import ServerRepository
            from services.vps_agent import VPSClient
            server_repo = ServerRepository(self.session)
            server = await server_repo.get_by_id(project.server_id)
            if server:
                client = VPSClient(
                    base_url=f"http://{server.ip}:{server.port}",
                    api_key=server.api_key or "",
                )
                try:
                    result = await client.write_file(project_id, safe_path, content)
                    return result.get("status") == "ok"
                except Exception:
                    return False

        if not self.docker:
            return False

        return await self.docker.write_file(project.docker_container_id, safe_path, content)

    async def delete_file(self, project_id: int, file_path: str) -> bool:
        project = await self.project_repo.get_by_id(project_id)
        if not project or not project.docker_container_id:
            return False

        # Validate path to prevent path traversal
        try:
            safe_path = self._validate_path(file_path)
        except ValueError as e:
            logger.warning(f"Path validation failed for project {project_id}: {e}")
            return False
        
        # Prevent deletion of critical files
        critical_files = ['requirements.txt', '__init__.py']
        if any(safe_path.endswith(f"/{cf}") for cf in critical_files):
            logger.warning(f"Attempt to delete critical file: {safe_path}")
            # Allow deletion but log it
            pass

        if project.server_id:
            from repositories.server import ServerRepository
            from services.vps_agent import VPSClient
            server_repo = ServerRepository(self.session)
            server = await server_repo.get_by_id(project.server_id)
            if server:
                client = VPSClient(
                    base_url=f"http://{server.ip}:{server.port}",
                    api_key=server.api_key or "",
                )
                try:
                    result = await client.delete_file(project_id, safe_path)
                    return result.get("status") == "ok"
                except Exception:
                    return False

        if not self.docker:
            return False

        return await self.docker.delete_file(project.docker_container_id, safe_path)

    async def create_dir(self, project_id: int, dir_path: str) -> bool:
        project = await self.project_repo.get_by_id(project_id)
        if not project or not project.docker_container_id:
            return False
        if not self.docker:
            return False
        return await self.docker.create_dir(project.docker_container_id, dir_path)

    async def clear_logs(self, project_id: int) -> bool:
        project = await self.project_repo.get_by_id(project_id)
        if not project or not project.docker_container_id:
            return False
        if not self.docker:
            return False
        return await self.docker.clear_logs(project.docker_container_id)

    async def get_installed_packages(self, project_id: int) -> list[str]:
        """Get list of installed Python packages from project container."""
        project = await self.project_repo.get_by_id(project_id)
        if not project or not project.docker_container_id:
            return []

        # TODO: VPS support for get_installed_packages
        # if project.server_id:
        #     Add VPS Agent API endpoint for pip list

        if not self.docker:
            return []

        return await self.docker.get_installed_packages(project.docker_container_id)
