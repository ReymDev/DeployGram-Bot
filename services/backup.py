from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from models.backup import Backup
from repositories.backup import BackupRepository
from repositories.project import ProjectRepository


class BackupService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.backup_repo = BackupRepository(session)
        self.project_repo = ProjectRepository(session)

    async def create_backup(self, project_id: int, version_id: int | None = None, size: int = 0) -> Backup | None:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            return None
        return await self.backup_repo.create(
            project_id=project_id,
            version_id=version_id,
            size=size,
        )

    async def get_backups(self, project_id: int) -> list[Backup]:
        return await self.backup_repo.get_by_project_id(project_id)

    async def delete_backup(self, backup_id: int) -> bool:
        return await self.backup_repo.delete(backup_id)

    async def restore_backup(self, backup_id: int) -> bool:
        backup = await self.backup_repo.get_by_id(backup_id)
        if backup is None:
            return False
        return True
