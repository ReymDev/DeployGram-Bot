from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.server import Server
from repositories.base import BaseRepository


class ServerRepository(BaseRepository[Server]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Server)

    async def get_online_servers(self) -> list[Server]:
        result = await self.session.execute(
            select(Server).where(Server.status == "online").order_by(Server.rating.desc())
        )
        return list(result.scalars().all())

    async def get_with_free_slots(self, premium: bool = False) -> list[Server]:
        if premium:
            result = await self.session.execute(
                select(Server)
                .where(Server.status == "online", Server.free_slots_premium > 0)
                .order_by(Server.rating.desc())
            )
        else:
            result = await self.session.execute(
                select(Server)
                .where(Server.status == "online", Server.free_slots > 0)
                .order_by(Server.rating.desc())
            )
        return list(result.scalars().all())
