from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

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
        self._notified_high_cpu: set[int] = set()
        self._notified_high_ram: set[int] = set()

    async def collect_metrics(self) -> None:
        async with async_session_factory() as session:
            monitoring = MonitoringService(session)
            await monitoring.collect_all_stats()

    async def check_resource_alerts(self) -> None:
        """Check for high resource usage and send notifications."""
        try:
            from aiogram import Bot
            from bot.config import settings as bot_settings
            from services.notifications import NotificationService
            from repositories.user import UserRepository
            
            bot = Bot(token=bot_settings.BOT_TOKEN)
            notification_service = NotificationService(bot)
            
            async with async_session_factory() as session:
                monitoring = MonitoringService(session)
                user_repo = UserRepository(session)
                
                # Get all running projects
                projects = await monitoring.project_repo.get_running_projects()
                
                for project in projects:
                    try:
                        # Get latest stats
                        stats_history = await monitoring.get_stats_history(project.id, hours=1)
                        if not stats_history:
                            continue
                        
                        latest_stats = stats_history[-1]
                        
                        # Get user
                        user = await user_repo.get_by_id(project.user_id)
                        if not user or not user.settings:
                            continue
                        
                        # Check CPU threshold (80%)
                        if latest_stats.cpu_percent > 80:
                            if project.id not in self._notified_high_cpu:
                                if user.settings.notify_high_cpu:
                                    await notification_service.notify_high_cpu(
                                        user, project.name, latest_stats.cpu_percent
                                    )
                                self._notified_high_cpu.add(project.id)
                        else:
                            # Reset notification flag when CPU is back to normal
                            self._notified_high_cpu.discard(project.id)
                        
                        # Check RAM threshold (80% of 512MB = ~400MB)
                        if latest_stats.ram_mb > 400:
                            if project.id not in self._notified_high_ram:
                                if user.settings.notify_high_ram:
                                    await notification_service.notify_high_ram(
                                        user, project.name, latest_stats.ram_mb
                                    )
                                self._notified_high_ram.add(project.id)
                        else:
                            # Reset notification flag when RAM is back to normal
                            self._notified_high_ram.discard(project.id)
                    
                    except Exception as e:
                        logger.error("Failed to check alerts for project %d: %s", project.id, e)
            
            await bot.session.close()
        
        except Exception as e:
            logger.error("Failed to check resource alerts: %s", e)

    async def check_auto_sleep(self) -> None:
        if settings.AUTO_SLEEP_MINUTES <= 0:
            return
        async with async_session_factory() as session:
            service = ProjectService(session)
            projects = await service.project_repo.get_running_projects()
            for project in projects:
                threshold = datetime.now(timezone.utc) - timedelta(minutes=settings.AUTO_SLEEP_MINUTES)
                if project.updated_at and project.updated_at < threshold:
                    if project.docker_container_id and service.docker:
                        await service.docker.stop_container(project.docker_container_id)
                        await service.project_repo.update(project.id, status="sleeping")
                        logger.info("Project %d put to sleep after %d minutes of inactivity", project.id, settings.AUTO_SLEEP_MINUTES)

    async def cleanup_inactive_projects(self) -> None:
        async with async_session_factory() as session:
            service = ProjectService(session)
            projects = await service.project_repo.get_all(limit=None)
            for project in projects:
                if project.user and project.user.tariff == "free":
                    if project.updated_at:
                        days_inactive = (datetime.now(timezone.utc) - project.updated_at).days
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
