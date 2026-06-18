from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.backup import Backup
from repositories.base import BaseRepository


class BackupRepository(BaseRepository[Backup]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Backup)

    async def get_by_project_id(self, project_id: int) -> list[Backup]:
        result = await self.session.execute(
            select(Backup)
            .where(Backup.project_id == project_id)
            .order_by(Backup.created_at.desc())
        )
        return list(result.scalars().all())
