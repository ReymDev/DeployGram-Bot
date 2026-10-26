from __future__ import annotations

import asyncio
import json
import logging
import os
import posixpath
import re
import shlex
from typing import Any

import docker
from docker.errors import APIError, ImageNotFound, NotFound
from docker.models.containers import Container

from services.archive import ArchiveError, safe_extract_zip

logger = logging.getLogger(__name__)

CONTAINER_NAME_RE = re.compile(r"[^a-zA-Z0-9_.-]+")
MODULE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$")
SCRIPT_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_./-]{0,510}$")

PYTHON_IMAGES = {
    "3.10": "python:3.10-slim",
    "3.11": "python:3.11-slim",
    "3.12": "python:3.12-slim",
}


def _container_name(project_id: int, project_name: str) -> str:
    slug = CONTAINER_NAME_RE.sub("-", str(project_name)).strip("-_.")[:48] or "project"
    return f"deploygram_{int(project_id)}_{slug}"


def _validate_entry(entry_point: str, entry_type: str) -> str:
    entry = (entry_point or "").replace("\\", "/").strip()
    if not entry or entry.startswith("/") or ".." in entry.split("/"):
        raise ValueError("Некорректная точка входа")
    if entry_type == "module":
        if not MODULE_RE.fullmatch(entry):
            raise ValueError("Некорректное имя модуля")
    elif not SCRIPT_RE.fullmatch(entry):
        raise ValueError("Некорректный путь точки входа")
    return entry


def _get_limits(tariff: str) -> dict[str, Any]:
    if tariff == "premium":
        return {
            "cpu_quota": int(float(os.getenv("PREMIUM_TARIFF_CPU", "1.0")) * 100000),
            "mem_limit": f"{os.getenv('PREMIUM_TARIFF_RAM', '1024')}m",
            "storage_opt": {"size": f"{os.getenv('PREMIUM_TARIFF_DISK', '500')}m"},
        }
    return {
        "cpu_quota": int(float(os.getenv("FREE_TARIFF_CPU", "0.3")) * 100000),
        "mem_limit": f"{os.getenv('FREE_TARIFF_RAM', '256')}m",
        "storage_opt": {"size": f"{os.getenv('FREE_TARIFF_DISK', '100')}m"},
    }


class DockerManager:
    def __init__(self) -> None:
        self.client = docker.from_env()

    async def create_container(
        self,
        project_id: int,
        project_name: str,
        python_version: str,
        entry_point: str,
        entry_type: str,
        tariff: str,
        env_vars: dict[str, str] | None = None,
        work_dir: str = "/app",
        project_dir: str | None = None,
    ) -> str:
        def _create() -> str:
            image = PYTHON_IMAGES.get(python_version, PYTHON_IMAGES["3.12"])
            limits = _get_limits(tariff)
            entry_type = entry_type if entry_type in ("script", "module") else "script"

            entry_point_norm = _validate_entry(entry_point, entry_type)
            entry_point_quoted = shlex.quote(entry_point_norm)
            entry_dir = entry_point_norm.rsplit("/", 1)[0] if "/" in entry_point_norm else ""

            env_list = [f"{k}={v}" for k, v in (env_vars or {}).items()]

            if entry_type == "module":
                python_cmd = f"/tmp/venv/bin/python -m {entry_point_quoted}"
                req_install = "if [ -f ./requirements.txt ]; then " \
                    f"/tmp/venv/bin/pip install --no-cache-dir -r ./requirements.txt; fi"
            else:
                python_cmd = f"/tmp/venv/bin/python {entry_point_quoted}"
                if entry_dir:
                    req_install = (
                        "if [ -f ./requirements.txt ]; then "
                        "/tmp/venv/bin/pip install --no-cache-dir -r ./requirements.txt; "
                        f"elif [ -f {shlex.quote(f'./{entry_dir}/requirements.txt')} ]; then "
                        f"/tmp/venv/bin/pip install --no-cache-dir -r {shlex.quote(f'./{entry_dir}/requirements.txt')}; "
                        "fi"
                    )
                else:
                    req_install = (
                        "if [ -f ./requirements.txt ]; then "
                        "/tmp/venv/bin/pip install --no-cache-dir -r ./requirements.txt; "
                        "fi"
                    )

            volumes = {}
            if project_dir:
                volumes[project_dir] = {"bind": "/app", "mode": "rw"}
                logger.info(
                    "Mounting volume: host=%s -> container=/app for project %s",
                    project_dir, project_id
                )

            container_name = _container_name(project_id, project_name)

            try:
                old = self.client.containers.get(container_name)
                old.remove(force=True)
                logger.info("Removed old container: %s", container_name)
            except (NotFound, APIError):
                pass

            full_command = f"python -m venv /tmp/venv && {req_install} && exec {python_cmd}"
            logger.info(
                "Creating container %s: entry_point=%s, command=%s",
                container_name, entry_point_norm, full_command
            )

            container = self.client.containers.run(
                image=image,
                command=[
                    "/bin/sh",
                    "-c",
                    full_command,
                ],
                detach=True,
                name=container_name,
                working_dir=work_dir,
                volumes=volumes,
                environment=env_list,
                cpu_quota=limits["cpu_quota"],
                mem_limit=limits["mem_limit"],
                memswap_limit=limits["mem_limit"],
                pids_limit=256,
                storage_opt=limits.get("storage_opt", {}),
                read_only=False,
                network_disabled=False,
                security_opt=["no-new-privileges"],
                user="1000:1000",
                labels={
                    "deploygram": "true",
                    "project_id": str(project_id),
                },
                restart_policy={"Name": "on-failure", "MaximumRetryCount": 3},
            )
            logger.info("Container created successfully: %s", container.id)
            return container.id

        return await asyncio.to_thread(_create)

    async def start_container(self, container_id: str) -> bool:
        def _start() -> bool:
            try:
                container = self.client.containers.get(container_id)
                container.start()
                return True
            except (NotFound, APIError) as e:
                logger.error("Failed to start container %s: %s", container_id, e)
                return False

        return await asyncio.to_thread(_start)

    async def stop_container(self, container_id: str, timeout: int = 10) -> bool:
        def _stop() -> bool:
            try:
                container = self.client.containers.get(container_id)
                container.stop(timeout=timeout)
                return True
            except (NotFound, APIError) as e:
                logger.error("Failed to stop container %s: %s", container_id, e)
                return False

        return await asyncio.to_thread(_stop)

    async def remove_container(self, container_id: str) -> bool:
        def _remove() -> bool:
            try:
                container = self.client.containers.get(container_id)
                container.remove(force=True)
                return True
            except (NotFound, APIError) as e:
                logger.error("Failed to remove container %s: %s", container_id, e)
                return False

        return await asyncio.to_thread(_remove)

    async def restart_container(self, container_id: str) -> bool:
        def _restart() -> bool:
            try:
                container = self.client.containers.get(container_id)
                container.restart()
                return True
            except (NotFound, APIError) as e:
                logger.error("Failed to restart container %s: %s", container_id, e)
                return False

        return await asyncio.to_thread(_restart)

    async def get_container_status(self, container_id: str) -> dict[str, Any]:
        def _status() -> dict[str, Any]:
            try:
                container = self.client.containers.get(container_id)
                container.reload()
                return {
                    "status": container.status,
                    "running": container.status == "running",
                }
            except (NotFound, APIError):
                return {"status": "not_found", "running": False}

        return await asyncio.to_thread(_status)

    async def get_container_stats(self, container_id: str) -> dict[str, float]:
        def _stats() -> dict[str, float]:
            try:
                container = self.client.containers.get(container_id)
                container.reload()
                
                # Получаем uptime
                uptime_seconds = 0
                started_at = container.attrs.get("State", {}).get("StartedAt")
                if started_at:
                    from dateutil import parser
                    import datetime
                    start_time = parser.parse(started_at)
                    now = datetime.datetime.now(datetime.timezone.utc)
                    uptime_seconds = int((now - start_time).total_seconds())
                
                stats = container.stats(stream=False)

                cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                    stats["precpu_stats"]["cpu_usage"]["total_usage"]
                system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                    stats["precpu_stats"]["system_cpu_usage"]
                num_cpus = stats["cpu_stats"]["online_cpus"]

                cpu_percent = 0.0
                if system_delta > 0 and cpu_delta > 0:
                    cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0

                ram_usage = stats["memory_stats"].get("usage", 0)
                ram_mb = ram_usage / (1024 * 1024)

                disk_usage = 0
                for item in stats.get("blkio_service_bytes", []):
                    if item.get("op") == "Read":
                        disk_usage += item.get("value", 0)
                disk_mb = disk_usage / (1024 * 1024)

                return {
                    "cpu_percent": round(cpu_percent, 2),
                    "ram_mb": round(ram_mb, 2),
                    "disk_mb": round(disk_mb, 2),
                    "uptime_seconds": uptime_seconds,
                }
            except (NotFound, APIError, KeyError) as e:
                logger.error("Failed to get stats for %s: %s", container_id, e)
                return {"cpu_percent": 0.0, "ram_mb": 0.0, "disk_mb": 0.0, "uptime_seconds": 0}

        return await asyncio.to_thread(_stats)

    async def get_container_logs(self, container_id: str, tail: int = 100) -> str:
        """
        Получение логов контейнера с фильтрацией служебных сообщений pip.
        
        Args:
            container_id: ID Docker контейнера
            tail: Количество последних строк для получения
            
        Returns:
            Отфильтрованные логи или сообщение об ошибке
        """
        def _logs() -> str:
            try:
                container = self.client.containers.get(container_id)
                tail = max(1, min(int(tail), 10000))
                logs = container.logs(tail=tail, timestamps=False)
                
                if not logs:
                    logger.warning("No logs returned for container %s", container_id)
                    return "Логи пока отсутствуют"
                
                decoded_logs = logs.decode("utf-8", errors="replace")
                
                # Убираем служебные логи pip
                lines = decoded_logs.split("\n")
                filtered_lines = []
                
                for line in lines:
                    line_stripped = line.strip()
                    if not line_stripped:
                        continue
                    
                    # Пропускаем pip служебные сообщения
                    if any(keyword in line for keyword in [
                        "Collecting", "Downloading", "Installing collected packages",
                        "Requirement already satisfied", "[notice]"
                    ]):
                        continue
                    
                    # Оставляем важные сообщения
                    if "Successfully installed" in line:
                        filtered_lines.append("✅ Зависимости установлены")
                        continue
                    
                    filtered_lines.append(line)
                
                result = "\n".join(filtered_lines).strip()
                if not result:
                    logger.info("All logs filtered out for container %s (only pip messages)", container_id)
                    return "✅ Зависимости установлены\n\nЛоги приложения появятся после запуска"
                
                return result
            except NotFound:
                logger.error("Container not found: %s", container_id)
                return "Контейнер не найден"
            except APIError as e:
                logger.error("Docker API error getting logs for %s: %s", container_id, e)
                return f"Ошибка Docker API: {str(e)}"
            except Exception as e:
                logger.error("Unexpected error getting logs for %s: %s", container_id, e, exc_info=True)
                return f"Неожиданная ошибка: {str(e)}"

        return await asyncio.to_thread(_logs)

    async def test_container(
        self,
        project_files: bytes,
        python_version: str,
        entry_point: str,
        entry_type: str,
    ) -> tuple[bool, str]:
        def _test() -> tuple[bool, str]:
            import tempfile
            import zipfile

            with tempfile.TemporaryDirectory() as tmpdir:
                try:
                    safe_extract_zip(project_files, tmpdir)
                except ArchiveError as exc:
                    return False, str(exc)

                image = PYTHON_IMAGES.get(python_version, PYTHON_IMAGES["3.12"])

                try:
                    entry_point_norm = _validate_entry(entry_point, entry_type)
                except ValueError as exc:
                    return False, str(exc)
                entry_point_quoted = shlex.quote(entry_point_norm)
                entry_dir = entry_point_norm.rsplit("/", 1)[0] if "/" in entry_point_norm else ""

                if entry_type == "module":
                    python_cmd = f"/tmp/venv/bin/python -m {entry_point_quoted}"
                    req_install = (
                        "if [ -f ./requirements.txt ]; then "
                        "/tmp/venv/bin/pip install --no-cache-dir -r ./requirements.txt; "
                        "fi"
                    )
                else:
                    python_cmd = f"/tmp/venv/bin/python {entry_point_quoted}"
                    if entry_dir:
                        req_install = (
                            "if [ -f ./requirements.txt ]; then "
                            "/tmp/venv/bin/pip install --no-cache-dir -r ./requirements.txt; "
                            f"elif [ -f {shlex.quote(f'./{entry_dir}/requirements.txt')} ]; then "
                            f"/tmp/venv/bin/pip install --no-cache-dir -r {shlex.quote(f'./{entry_dir}/requirements.txt')}; "
                            "fi"
                        )
                    else:
                        req_install = (
                            "if [ -f ./requirements.txt ]; then "
                            "/tmp/venv/bin/pip install --no-cache-dir -r ./requirements.txt; "
                            "fi"
                        )

                full_cmd = f"python -m venv /tmp/venv && {req_install} && exec {python_cmd} 2>&1"

                container = None
                try:
                    container = self.client.containers.run(
                        image=image,
                        command=["/bin/sh", "-c", full_cmd],
                        detach=True,
                        working_dir="/app",
                        volumes={tmpdir: {"bind": "/app", "mode": "ro"}},
                        mem_limit="512m",
                        pids_limit=128,
                        security_opt=["no-new-privileges"],
                        remove=False,
                    )

                    result = container.wait(timeout=60)
                    logs = container.logs().decode("utf-8", errors="replace")

                    if result.get("StatusCode", 1) != 0:
                        return False, logs[-2000:]

                    return True, logs[-2000:]
                except Exception as e:
                    return False, str(e)
                finally:
                    if container is not None:
                        try:
                            container.remove(force=True)
                        except Exception:
                            pass

        return await asyncio.to_thread(_test)

    async def get_server_load(self) -> dict[str, float]:
        def _load() -> dict[str, float]:
            try:
                info = self.client.info()
                containers = self.client.containers.list()
                running = len([c for c in containers if c.status == "running"])
                total = len(containers)

                return {
                    "containers_running": running,
                    "containers_total": total,
                }
            except APIError:
                return {"containers_running": 0, "containers_total": 0}

        return await asyncio.to_thread(_load)

    async def list_files(self, container_id: str, path: str = "/app") -> list[str]:
        def _list() -> list[str]:
            try:
                container = self.client.containers.get(container_id)
                # Используем ls -1p чтобы папки отображались со слешем
                exit_code, output = container.exec_run(["ls", "-1p", path])
                logger.info(f"[LIST_FILES] Container: {container_id}, Path: {path}, Exit code: {exit_code}")
                if exit_code != 0:
                    logger.error(f"[LIST_FILES] ls command failed with exit code {exit_code}")
                    return []
                result = output.decode("utf-8", errors="replace").strip().split("\n")
                # Фильтруем пустые строки
                filtered = [f for f in result if f]
                logger.info(f"[LIST_FILES] Found {len(filtered)} items: {filtered[:5]}")  # Первые 5
                return filtered
            except (NotFound, APIError) as e:
                logger.error("Failed to list files in %s: %s", container_id, e)
                return []

        return await asyncio.to_thread(_list)

    async def read_file(self, container_id: str, file_path: str) -> str:
        def _read() -> str:
            try:
                container = self.client.containers.get(container_id)
                exit_code, output = container.exec_run(["cat", file_path])
                if exit_code != 0 or len(output) > 5 * 1024 * 1024:
                    return ""
                return output.decode("utf-8", errors="replace")
            except (NotFound, APIError) as e:
                logger.error("Failed to read file %s: %s", file_path, e)
                return ""

        return await asyncio.to_thread(_read)

    async def write_file(self, container_id: str, file_path: str, content: str) -> bool:
        def _write() -> bool:
            try:
                if not file_path.startswith("/app/"):
                    return False
                container = self.client.containers.get(container_id)
                import tarfile
                import io as _io
                tar_buffer = _io.BytesIO()
                with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
                    data = content.encode("utf-8")
                    info = tarfile.TarInfo(name=posixpath.basename(file_path))
                    info.size = len(data)
                    info.uid = 1000
                    info.gid = 1000
                    info.mode = 0o644
                    tar.addfile(info, _io.BytesIO(data))
                tar_buffer.seek(0)
                container.put_archive(posixpath.dirname(file_path) or "/", tar_buffer)
                return True
            except (NotFound, APIError, OSError) as e:
                logger.error("Failed to write file %s: %s", file_path, e)
                return False

        return await asyncio.to_thread(_write)

    async def delete_file(self, container_id: str, file_path: str) -> bool:
        def _delete() -> bool:
            try:
                if not file_path.startswith("/app/") or file_path == "/app":
                    return False
                container = self.client.containers.get(container_id)
                exit_code, _ = container.exec_run(["rm", "-rf", "--", file_path])
                return exit_code == 0
            except (NotFound, APIError) as e:
                logger.error("Failed to delete file %s: %s", file_path, e)
                return False

        return await asyncio.to_thread(_delete)

    async def create_dir(self, container_id: str, dir_path: str) -> bool:
        def _mkdir() -> bool:
            try:
                if not dir_path.startswith("/app/") or dir_path == "/app":
                    return False
                container = self.client.containers.get(container_id)
                exit_code, _ = container.exec_run(["mkdir", "-p", "--", dir_path])
                return exit_code == 0
            except (NotFound, APIError) as e:
                logger.error("Failed to create dir %s: %s", dir_path, e)
                return False

        return await asyncio.to_thread(_mkdir)

    async def clear_logs(self, container_id: str) -> bool:
        def _clear() -> bool:
            try:
                container = self.client.containers.get(container_id)
                container.restart()
                return True
            except (NotFound, APIError) as e:
                logger.error("Failed to clear logs for %s: %s", container_id, e)
                return False

        return await asyncio.to_thread(_clear)

    async def get_installed_packages(self, container_id: str) -> list[str]:
        """Get list of installed Python packages from container."""
        def _get_packages() -> list[str]:
            try:
                container = self.client.containers.get(container_id)
                # Выполняем pip list --format=freeze в venv
                exit_code, output = container.exec_run(
                    "/tmp/venv/bin/pip list --format=freeze",
                    user="1000:1000"
                )
                if exit_code != 0:
                    logger.warning("pip list failed with code %s", exit_code)
                    return []
                
                decoded = output.decode("utf-8", errors="replace").strip()
                packages = []
                for line in decoded.split("\n"):
                    if not line or line.startswith("#"):
                        continue
                    # Формат: package==version
                    pkg_name = line.split("==")[0].split(">=")[0].split("<=")[0].strip()
                    if pkg_name:
                        packages.append(pkg_name)
                
                return packages
            except (NotFound, APIError) as e:
                logger.error("Failed to get installed packages: %s", e)
                return []

        return await asyncio.to_thread(_get_packages)
