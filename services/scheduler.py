from __future__ import annotations

import logging
from datetime import datetime, timedelta

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
                threshold = datetime.utcnow() - timedelta(minutes=settings.AUTO_SLEEP_MINUTES)
                if project.updated_at and project.updated_at < threshold:
                    if project.docker_container_id and service.docker:
                        await service.docker.stop_container(project.docker_container_id)
                        await service.project_repo.update(project.id, status="sleeping")
                        logger.info("Project %d put to sleep after %d minutes of inactivity", project.id, settings.AUTO_SLEEP_MINUTES)

    async def cleanup_inactive_projects(self) -> None:
        async with async_session_factory() as session:
            service = ProjectService(session)
            projects = await service.project_repo.get_all()
            for project in projects:
                if project.user and project.user.tariff == "free":
                    if project.updated_at:
                        days_inactive = (datetime.utcnow() - project.updated_at).days
                        if days_inactive >= settings.INACTIVE_DELETE_DAYS:
                            logger.info("Deleting inactive project %d (inactive %d days)", project.id, days_inactive)
                            await service.delete_project(project.id)

    async def auto_backup(self) -> None:
        async with async_session_factory() as session:
            from services.backup import BackupService
            backup_service = BackupService(session)
            result = await session.execute(
                select(Project).where(Project.status == "running")
            )
            for project in result.scalars().all():
                try:
                    await backup_service.create_backup(project.id)
                    logger.info("Auto-backup created for project %d", project.id)
                except Exception as e:
                    logger.error("Failed to auto-backup project %d: %s", project.id, e)
