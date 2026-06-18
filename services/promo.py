from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from models.promo import PromoCode
from repositories.promo import PromoRepository


class PromoService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.promo_repo = PromoRepository(session)

    async def create_promo(
        self,
        code: str,
        reward_type: str,
        reward_value: str,
        max_activations: int = 1,
        expires_at: datetime | None = None,
        created_by: int = 0,
    ) -> PromoCode:
        return await self.promo_repo.create(
            code=code.upper(),
            reward_type=reward_type,
            reward_value=reward_value,
            max_activations=max_activations,
            expires_at=expires_at,
            created_by=created_by,
        )

    async def activate_promo(self, code: str) -> tuple[bool, str, PromoCode | None]:
        promo = await self.promo_repo.get_by_code(code)
        if promo is None:
            return False, "Промокод не найден", None
        if promo.activated_count >= promo.max_activations:
            return False, "Промокод уже использован максимальное количество раз", None
        if promo.expires_at and promo.expires_at < datetime.utcnow():
            return False, "Промокод истёк", None
        await self.promo_repo.update(
            promo.id, activated_count=promo.activated_count + 1
        )
        return True, f"Промокод активирован! Награда: {promo.reward_type} = {promo.reward_value}", promo

    async def get_promos(self) -> list[PromoCode]:
        return await self.promo_repo.get_all()

    async def delete_promo(self, promo_id: int) -> bool:
        return await self.promo_repo.delete(promo_id)
