from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from models.server import Server
from repositories.server import ServerRepository


class RatingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.server_repo = ServerRepository(session)

    async def calculate_rating(self, server_id: int) -> float:
        server = await self.server_repo.get_by_id(server_id)
        if server is None:
            return 0.0

        slot_score = (server.free_slots / max(server.total_slots, 1)) * 30
        load_score = max(0, (100 - server.load_cpu)) * 0.3
        ping_score = max(0, 100 - server.ping) * 0.2

        rating = slot_score + load_score + ping_score
        await self.server_repo.update(server_id, rating=round(rating, 1))
        return round(rating, 1)

    async def update_all_ratings(self) -> None:
        servers = await self.server_repo.get_all()
        for server in servers:
            await self.calculate_rating(server.id)
