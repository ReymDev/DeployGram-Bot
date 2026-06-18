from __future__ import annotations

import logging
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from models.project import Project
from repositories.project import ProjectRepository

try:
    from services.docker_manager import DockerManager
    _HAS_DOCKER = True
except ImportError:
    _HAS_DOCKER = False

logger = logging.getLogger(__name__)


class AutoSleepService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.project_repo = ProjectRepository(session)
        self.docker = DockerManager() if _HAS_DOCKER else None

    async def check_and_sleep(self) -> int:
        if settings.AUTO_SLEEP_MINUTES <= 0:
            return 0

        threshold = datetime.utcnow() - timedelta(minutes=settings.AUTO_SLEEP_MINUTES)
        projects = await self.project_repo.get_running_projects()
        slept = 0

        for project in projects:
            if project.updated_at < threshold:
                if project.docker_container_id:
                    await self.docker.stop_container(project.docker_container_id)
                    await self.project_repo.update(project.id, status="sleeping")
                    slept += 1
                    logger.info("Project %d put to sleep", project.id)

        return slept

    async def wake_up(self, project_id: int) -> tuple[bool, str]:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            return False, "Проект не найден"
        if project.status != "sleeping":
            return False, "Проект не в спящем режиме"
        await self.project_repo.update(project_id, status="stopped")
        return True, "Проект готов к запуску"
