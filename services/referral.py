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

    async def process_referral(self, referrer_id: int, referred_id: int) -> Referral | None:
        existing = await self.referral_repo.get_by_referred(referred_id)
        if existing:
            return None
        if referrer_id == referred_id:
            return None
        return await self.referral_repo.create(
            referrer_id=referrer_id,
            referred_id=referred_id,
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
