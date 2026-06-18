from __future__ import annotations

import asyncio
import os

import aiohttp


class VPSClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    async def health(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/health") as resp:
                return await resp.json()

    async def create_container(self, data: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/container/create",
                json=data,
                headers=self._headers(),
            ) as resp:
                return await resp.json()

    async def start_container(self, container_id: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/container/start",
                json={"container_id": container_id},
                headers=self._headers(),
            ) as resp:
                return await resp.json()

    async def stop_container(self, container_id: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/container/stop",
                json={"container_id": container_id},
                headers=self._headers(),
            ) as resp:
                return await resp.json()

    async def remove_container(self, container_id: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/container/remove",
                json={"container_id": container_id},
                headers=self._headers(),
            ) as resp:
                return await resp.json()

    async def get_status(self, container_id: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/container/{container_id}/status",
                headers=self._headers(),
            ) as resp:
                return await resp.json()

    async def get_stats(self, container_id: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/container/{container_id}/stats",
                headers=self._headers(),
            ) as resp:
                return await resp.json()

    async def get_logs(self, container_id: str, tail: int = 100) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/container/{container_id}/logs",
                params={"tail": tail},
                headers=self._headers(),
            ) as resp:
                return await resp.json()

    async def get_server_stats(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/stats",
                headers=self._headers(),
            ) as resp:
                return await resp.json()
