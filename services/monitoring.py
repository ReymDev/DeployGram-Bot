from __future__ import annotations

import logging
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from models.project import ProjectStats
from repositories.project import ProjectRepository, ProjectStatsRepository

try:
    from services.docker_manager import DockerManager
    _HAS_DOCKER = True
except ImportError:
    _HAS_DOCKER = False

logger = logging.getLogger(__name__)


class MonitoringService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.project_repo = ProjectRepository(session)
        self.stats_repo = ProjectStatsRepository(session)
        self.docker = DockerManager() if _HAS_DOCKER else None

    async def collect_stats(self, project_id: int) -> ProjectStats | None:
        project = await self.project_repo.get_by_id(project_id)
        if project is None or not project.docker_container_id:
            return None

        stats = await self.docker.get_container_stats(project.docker_container_id)
        return await self.stats_repo.create(
            project_id=project_id,
            cpu_percent=stats.get("cpu_percent", 0),
            ram_mb=stats.get("ram_mb", 0),
            disk_mb=stats.get("disk_mb", 0),
        )

    async def collect_all_stats(self) -> None:
        projects = await self.project_repo.get_running_projects()
        for project in projects:
            try:
                await self.collect_stats(project.id)
            except Exception as e:
                logger.error("Failed to collect stats for project %d: %s", project.id, e)

    async def get_stats_history(
        self, project_id: int, hours: int = 24
    ) -> list[ProjectStats]:
        since = datetime.utcnow() - timedelta(hours=hours)
        from sqlalchemy import select
        result = await self.session.execute(
            select(ProjectStats)
            .where(
                ProjectStats.project_id == project_id,
                ProjectStats.timestamp >= since,
            )
            .order_by(ProjectStats.timestamp.asc())
        )
        return list(result.scalars().all())
