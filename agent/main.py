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
        self.api_key = api_key
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
        self.app.router.add_post("/project/{id}/upload", self.upload_project)
        self.app.router.add_get("/project/{id}/files", self.list_files)
        self.app.router.add_get("/project/{id}/file", self.read_file)
        self.app.router.add_post("/project/{id}/file", self.write_file)
        self.app.router.add_post("/project/{id}/file/delete", self.delete_file)

    def _check_auth(self, request: web.Request) -> bool:
        if not self.api_key:
            return True
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

        try:
            data = await request.json()
            import docker
            from services.docker_manager import DockerManager

            project_id = data["project_id"]
            project_dir = f"/data/projects/{project_id}"

            dm = DockerManager()
            container_id = await dm.create_container(
                project_id=project_id,
                project_name=data["project_name"],
                python_version=data.get("python_version", "3.12"),
                entry_point=data.get("entry_point", "main.py"),
                entry_type=data.get("entry_type", "script"),
                tariff=data.get("tariff", "free"),
                env_vars=data.get("env_vars", {}),
                project_dir=project_dir,
            )
            return web.json_response({"container_id": container_id})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def start_container(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)
        try:
            data = await request.json()
            from services.docker_manager import DockerManager
            dm = DockerManager()
            success = await dm.start_container(data["container_id"])
            return web.json_response({"success": success})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def stop_container(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)
        try:
            data = await request.json()
            from services.docker_manager import DockerManager
            dm = DockerManager()
            success = await dm.stop_container(data["container_id"])
            return web.json_response({"success": success})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def remove_container(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)
        try:
            data = await request.json()
            from services.docker_manager import DockerManager
            dm = DockerManager()
            success = await dm.remove_container(data["container_id"])
            return web.json_response({"success": success})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def container_status(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)
        try:
            container_id = request.match_info["id"]
            from services.docker_manager import DockerManager
            dm = DockerManager()
            status = await dm.get_container_status(container_id)
            return web.json_response(status)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def container_stats(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)
        try:
            container_id = request.match_info["id"]
            from services.docker_manager import DockerManager
            dm = DockerManager()
            stats = await dm.get_container_stats(container_id)
            return web.json_response(stats)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def container_logs(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)
        try:
            container_id = request.match_info["id"]
            tail = int(request.query.get("tail", 100))
            from services.docker_manager import DockerManager
            dm = DockerManager()
            logs = await dm.get_container_logs(container_id, tail)
            return web.json_response({"logs": logs})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def run(self) -> None:
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        logger.info("VPS Agent started on %s:%d", self.host, self.port)
        await site.start()
        await asyncio.Event().wait()

    def _get_project_dir(self, project_id: str) -> str:
        project_dir = f"/data/projects/{project_id}"
        os.makedirs(project_dir, exist_ok=True)
        return project_dir

    async def upload_project(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)
        try:
            project_id = request.match_info["id"]
            project_dir = self._get_project_dir(project_id)

            reader = await request.multipart()
            while True:
                part = await reader.next()
                if part is None:
                    break
                if part.name == "file":
                    filename = part.filename or "archive.zip"
                    filepath = os.path.join(project_dir, filename)
                    with open(filepath, "wb") as f:
                        while True:
                            chunk = await part.read_chunk()
                            if not chunk:
                                break
                            f.write(chunk)

                    import zipfile
                    with zipfile.ZipFile(filepath, "r") as zf:
                        zf.extractall(project_dir)
                    os.remove(filepath)

            return web.json_response({"status": "ok", "project_dir": project_dir})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def list_files(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)
        try:
            project_id = request.match_info["id"]
            project_dir = self._get_project_dir(project_id)
            path = request.query.get("path", "/")

            full_path = os.path.join(project_dir, path.lstrip("/"))
            if not os.path.exists(full_path):
                return web.json_response({"files": []})

            files = []
            for name in os.listdir(full_path):
                files.append(name)
            return web.json_response({"files": files})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def read_file(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)
        try:
            project_id = request.match_info["id"]
            project_dir = self._get_project_dir(project_id)
            file_path = request.query.get("path", "")

            full_path = os.path.join(project_dir, file_path.lstrip("/"))
            if not os.path.exists(full_path):
                return web.json_response({"error": "file not found"}, status=404)

            with open(full_path, "r", errors="replace") as f:
                content = f.read()
            return web.json_response({"content": content})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def write_file(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)
        try:
            project_id = request.match_info["id"]
            project_dir = self._get_project_dir(project_id)
            data = await request.json()
            file_path = data.get("path", "")
            content = data.get("content", "")

            full_path = os.path.join(project_dir, file_path.lstrip("/"))
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)
            return web.json_response({"status": "ok"})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def delete_file(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return web.json_response({"error": "unauthorized"}, status=401)
        try:
            project_id = request.match_info["id"]
            project_dir = self._get_project_dir(project_id)
            data = await request.json()
            file_path = data.get("path", "")

            full_path = os.path.join(project_dir, file_path.lstrip("/"))
            if os.path.exists(full_path):
                if os.path.isdir(full_path):
                    import shutil
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)
            return web.json_response({"status": "ok"})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    api_key = os.getenv("AGENT_API_KEY", "")
    agent = VPSAgent(api_key=api_key)
    asyncio.run(agent.run())
