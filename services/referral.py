from __future__ import annotations

import secrets
import string

from sqlalchemy.ext.asyncio import AsyncSession

from models.referral import Referral
from repositories.referral import ReferralRepository


class ReferralService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.referral_repo = ReferralRepository(session)

    async def process_referral(self, referrer_telegram_id: int, referred_telegram_id: int) -> Referral | None:
        """Process referral by telegram IDs - converts to user IDs and creates referral"""
        # Проверка что это не сам себя
        if referrer_telegram_id == referred_telegram_id:
            return None
        
        # Получаем user IDs из telegram IDs
        from repositories.user import UserRepository
        user_repo = UserRepository(self.session)
        
        referrer = await user_repo.get_by_telegram_id(referrer_telegram_id)
        referred = await user_repo.get_by_telegram_id(referred_telegram_id)
        
        if not referrer or not referred:
            return None
        
        # Проверяем что referred еще не был приглашен
        existing = await self.referral_repo.get_by_referred(referred.id)
        if existing:
            return None
        
        return await self.referral_repo.create(
            referrer_id=referrer.id,
            referred_id=referred.id,
        )

    async def get_referral_link(self, user_id: int) -> str:
        return f"https://t.me/{await self._get_bot_username()}?start={user_id}"

    async def get_referrals_count(self, user_id: int) -> int:
        referrals = await self.referral_repo.get_by_referrer(user_id)
        return len(referrals)

    async def get_referrals(self, user_id: int) -> list[Referral]:
        return await self.referral_repo.get_by_referrer(user_id)

    async def _get_bot_username(self) -> str:
        return "DeployGramBot"
