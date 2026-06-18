from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.coowner import CoOwner
from repositories.base import BaseRepository


class CoOwnerRepository(BaseRepository[CoOwner]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CoOwner)

    async def get_by_project_id(self, project_id: int) -> list[CoOwner]:
        result = await self.session.execute(
            select(CoOwner).where(CoOwner.project_id == project_id)
        )
        return list(result.scalars().all())

    async def get_by_user_and_project(self, user_id: int, project_id: int) -> CoOwner | None:
        result = await self.session.execute(
            select(CoOwner).where(
                CoOwner.user_id == user_id,
                CoOwner.project_id == project_id,
            )
        )
        return result.scalar_one_or_none()
