from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import docker
from docker.errors import APIError, ImageNotFound, NotFound
from docker.models.containers import Container

from bot.config import settings

logger = logging.getLogger(__name__)

PYTHON_IMAGES = {
    "3.10": "python:3.10-slim",
    "3.11": "python:3.11-slim",
    "3.12": "python:3.12-slim",
}


class DockerManager:
    def __init__(self) -> None:
        self.client = docker.from_env()

    def _get_limits(self, tariff: str) -> dict[str, Any]:
        if tariff == "premium":
            return {
                "cpu_quota": int(settings.PREMIUM_TARIFF_CPU * 100000),
                "mem_limit": f"{settings.PREMIUM_TARIFF_RAM}m",
                "storage_opt": {"size": f"{settings.PREMIUM_TARIFF_DISK}m"},
            }
        return {
            "cpu_quota": int(settings.FREE_TARIFF_CPU * 100000),
            "mem_limit": f"{settings.FREE_TARIFF_RAM}m",
            "storage_opt": {"size": f"{settings.FREE_TARIFF_DISK}m"},
        }

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
    ) -> str:
        def _create() -> str:
            image = PYTHON_IMAGES.get(python_version, PYTHON_IMAGES["3.12"])
            limits = self._get_limits(tariff)

            env_list = [f"{k}={v}" for k, v in (env_vars or {}).items()]

            if entry_type == "module":
                cmd = f"python -m {entry_point}"
            else:
                cmd = f"python {entry_point}"

            container = self.client.containers.run(
                image=image,
                command=["/bin/sh", "-c", f"pip install -r /app/requirements.txt 2>/dev/null; {cmd}"],
                detach=True,
                name=f"deploygram_{project_id}_{project_name}",
                working_dir=work_dir,
                volumes={},
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
                nano_cpus=0,
            )
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
                logs = container.logs(tail=tail, timestamps=False)
                return logs.decode("utf-8", errors="replace")
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
            import os

            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(project_files, "r") as zf:
                    zf.extractall(tmpdir)

                requirements_path = os.path.join(tmpdir, "requirements.txt")
                if not os.path.exists(requirements_path):
                    with open(requirements_path, "w") as f:
                        f.write("")

                image = PYTHON_IMAGES.get(python_version, PYTHON_IMAGES["3.12"])

                if entry_type == "module":
                    cmd = f"python -m {entry_point}"
                else:
                    cmd = f"python {entry_point}"

                full_cmd = f"pip install -r /app/requirements.txt 2>&1; {cmd} 2>&1"

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
