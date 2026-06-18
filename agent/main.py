from __future__ import annotations

import asyncio
import logging
import os
import secrets
from typing import Any

import aiohttp
from aiohttp import web

logger = logging.getLogger(__name__)


class VPSAgent:
    def __init__(self, host: str = "0.0.0.0", port: int = 8080, api_key: str = "") -> None:
        self.host = host
        self.port = port
        self.api_key = api_key or secrets.token_hex(32)
        self.app = web.Application()
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.app.router.add_get("/health", self.health)
        self.app.router.add_get("/stats", self.stats)
        self.app.router.add_post("/container/create", self.create_container)
        self.app.router.add_post("/container/start", self.start_container)
        self.app.router.add_post("/container/stop", self.stop_container)
        self.app.router.add_post("/container/remove", self.remove_container)
        self.app.router.add_get("/container/{id}/status", self.container_status)
        self.app.router.add_get("/container/{id}/stats", self.container_stats)
        self.app.router.add_get("/container/{id}/logs", self.container_logs)

    def _check_auth(self, request: web.Request) -> bool:
        auth = request.headers.get("Authorization", "")
        return auth == f"Bearer {self.api_key}"

    async def health(self, request: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    async def stats(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)

        import docker
        client = docker.from_env()
        containers = client.containers.list()
        return web.json_response({
            "containers_running": len([c for c in containers if c.status == "running"]),
            "containers_total": len(containers),
        })

    async def create_container(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)

        data = await request.json()
        import docker
        from services.docker_manager import DockerManager

        dm = DockerManager()
        try:
            container_id = await dm.create_container(
                project_id=data["project_id"],
                project_name=data["project_name"],
                python_version=data.get("python_version", "3.12"),
                entry_point=data.get("entry_point", "main.py"),
                entry_type=data.get("entry_type", "script"),
                tariff=data.get("tariff", "free"),
                env_vars=data.get("env_vars", {}),
            )
            return web.json_response({"container_id": container_id})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def start_container(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)

        data = await request.json()
        from services.docker_manager import DockerManager
        dm = DockerManager()
        success = await dm.start_container(data["container_id"])
        return web.json_response({"success": success})

    async def stop_container(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)

        data = await request.json()
        from services.docker_manager import DockerManager
        dm = DockerManager()
        success = await dm.stop_container(data["container_id"])
        return web.json_response({"success": success})

    async def remove_container(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)

        data = await request.json()
        from services.docker_manager import DockerManager
        dm = DockerManager()
        success = await dm.remove_container(data["container_id"])
        return web.json_response({"success": success})

    async def container_status(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)

        container_id = request.match_info["id"]
        from services.docker_manager import DockerManager
        dm = DockerManager()
        status = await dm.get_container_status(container_id)
        return web.json_response(status)

    async def container_stats(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)

        container_id = request.match_info["id"]
        from services.docker_manager import DockerManager
        dm = DockerManager()
        stats = await dm.get_container_stats(container_id)
        return web.json_response(stats)

    async def container_logs(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)

        container_id = request.match_info["id"]
        tail = int(request.query.get("tail", 100))
        from services.docker_manager import DockerManager
        dm = DockerManager()
        logs = await dm.get_container_logs(container_id, tail)
        return web.json_response({"logs": logs})

    async def run(self) -> None:
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        logger.info("VPS Agent started on %s:%d", self.host, self.port)
        await site.start()
        await asyncio.Event().wait()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    api_key = os.getenv("AGENT_API_KEY", "")
    agent = VPSAgent(api_key=api_key)
    asyncio.run(agent.run())
