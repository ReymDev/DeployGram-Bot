from __future__ import annotations

import io
import logging
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


class GitHubService:
    async def get_repo_info(self, owner: str, repo: str) -> dict[str, Any] | None:
        url = f"{GITHUB_API}/repos/{owner}/{repo}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None

    async def download_zip(self, owner: str, repo: str, branch: str = "main") -> bytes | None:
        url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.read()
                return None

    async def get_commits(self, owner: str, repo: str, limit: int = 20) -> list[dict[str, Any]]:
        url = f"{GITHUB_API}/repos/{owner}/{repo}/commits?per_page={limit}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                return []

    async def get_commit(self, owner: str, repo: str, sha: str) -> bytes | None:
        url = f"https://github.com/{owner}/{repo}/archive/{sha}.zip"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.read()
                return None

    @staticmethod
    def parse_github_url(url: str) -> tuple[str, str] | None:
        url = url.rstrip("/")
        url = url.replace("https://github.com/", "").replace("http://github.com/", "")
        url = url.replace("git@github.com:", "")
        parts = url.strip("/").split("/")
        if len(parts) >= 2:
            return parts[0], parts[1]
        return None
