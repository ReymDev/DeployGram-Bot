from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.promo import PromoCode
from repositories.base import BaseRepository


class PromoRepository(BaseRepository[PromoCode]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PromoCode)

    async def get_by_code(self, code: str) -> PromoCode | None:
        result = await self.session.execute(
            select(PromoCode).where(PromoCode.code == code.upper())
        )
        return result.scalar_one_or_none()
