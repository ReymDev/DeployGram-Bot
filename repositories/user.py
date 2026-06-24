from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserSettings
from repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self, telegram_id: int, username: str | None = None, full_name: str | None = None, referral_id: int | None = None
    ) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            if username:
                user.username = username
            if full_name:
                user.full_name = full_name
            await self.session.flush()
            return user
        user = await self.create(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            referral_id=referral_id,
        )
        await self.session.flush()
        settings = UserSettings(user_id=user.id)
        self.session.add(settings)
        await self.session.flush()
        return user

    async def get_active_users(self, limit: int = 1000) -> list[User]:
        result = await self.session.execute(
            select(User).where(User.status == "active", User.is_banned == False).limit(limit)
        )
        return list(result.scalars().all())

    async def ban_user(self, user_id: int) -> User | None:
        return await self.update(user_id, is_banned=True, status="banned")

    async def unban_user(self, user_id: int) -> User | None:
        return await self.update(user_id, is_banned=False, status="active")


class UserSettingsRepository(BaseRepository[UserSettings]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserSettings)

    async def get_by_user_id(self, user_id: int) -> UserSettings | None:
        result = await self.session.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()
