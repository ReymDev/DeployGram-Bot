from __future__ import annotations

import asyncio
import os

import aiohttp


class VPSClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            return {}
        return {"Authorization": f"Bearer {self.api_key}"}

    @staticmethod
    async def _json(response: aiohttp.ClientResponse) -> dict:
        if response.status >= 400:
            return {"error": f"HTTP {response.status}"}
        try:
            return await response.json()
        except Exception:
            return {"error": "invalid response"}

    async def health(self) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(f"{self.base_url}/health") as resp:
                return await self._json(resp)

    async def create_container(self, data: dict) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{self.base_url}/container/create",
                json=data,
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)

    async def start_container(self, container_id: str) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{self.base_url}/container/start",
                json={"container_id": container_id},
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)

    async def stop_container(self, container_id: str) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{self.base_url}/container/stop",
                json={"container_id": container_id},
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)

    async def remove_container(self, container_id: str) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{self.base_url}/container/remove",
                json={"container_id": container_id},
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)

    async def restart_container(self, container_id: str) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{self.base_url}/container/restart",
                json={"container_id": container_id},
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)

    async def get_status(self, container_id: str) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(
                f"{self.base_url}/container/{container_id}/status",
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)

    async def get_stats(self, container_id: str) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(
                f"{self.base_url}/container/{container_id}/stats",
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)

    async def get_logs(self, container_id: str, tail: int = 100) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(
                f"{self.base_url}/container/{container_id}/logs",
                params={"tail": tail},
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)

    async def get_packages(self, container_id: str) -> dict:
        """Список установленных пакетов из контейнера."""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(
                f"{self.base_url}/container/{container_id}/packages",
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)

    async def get_server_stats(self) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(
                f"{self.base_url}/stats",
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)

    async def get_server_info(self) -> dict:
        """Информация о сервере (CPU/RAM/Disk) из агента."""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(
                f"{self.base_url}/server/info",
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)

    async def upload_project(self, project_id: int, files_zip: bytes) -> dict:
        # Increase timeout for file upload
        upload_timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes
        async with aiohttp.ClientSession(timeout=upload_timeout) as session:
            data = aiohttp.FormData()
            data.add_field("file", files_zip, filename="project.zip", content_type="application/zip")
            async with session.post(
                f"{self.base_url}/project/{project_id}/upload",
                data=data,
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)

    async def list_files(self, project_id: int, path: str = "/", container_id: str = "") -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            params = {"path": path}
            if container_id:
                params["container_id"] = container_id
            async with session.get(
                f"{self.base_url}/project/{project_id}/files",
                params=params,
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)

    async def read_file(self, project_id: int, file_path: str, container_id: str = "") -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            params = {"path": file_path}
            if container_id:
                params["container_id"] = container_id
            async with session.get(
                f"{self.base_url}/project/{project_id}/file",
                params=params,
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)

    async def write_file(self, project_id: int, file_path: str, content: str) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{self.base_url}/project/{project_id}/file",
                json={"path": file_path, "content": content},
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)

    async def delete_file(self, project_id: int, file_path: str) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{self.base_url}/project/{project_id}/file/delete",
                json={"path": file_path},
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)

    async def delete_project(self, project_id: int) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{self.base_url}/project/{project_id}/delete",
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)

    async def create_directory(self, project_id: int, dir_path: str) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{self.base_url}/project/{project_id}/file/mkdir",
                json={"path": dir_path},
                headers=self._headers(),
            ) as resp:
                return await self._json(resp)
