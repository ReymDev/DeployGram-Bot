from __future__ import annotations

import hashlib
import io
import json
import logging
import zipfile
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
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

    async def save_project_files(self, project_id: int, files_zip: bytes) -> bool:
        project_dir = self.get_project_dir(project_id)
        try:
            with zipfile.ZipFile(io.BytesIO(files_zip), "r") as zf:
                zf.extractall(project_dir)
            return True
        except Exception as e:
            logger.error("Failed to save project files for %d: %s", project_id, e)
            return False

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

            project_dir = str(self.get_project_dir(project_id))
            import os
            zip_path = os.path.join(project_dir, "project.zip")
            if os.path.exists(zip_path):
                with open(zip_path, "rb") as f:
                    await client.upload_project(project_id, f.read())

            result = await client.create_container({
                "project_id": project_id,
                "project_name": project.name,
                "python_version": project.python_version,
                "entry_point": project.entry_point,
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
                project_dir = str(self.get_project_dir(project_id))
                container_id = await self.docker.create_container(
                    project_id=project_id,
                    project_name=project.name,
                    python_version=project.python_version,
                    entry_point=project.entry_point,
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
        if project is None or not project.docker_container_id or not self.docker:
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
        if project is None or not project.docker_container_id or not self.docker:
            return "Проект не запущен"
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
                names = zf.namelist()
                for entry in ENTRY_FILES:
                    if entry in names:
                        return entry
                for name in names:
                    basename = Path(name).name
                    if basename in ENTRY_FILES:
                        return basename
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

    async def list_files(self, project_id: int, path: str = "/app") -> list[str]:
        project = await self.project_repo.get_by_id(project_id)
        if not project or not project.docker_container_id or not self.docker:
            return []
        return await self.docker.list_files(project.docker_container_id, path)

    async def read_file(self, project_id: int, file_path: str) -> str:
        project = await self.project_repo.get_by_id(project_id)
        if not project or not project.docker_container_id or not self.docker:
            return ""
        return await self.docker.read_file(project.docker_container_id, file_path)

    async def write_file(self, project_id: int, file_path: str, content: str) -> bool:
        project = await self.project_repo.get_by_id(project_id)
        if not project or not project.docker_container_id or not self.docker:
            return False
        return await self.docker.write_file(project.docker_container_id, file_path, content)

    async def delete_file(self, project_id: int, file_path: str) -> bool:
        project = await self.project_repo.get_by_id(project_id)
        if not project or not project.docker_container_id or not self.docker:
            return False
        return await self.docker.delete_file(project.docker_container_id, file_path)

    async def create_dir(self, project_id: int, dir_path: str) -> bool:
        project = await self.project_repo.get_by_id(project_id)
        if not project or not project.docker_container_id or not self.docker:
            return False
        return await self.docker.create_dir(project.docker_container_id, dir_path)

    async def clear_logs(self, project_id: int) -> bool:
        project = await self.project_repo.get_by_id(project_id)
        if not project or not project.docker_container_id or not self.docker:
            return False
        return await self.docker.clear_logs(project.docker_container_id)
