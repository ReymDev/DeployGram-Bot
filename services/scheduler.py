from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from db.engine import async_session_factory
from models.project import Project
from services.project import ProjectService
from services.monitoring import MonitoringService

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self) -> None:
        self._jobs: list = []

    async def collect_metrics(self) -> None:
        async with async_session_factory() as session:
            monitoring = MonitoringService(session)
            await monitoring.collect_all_stats()

    async def check_auto_sleep(self) -> None:
        if settings.AUTO_SLEEP_MINUTES <= 0:
            return
        async with async_session_factory() as session:
            service = ProjectService(session)
            projects = await service.project_repo.get_running_projects()
            for project in projects:
                logger.info("Auto-sleep check for project %d", project.id)

    async def cleanup_inactive_projects(self) -> None:
        async with async_session_factory() as session:
            service = ProjectService(session)
            projects = await service.project_repo.get_all()
            for project in projects:
                if project.user and project.user.tariff == "free":
                    days_inactive = (datetime.utcnow() - project.updated_at).days
                    if days_inactive >= settings.INACTIVE_DELETE_DAYS:
                        logger.info("Deleting inactive project %d", project.id)

    async def auto_backup(self) -> None:
        async with async_session_factory() as session:
            from services.backup import BackupService
            backup_service = BackupService(session)
            result = await session.execute(
                select(Project).where(Project.status == "running")
            )
            for project in result.scalars().all():
                logger.info("Auto-backup for project %d", project.id)
