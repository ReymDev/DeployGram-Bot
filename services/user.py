from __future__ import annotations

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from models.user import User
from repositories.user import UserRepository, UserSettingsRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.user_repo = UserRepository(session)
        self.settings_repo = UserSettingsRepository(session)

    async def get_or_create_user(
        self, telegram_id: int, username: str | None = None,
        full_name: str | None = None, referral_id: int | None = None
    ) -> User:
        return await self.user_repo.get_or_create(
            telegram_id, username, full_name, referral_id
        )

    async def get_user(self, telegram_id: int) -> User | None:
        return await self.user_repo.get_by_telegram_id(telegram_id)

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.user_repo.get_by_id(user_id)

    async def get_max_projects(self, tariff: str) -> int:
        if tariff == "premium":
            return settings.PREMIUM_TARIFF_PROJECTS
        return settings.FREE_TARIFF_PROJECTS

    async def get_tariff_limits(self, tariff: str) -> dict:
        if tariff == "premium":
            return {
                "projects": settings.PREMIUM_TARIFF_PROJECTS,
                "ram": settings.PREMIUM_TARIFF_RAM,
                "cpu": settings.PREMIUM_TARIFF_CPU,
                "disk": settings.PREMIUM_TARIFF_DISK,
            }
        return {
            "projects": settings.FREE_TARIFF_PROJECTS,
            "ram": settings.FREE_TARIFF_RAM,
            "cpu": settings.FREE_TARIFF_CPU,
            "disk": settings.FREE_TARIFF_DISK,
        }

    async def ban_user(self, user_id: int) -> User | None:
        return await self.user_repo.ban_user(user_id)

    async def unban_user(self, user_id: int) -> User | None:
        return await self.user_repo.unban_user(user_id)

    async def set_tariff(self, user_id: int, tariff: str) -> User | None:
        return await self.user_repo.update(user_id, tariff=tariff)

    async def update_balance(self, user_id: int, amount: float) -> User | None:
        from sqlalchemy import literal_column
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(balance=User.balance + amount)
        )
        await self.session.flush()
        return await self.user_repo.get_by_id(user_id)

    async def get_settings(self, user_id: int):
        return await self.settings_repo.get_by_user_id(user_id)

    async def toggle_setting(self, user_id: int, setting_name: str):
        s = await self.settings_repo.get_by_user_id(user_id)
        if s is None:
            return None
        current = getattr(s, setting_name, None)
        if current is None:
            return None
        return await self.settings_repo.update(s.id, **{setting_name: not current})

    async def get_all_users(self, limit: int = 100, offset: int = 0):
        return await self.user_repo.get_all(limit, offset)

    async def count_users(self) -> int:
        return await self.user_repo.count()
