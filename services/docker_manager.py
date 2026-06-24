from __future__ import annotations

import asyncio
import json
import logging
import os
import shlex
from typing import Any

import docker
from docker.errors import APIError, ImageNotFound, NotFound
from docker.models.containers import Container

logger = logging.getLogger(__name__)

PYTHON_IMAGES = {
    "3.10": "python:3.10-slim",
    "3.11": "python:3.11-slim",
    "3.12": "python:3.12-slim",
}


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

            entry_point_norm = entry_point.replace("\\", "/")
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

            container_name = f"deploygram_{project_id}_{project_name}"

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
                storage_opt=limits.get("storage_opt", {}),
                read_only=False,
                network_disabled=False,
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
                }
            except (NotFound, APIError, KeyError):
                return {"cpu_percent": 0.0, "ram_mb": 0.0, "disk_mb": 0.0}

        return await asyncio.to_thread(_stats)

    async def get_container_logs(self, container_id: str, tail: int = 100) -> str:
        def _logs() -> str:
            try:
                container = self.client.containers.get(container_id)
                # Получаем время запуска контейнера
                container.reload()
                started_at = container.attrs.get("State", {}).get("StartedAt")
                
                # Получаем логи с момента запуска
                if started_at:
                    logs = container.logs(since=started_at, timestamps=False)
                else:
                    logs = container.logs(tail=tail, timestamps=False)
                
                decoded_logs = logs.decode("utf-8", errors="replace")
                
                # Фильтруем логи: убираем установку зависимостей
                lines = decoded_logs.split("\n")
                filtered_lines = []
                skip_pip = False
                
                for line in lines:
                    # Начало установки pip
                    if "Collecting" in line or "Downloading" in line or "Installing collected packages" in line:
                        skip_pip = True
                        continue
                    # Конец установки pip
                    if skip_pip and ("Successfully installed" in line or line.startswith("[")):
                        skip_pip = False
                        if "Successfully installed" in line:
                            continue
                    # Пропускаем строки установки
                    if skip_pip:
                        continue
                    # Пропускаем pip notice
                    if "[notice]" in line.lower() and "pip" in line.lower():
                        continue
                    # Пропускаем "Requirement already satisfied"
                    if "Requirement already satisfied" in line:
                        continue
                    
                    filtered_lines.append(line)
                
                return "\n".join(filtered_lines).strip()
            except (NotFound, APIError) as e:
                logger.error("Failed to get logs for %s: %s", container_id, e)
                return ""

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
                with zipfile.ZipFile(project_files, "r") as zf:
                    zf.extractall(tmpdir)

                image = PYTHON_IMAGES.get(python_version, PYTHON_IMAGES["3.12"])

                entry_point_norm = entry_point.replace("\\", "/")
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

                try:
                    container = self.client.containers.run(
                        image=image,
                        command=["/bin/sh", "-c", full_cmd],
                        detach=True,
                        working_dir="/app",
                        volumes={tmpdir: {"bind": "/app", "mode": "ro"}},
                        remove=True,
                    )

                    result = container.wait(timeout=60)
                    logs = container.logs().decode("utf-8", errors="replace")

                    if result.get("StatusCode", 1) != 0:
                        return False, logs[-2000:]

                    return True, logs[-2000:]
                except Exception as e:
                    return False, str(e)

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
                exit_code, output = container.exec_run(f"ls -1 {path}")
                if exit_code != 0:
                    return []
                return output.decode("utf-8", errors="replace").strip().split("\n")
            except (NotFound, APIError) as e:
                logger.error("Failed to list files in %s: %s", container_id, e)
                return []

        return await asyncio.to_thread(_list)

    async def read_file(self, container_id: str, file_path: str) -> str:
        def _read() -> str:
            try:
                container = self.client.containers.get(container_id)
                exit_code, output = container.exec_run(f"cat {file_path}")
                if exit_code != 0:
                    return ""
                return output.decode("utf-8", errors="replace")
            except (NotFound, APIError) as e:
                logger.error("Failed to read file %s: %s", file_path, e)
                return ""

        return await asyncio.to_thread(_read)

    async def write_file(self, container_id: str, file_path: str, content: str) -> bool:
        def _write() -> bool:
            try:
                container = self.client.containers.get(container_id)
                import tempfile
                with tempfile.NamedTemporaryFile(mode="w", suffix=".tmp", delete=False) as f:
                    f.write(content)
                    tmp_path = f.name
                try:
                    container.put_archive(os.path.dirname(file_path), open(tmp_path, "rb"))
                finally:
                    os.unlink(tmp_path)
                return True
            except (NotFound, APIError) as e:
                logger.error("Failed to write file %s: %s", file_path, e)
                return False

        return await asyncio.to_thread(_write)

    async def delete_file(self, container_id: str, file_path: str) -> bool:
        def _delete() -> bool:
            try:
                container = self.client.containers.get(container_id)
                exit_code, _ = container.exec_run(f"rm -f {file_path}")
                return exit_code == 0
            except (NotFound, APIError) as e:
                logger.error("Failed to delete file %s: %s", file_path, e)
                return False

        return await asyncio.to_thread(_delete)

    async def create_dir(self, container_id: str, dir_path: str) -> bool:
        def _mkdir() -> bool:
            try:
                container = self.client.containers.get(container_id)
                exit_code, _ = container.exec_run(f"mkdir -p {dir_path}")
                return exit_code == 0
            except (NotFound, APIError) as e:
                logger.error("Failed to create dir %s: %s", dir_path, e)
                return False

        return await asyncio.to_thread(_mkdir)

    async def clear_logs(self, container_id: str) -> bool:
        def _clear() -> bool:
            try:
                container = self.client.containers.get(container_id)
                container.stop()
                container.remove(force=True)
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
