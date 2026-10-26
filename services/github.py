from __future__ import annotations

import logging
import re
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
REPO_PART_RE = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")
MAX_ARCHIVE_SIZE = 100 * 1024 * 1024
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=60)


class GitHubService:
    @staticmethod
    def _validate_repo_part(value: str) -> str:
        value = (value or "").strip()
        if value.endswith(".git"):
            value = value[:-4]
        if not REPO_PART_RE.fullmatch(value):
            raise ValueError("Некорректное имя репозитория GitHub")
        return value

    async def get_repo_info(self, owner: str, repo: str) -> dict[str, Any] | None:
        try:
            owner = self._validate_repo_part(owner)
            repo = self._validate_repo_part(repo)
        except ValueError:
            return None

        url = f"{GITHUB_API}/repos/{owner}/{repo}"
        async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None

    async def download_zip(
        self, owner: str, repo: str, branch: str | None = None
    ) -> bytes | None:
        try:
            owner = self._validate_repo_part(owner)
            repo = self._validate_repo_part(repo)
        except ValueError:
            return None

        branches = [branch] if branch else ["main", "master"]
        for candidate in branches:
            if not candidate or not REPO_PART_RE.fullmatch(candidate):
                continue
            url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{candidate}.zip"
            async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT) as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        continue
                    content_length = int(resp.headers.get("Content-Length", "0") or 0)
                    if content_length > MAX_ARCHIVE_SIZE:
                        logger.warning("GitHub archive too large: %s bytes", content_length)
                        return None
                    data = await resp.read()
                    if len(data) > MAX_ARCHIVE_SIZE:
                        logger.warning("GitHub archive too large after download")
                        return None
                    return data
        return None

    async def get_commits(self, owner: str, repo: str, limit: int = 20) -> list[dict[str, Any]]:
        try:
            owner = self._validate_repo_part(owner)
            repo = self._validate_repo_part(repo)
        except ValueError:
            return []
        limit = max(1, min(int(limit), 100))

        url = f"{GITHUB_API}/repos/{owner}/{repo}/commits?per_page={limit}"
        async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                return []

    async def get_commit(self, owner: str, repo: str, sha: str | None) -> bytes | None:
        try:
            owner = self._validate_repo_part(owner)
            repo = self._validate_repo_part(repo)
        except ValueError:
            return None
        if not sha or not re.fullmatch(r"[A-Fa-f0-9]{7,40}", sha):
            return None

        url = f"https://github.com/{owner}/{repo}/archive/{sha}.zip"
        async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                content_length = int(resp.headers.get("Content-Length", "0") or 0)
                if content_length > MAX_ARCHIVE_SIZE:
                    return None
                data = await resp.read()
                return data if len(data) <= MAX_ARCHIVE_SIZE else None

    @staticmethod
    def parse_github_url(url: str) -> tuple[str, str] | None:
        raw = (url or "").strip().rstrip("/")
        for prefix in (
            "https://github.com/",
            "http://github.com/",
            "git@github.com:",
            "github.com/",
        ):
            if raw.startswith(prefix):
                raw = raw[len(prefix):]
                break

        parts = raw.strip("/").split("/")
        if len(parts) < 2:
            return None

        owner, repo = parts[0], parts[1]
        if repo.endswith(".git"):
            repo = repo[:-4]
        if not REPO_PART_RE.fullmatch(owner) or not REPO_PART_RE.fullmatch(repo):
            return None
        return owner, repo
