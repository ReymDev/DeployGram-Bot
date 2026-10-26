from __future__ import annotations

import asyncio
import hmac
import logging
import os
import posixpath
import re
import shutil
import stat
import time
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from aiohttp import web

logger = logging.getLogger(__name__)

PROJECT_ID_RE = re.compile(r"^[0-9]{1,20}$")
CONTAINER_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
MAX_UPLOAD_SIZE = 100 * 1024 * 1024
MAX_UNCOMPRESSED_SIZE = 500 * 1024 * 1024
MAX_FILES = 20_000
MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_READ_SIZE = 1024 * 1024


class ArchiveError(ValueError):
    pass


class VPSAgent:
    def __init__(self, host: str = "0.0.0.0", port: int = 8080, api_key: str = "") -> None:
        self.host = host
        self.port = port
        self.api_key = api_key
        self.start_time = time.time()
        self.internal_data_dir = os.getenv("AGENT_DATA_DIR", "/app/data/projects")
        self.host_data_dir = os.getenv(
            "AGENT_HOST_DATA_DIR", "/var/lib/deploygram/data/projects"
        )
        self.app = web.Application(client_max_size=MAX_UPLOAD_SIZE + 1024 * 1024)
        from services.docker_manager import DockerManager

        self.docker = DockerManager()
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.app.router.add_get("/health", self.health)
        self.app.router.add_get("/stats", self.stats)
        self.app.router.add_get("/server/info", self.server_info)
        self.app.router.add_get("/server/containers", self.server_containers)
        self.app.router.add_post("/container/create", self.create_container)
        self.app.router.add_post("/container/start", self.start_container)
        self.app.router.add_post("/container/stop", self.stop_container)
        self.app.router.add_post("/container/restart", self.restart_container)
        self.app.router.add_post("/container/remove", self.remove_container)
        self.app.router.add_get("/container/{id}/status", self.container_status)
        self.app.router.add_get("/container/{id}/stats", self.container_stats)
        self.app.router.add_get("/container/{id}/logs", self.container_logs)
        self.app.router.add_get("/container/{id}/packages", self.container_packages)
        self.app.router.add_post("/project/{id}/upload", self.upload_project)
        self.app.router.add_get("/project/{id}/files", self.list_files)
        self.app.router.add_get("/project/{id}/file", self.read_file)
        self.app.router.add_post("/project/{id}/file", self.write_file)
        self.app.router.add_post("/project/{id}/file/delete", self.delete_file)
        self.app.router.add_post("/project/{id}/delete", self.delete_project)
        self.app.router.add_post("/project/{id}/file/mkdir", self.create_directory)

    def _check_auth(self, request: web.Request) -> bool:
        if not self.api_key:
            # Без ключа разрешаем только локальные запросы.
            return request.remote in ("127.0.0.1", "::1")
        auth = request.headers.get("Authorization", "")
        return hmac.compare_digest(auth, f"Bearer {self.api_key}")

    @staticmethod
    def _validate_project_id(project_id: str) -> bool:
        return bool(PROJECT_ID_RE.fullmatch(project_id or ""))

    @staticmethod
    def _validate_container_id(container_id: str) -> bool:
        return bool(CONTAINER_ID_RE.fullmatch(container_id or ""))

    @staticmethod
    def _safe_container_path(user_path: str) -> str | None:
        raw = (user_path or "/app").replace("\\", "/").strip()
        if raw == "/app":
            relative = ""
        elif raw.startswith("/app/"):
            relative = raw[len("/app/"):]
        else:
            return None
        parts = [part for part in relative.split("/") if part not in ("", ".")]
        if any(part == ".." for part in parts):
            return None
        normalized = "/".join(parts)
        return "/app" if not normalized else f"/app/{normalized}"

    @staticmethod
    def _safe_project_path(base: str, user_path: str, allow_base: bool = False) -> str | None:
        raw = (user_path or "").replace("\\", "/").strip()
        if "\x00" in raw or "\n" in raw or "\r" in raw:
            return None
        if raw == "/app":
            relative = ""
        elif raw.startswith("/app/"):
            relative = raw[len("/app/"):]
        elif raw.startswith("/"):
            return None
        else:
            relative = raw

        parts = [part for part in relative.split("/") if part not in ("", ".")]
        if any(part == ".." or ":" in part for part in parts):
            return None

        base_real = os.path.realpath(base)
        full = os.path.realpath(os.path.join(base_real, *parts)) if parts else base_real
        try:
            if os.path.commonpath([base_real, full]) != base_real:
                return None
        except ValueError:
            return None
        if not allow_base and full == base_real:
            return None
        return full

    @staticmethod
    def _safe_extract(archive_path: str, destination: str) -> None:
        dest = os.path.realpath(destination)
        os.makedirs(dest, exist_ok=True)
        with zipfile.ZipFile(archive_path, "r") as zf:
            infos = zf.infolist()
            if len(infos) > MAX_FILES:
                raise ArchiveError("too many files in archive")

            total = 0
            validated: list[tuple[zipfile.ZipInfo, str]] = []
            for info in infos:
                name = (info.filename or "").replace("\\", "/")
                if not name or name.startswith("/") or any(ord(ch) < 32 for ch in name):
                    raise ArchiveError("unsafe archive path")
                pure = PurePosixPath(name)
                if pure.is_absolute() or any(part in ("..", "") for part in pure.parts):
                    raise ArchiveError("unsafe archive path")
                if any(":" in part for part in pure.parts):
                    raise ArchiveError("unsafe archive path")
                mode = info.external_attr >> 16
                if stat.S_ISLNK(mode):
                    raise ArchiveError("symlinks are not allowed")
                total += info.file_size
                if info.file_size > MAX_UNCOMPRESSED_SIZE or total > MAX_UNCOMPRESSED_SIZE:
                    raise ArchiveError("archive is too large after extraction")
                target = os.path.realpath(os.path.join(dest, *pure.parts))
                try:
                    if os.path.commonpath([dest, target]) != dest:
                        raise ArchiveError("unsafe archive path")
                except ValueError as exc:
                    raise ArchiveError("unsafe archive path") from exc
                validated.append((info, target))

            for info, target in validated:
                if info.is_dir():
                    os.makedirs(target, exist_ok=True)
                    continue
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with zf.open(info, "r") as src, open(target, "wb") as out:
                    while True:
                        chunk = src.read(1024 * 1024)
                        if not chunk:
                            break
                        out.write(chunk)

    async def _get_container(self, request: web.Request, container_id: str):
        if not self._validate_container_id(container_id):
            return None
        try:
            container = await asyncio.to_thread(
                self.docker.client.containers.get, container_id
            )
        except Exception:
            return None
        labels = container.labels or {}
        if labels.get("deploygram") != "true" and not container.name.startswith("deploygram_"):
            return None
        return container

    def _json_error(self, message: str, status: int = 400) -> web.Response:
        return web.json_response({"error": message}, status=status)

    async def health(self, request: web.Request) -> web.Response:
        try:
            await asyncio.to_thread(self.docker.client.ping)
            docker_ok = True
        except Exception:
            docker_ok = False
        return web.json_response({
            "status": "ok",
            "docker": docker_ok,
            "uptime": int(time.time() - self.start_time),
            "version": "1.0.0",
        })

    async def stats(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)
        try:
            containers = await asyncio.to_thread(self.docker.client.containers.list)
            running = [c for c in containers if c.status == "running"]
            deploygram = [c for c in containers if (c.labels or {}).get("deploygram") == "true"]
            return web.json_response({
                "containers_running": len(running),
                "containers_total": len(containers),
                "deploygram_containers": len(deploygram),
                "deploygram_running": len([c for c in deploygram if c.status == "running"]),
            })
        except Exception as e:
            logger.error("Failed to get stats: %s", e)
            return self._json_error("internal error", 500)

    async def server_info(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            return web.json_response({
                "cpu_percent": cpu_percent,
                "ram_total_mb": round(mem.total / (1024 * 1024)),
                "ram_used_mb": round(mem.used / (1024 * 1024)),
                "ram_percent": mem.percent,
                "disk_total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
                "disk_used_gb": round(disk.used / (1024 * 1024 * 1024), 2),
                "disk_percent": disk.percent,
                "uptime": int(time.time() - self.start_time),
            })
        except ImportError:
            return self._json_error("psutil not installed", 500)
        except Exception as e:
            logger.error("Failed to get server info: %s", e)
            return self._json_error("internal error", 500)

    async def server_containers(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)
        try:
            containers = await asyncio.to_thread(
                self.docker.client.containers.list, all=True
            )
            result = []
            for c in containers:
                labels = c.labels or {}
                result.append({
                    "id": c.id[:12],
                    "name": c.name,
                    "status": c.status,
                    "image": c.image.tags[0] if c.image.tags else "unknown",
                    "deploygram": labels.get("deploygram") == "true",
                    "project_id": labels.get("project_id"),
                })
            return web.json_response({"containers": result})
        except Exception as e:
            logger.error("Failed to list containers: %s", e)
            return self._json_error("internal error", 500)

    async def create_container(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)
        try:
            data = await request.json()
            project_id = str(data["project_id"])
            if not self._validate_project_id(project_id):
                return self._json_error("invalid project id")
            project_dir = self._get_project_dir(project_id)
            host_project_dir = self._get_host_project_dir(project_id)

            logger.info(
                "Creating container for project %s: entry_point=%s, entry_type=%s",
                project_id,
                data.get("entry_point", "main.py"),
                data.get("entry_type", "script"),
            )

            container_id = await self.docker.create_container(
                project_id=int(project_id),
                project_name=str(data["project_name"]),
                python_version=str(data.get("python_version", "3.12")),
                entry_point=str(data.get("entry_point", "main.py")),
                entry_type=str(data.get("entry_type", "script")),
                tariff=str(data.get("tariff", "free")),
                env_vars=data.get("env_vars") if isinstance(data.get("env_vars"), dict) else {},
                project_dir=(host_project_dir if os.path.isdir(project_dir) else None),
            )
            return web.json_response({"container_id": container_id})
        except (KeyError, TypeError, ValueError) as e:
            logger.warning("Invalid create request: %s", e)
            return self._json_error("invalid request", 400)
        except Exception as e:
            logger.error("Failed to create container: %s", e)
            return self._json_error("container creation failed", 500)

    async def start_container(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)
        try:
            data = await request.json()
            container_id = str(data["container_id"])
            if await self._get_container(request, container_id) is None:
                return self._json_error("container not found", 404)
            success = await self.docker.start_container(container_id)
            return web.json_response({"success": success})
        except Exception as e:
            logger.error("Failed to start container: %s", e)
            return self._json_error("internal error", 500)

    async def stop_container(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)
        try:
            data = await request.json()
            container_id = str(data["container_id"])
            if await self._get_container(request, container_id) is None:
                return self._json_error("container not found", 404)
            success = await self.docker.stop_container(container_id)
            return web.json_response({"success": success})
        except Exception as e:
            logger.error("Failed to stop container: %s", e)
            return self._json_error("internal error", 500)

    async def restart_container(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)
        try:
            data = await request.json()
            container_id = str(data["container_id"])
            if await self._get_container(request, container_id) is None:
                return self._json_error("container not found", 404)
            success = await self.docker.restart_container(container_id)
            return web.json_response({"success": success})
        except Exception as e:
            logger.error("Failed to restart container: %s", e)
            return self._json_error("internal error", 500)

    async def remove_container(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)
        try:
            data = await request.json()
            container_id = str(data["container_id"])
            if await self._get_container(request, container_id) is None:
                return self._json_error("container not found", 404)
            success = await self.docker.remove_container(container_id)
            return web.json_response({"success": success})
        except Exception as e:
            logger.error("Failed to remove container: %s", e)
            return self._json_error("internal error", 500)

    async def container_status(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)
        container_id = request.match_info["id"]
        if await self._get_container(request, container_id) is None:
            return self._json_error("container not found", 404)
        try:
            status = await self.docker.get_container_status(container_id)
            return web.json_response(status)
        except Exception as e:
            logger.error("Failed to get container status: %s", e)
            return self._json_error("internal error", 500)

    async def container_stats(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)
        container_id = request.match_info["id"]
        if await self._get_container(request, container_id) is None:
            return self._json_error("container not found", 404)
        try:
            stats = await self.docker.get_container_stats(container_id)
            return web.json_response(stats)
        except Exception as e:
            logger.error("Failed to get container stats: %s", e)
            return self._json_error("internal error", 500)

    async def container_logs(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)
        container_id = request.match_info["id"]
        if await self._get_container(request, container_id) is None:
            return self._json_error("container not found", 404)
        try:
            tail = max(1, min(int(request.query.get("tail", 100)), 10000))
            logs = await self.docker.get_container_logs(container_id, tail)
            return web.json_response({"logs": logs})
        except Exception as e:
            logger.error("Failed to get container logs: %s", e)
            return self._json_error("internal error", 500)

    async def container_packages(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)
        container_id = request.match_info["id"]
        if await self._get_container(request, container_id) is None:
            return self._json_error("container not found", 404)
        try:
            packages = await self.docker.get_installed_packages(container_id)
            return web.json_response({"packages": packages})
        except Exception as e:
            logger.error("Failed to get container packages: %s", e)
            return self._json_error("internal error", 500)

    async def upload_project(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)

        project_id = request.match_info["id"]
        if not self._validate_project_id(project_id):
            return self._json_error("invalid project id")

        project_dir = self._get_project_dir(project_id)
        archive_path = os.path.join(project_dir, f".upload-{time.time_ns()}.zip")
        total_size = 0
        swapped = False

        try:
            reader = await request.multipart()
            uploaded = False
            while True:
                part = await reader.next()
                if part is None:
                    break
                if part.name != "file":
                    await part.release()
                    continue
                if uploaded:
                    return self._json_error("only one archive is allowed")
                filename = os.path.basename(part.filename or "archive.zip")
                if not filename.lower().endswith(".zip"):
                    return self._json_error("only .zip archives are allowed")
                with open(archive_path, "wb") as f:
                    while True:
                        chunk = await part.read_chunk()
                        if not chunk:
                            break
                        total_size += len(chunk)
                        if total_size > MAX_UPLOAD_SIZE:
                            return self._json_error("archive is too large", 413)
                        f.write(chunk)
                uploaded = True

            if not uploaded:
                return self._json_error("archive is missing")

            tmp_dir = f"{project_dir}.upload-{time.time_ns()}"
            try:
                self._safe_extract(archive_path, tmp_dir)
                for child in os.listdir(project_dir):
                    child_path = os.path.join(project_dir, child)
                    if os.path.isdir(child_path) and not os.path.islink(child_path):
                        shutil.rmtree(child_path)
                    else:
                        os.remove(child_path)
                for child in os.listdir(tmp_dir):
                    shutil.move(os.path.join(tmp_dir, child), os.path.join(project_dir, child))
                swapped = True
            finally:
                shutil.rmtree(tmp_dir, ignore_errors=True)
            self._chown_project(project_dir)

            files_list = []
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), project_dir)
                    files_list.append(rel_path)
            return web.json_response({
                "status": "ok",
                "project_dir": project_dir,
                "files": files_list[:20],
            })
        except ArchiveError as e:
            logger.warning("Rejected archive for project %s: %s", project_id, e)
            return self._json_error("unsafe archive", 400)
        except Exception as e:
            logger.error("Failed to upload project %s: %s", project_id, e)
            return self._json_error("upload failed", 500)
        finally:
            if not swapped:
                try:
                    os.remove(archive_path)
                except OSError:
                    pass

    async def list_files(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)

        project_id = request.match_info["id"]
        if not self._validate_project_id(project_id):
            return self._json_error("invalid project id")

        path = self._safe_container_path(request.query.get("path", "/app"))
        if path is None:
            return self._json_error("path traversal detected")

        container_id = request.query.get("container_id")
        if container_id:
            if await self._get_container(request, container_id) is None:
                return self._json_error("container not found", 404)
        else:
            containers = await asyncio.to_thread(
                self.docker.client.containers.list,
                filters={"name": f"deploygram_{project_id}_"},
            )
            if not containers:
                return web.json_response({"files": []})
            container_id = containers[0].id

        try:
            files = await self.docker.list_files(container_id, path)
            return web.json_response({"files": files})
        except Exception as e:
            logger.error("Failed to list files: %s", e)
            return self._json_error("internal error", 500)

    async def read_file(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)

        project_id = request.match_info["id"]
        if not self._validate_project_id(project_id):
            return self._json_error("invalid project id")

        file_path = self._safe_container_path(request.query.get("path", ""))
        if file_path is None or file_path == "/app":
            return self._json_error("path traversal detected")

        container_id = request.query.get("container_id")
        if container_id:
            if await self._get_container(request, container_id) is None:
                return self._json_error("container not found", 404)
        else:
            containers = await asyncio.to_thread(
                self.docker.client.containers.list,
                filters={"name": f"deploygram_{project_id}_"},
            )
            if not containers:
                return self._json_error("container not found", 404)
            container_id = containers[0].id

        try:
            content = await self.docker.read_file(container_id, file_path)
            if not content:
                return web.json_response({"error": "file not found"}, status=404)
            if len(content.encode("utf-8", errors="replace")) > MAX_READ_SIZE:
                return self._json_error("file too large", 413)
            return web.json_response({"content": content, "size": len(content)})
        except Exception as e:
            logger.error("Failed to read file: %s", e)
            return self._json_error("internal error", 500)

    async def write_file(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)

        project_id = request.match_info["id"]
        if not self._validate_project_id(project_id):
            return self._json_error("invalid project id")

        project_dir = self._get_project_dir(project_id)
        try:
            data = await request.json()
        except Exception:
            return self._json_error("invalid request")

        if not isinstance(data, dict):
            return self._json_error("invalid request")
        file_path = data.get("path", "")
        content = data.get("content", "")
        if not isinstance(content, str):
            return self._json_error("content must be a string")
        if len(content.encode("utf-8")) > MAX_FILE_SIZE:
            return self._json_error("file too large", 413)

        full_path = self._safe_project_path(project_dir, file_path)
        if full_path is None:
            return self._json_error("path traversal detected")

        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            self._chown_project(project_dir)
            return web.json_response({"status": "ok", "size": len(content)})
        except Exception as e:
            logger.error("Failed to write file: %s", e)
            return self._json_error("internal error", 500)

    async def delete_file(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)

        project_id = request.match_info["id"]
        if not self._validate_project_id(project_id):
            return self._json_error("invalid project id")

        project_dir = self._get_project_dir(project_id)
        try:
            data = await request.json()
        except Exception:
            return self._json_error("invalid request")

        if not isinstance(data, dict):
            return self._json_error("invalid request")
        full_path = self._safe_project_path(project_dir, data.get("path", ""))
        if full_path is None:
            return self._json_error("path traversal detected")

        try:
            if os.path.isdir(full_path) and not os.path.islink(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)
            return web.json_response({"status": "ok"})
        except FileNotFoundError:
            return web.json_response({"status": "ok"})
        except Exception as e:
            logger.error("Failed to delete file: %s", e)
            return self._json_error("internal error", 500)

    async def create_directory(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)

        project_id = request.match_info["id"]
        if not self._validate_project_id(project_id):
            return self._json_error("invalid project id")

        project_dir = self._get_project_dir(project_id)
        try:
            data = await request.json()
        except Exception:
            return self._json_error("invalid request")

        if not isinstance(data, dict):
            return self._json_error("invalid request")
        full_path = self._safe_project_path(
            project_dir, data.get("path", ""), allow_base=True
        )
        if full_path is None:
            return self._json_error("path traversal detected")

        try:
            os.makedirs(full_path, exist_ok=True)
            self._chown_project(project_dir)
            return web.json_response({"status": "ok"})
        except Exception as e:
            logger.error("Failed to create directory: %s", e)
            return self._json_error("internal error", 500)

    async def delete_project(self, request: web.Request) -> web.Response:
        if not self._check_auth(request):
            return self._json_error("unauthorized", 401)
        project_id = request.match_info["id"]
        if not self._validate_project_id(project_id):
            return self._json_error("invalid project id")
        try:
            project_dir = self._get_project_dir(project_id)
            shutil.rmtree(project_dir, ignore_errors=True)
            return web.json_response({"status": "ok"})
        except Exception as e:
            logger.error("Failed to delete project %s: %s", project_id, e)
            return self._json_error("internal error", 500)

    async def run(self) -> None:
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        logger.info("VPS Agent started on %s:%d", self.host, self.port)
        if not self.api_key:
            logger.warning(
                "AGENT_API_KEY is not set: only loopback requests are allowed"
            )
        await site.start()
        await asyncio.Event().wait()

    def _get_project_dir(self, project_id: str) -> str:
        if not self._validate_project_id(project_id):
            raise ValueError("invalid project_id")
        path = os.path.join(self.internal_data_dir, project_id)
        os.makedirs(path, exist_ok=True)
        self._chown_project(path)
        return os.path.realpath(path)

    def _get_host_project_dir(self, project_id: str) -> str:
        if not self._validate_project_id(project_id):
            raise ValueError("invalid project_id")
        return os.path.join(self.host_data_dir, project_id)

    def _chown_project(self, path: str) -> None:
        try:
            if not hasattr(os, "geteuid") or os.geteuid() != 0:
                return
            os.chown(path, 1000, 1000)
            for root, dirs, files in os.walk(path):
                for name in dirs + files:
                    try:
                        os.chown(os.path.join(root, name), 1000, 1000)
                    except OSError:
                        pass
        except OSError as e:
            logger.warning("Failed to chown project directory: %s", e)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    api_key = os.getenv("AGENT_API_KEY", "")
    port = int(os.getenv("AGENT_PORT", "8080"))
    host = os.getenv("AGENT_HOST", "0.0.0.0")
    if not api_key and host not in ("127.0.0.1", "::1"):
        logger.warning("AGENT_API_KEY is empty: remote access will be denied")
    agent = VPSAgent(host=host, port=port, api_key=api_key)
    asyncio.run(agent.run())
