from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.project import Project, ProjectStats, ProjectVersion
from repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Project)

    async def get_by_user_id(self, user_id: int) -> list[Project]:
        result = await self.session.execute(
            select(Project).where(Project.user_id == user_id).order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_coowned_projects(self, user_id: int) -> list[Project]:
        """Get projects where user is a coowner."""
        from models.coowner import CoOwner
        result = await self.session.execute(
            select(Project)
            .join(CoOwner, CoOwner.project_id == Project.id)
            .where(CoOwner.user_id == user_id)
            .order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_all_user_projects(self, user_id: int) -> list[tuple[Project, bool]]:
        """
        Get all projects accessible by user (owned + coowned).
        Returns list of tuples (project, is_coowner).
        """
        # Get owned projects
        owned = await self.get_by_user_id(user_id)
        owned_with_flag = [(p, False) for p in owned]
        
        # Get coowned projects
        coowned = await self.get_coowned_projects(user_id)
        coowned_with_flag = [(p, True) for p in coowned]
        
        # Combine and sort by created_at
        all_projects = owned_with_flag + coowned_with_flag
        all_projects.sort(key=lambda x: x[0].created_at, reverse=True)
        
        return all_projects

    async def get_running_projects(self) -> list[Project]:
        result = await self.session.execute(
            select(Project).where(Project.status == "running")
        )
        return list(result.scalars().all())

    async def get_by_container_id(self, container_id: str) -> Project | None:
        result = await self.session.execute(
            select(Project).where(Project.docker_container_id == container_id)
        )
        return result.scalar_one_or_none()

    async def count_by_user(self, user_id: int) -> int:
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count()).select_from(Project).where(Project.user_id == user_id)
        )
        return result.scalar_one()


class ProjectVersionRepository(BaseRepository[ProjectVersion]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ProjectVersion)

    async def get_by_project_id(self, project_id: int) -> list[ProjectVersion]:
        result = await self.session.execute(
            select(ProjectVersion)
            .where(ProjectVersion.project_id == project_id)
            .order_by(ProjectVersion.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_latest(self, project_id: int) -> ProjectVersion | None:
        result = await self.session.execute(
            select(ProjectVersion)
            .where(ProjectVersion.project_id == project_id)
            .order_by(ProjectVersion.version_number.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


class ProjectStatsRepository(BaseRepository[ProjectStats]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ProjectStats)

    async def get_by_project_id(
        self, project_id: int, limit: int = 100
    ) -> list[ProjectStats]:
        result = await self.session.execute(
            select(ProjectStats)
            .where(ProjectStats.project_id == project_id)
            .order_by(ProjectStats.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_latest(self, project_id: int) -> ProjectStats | None:
        result = await self.session.execute(
            select(ProjectStats)
            .where(ProjectStats.project_id == project_id)
            .order_by(ProjectStats.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
