from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    plan: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    payment_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


def get_premium_prices() -> dict:
    from bot.config import settings
    return {
        "1_week": {"days": 7, "price": settings.PREMIUM_PRICE_1W, "label": "1 неделя"},
        "1_month": {"days": 30, "price": settings.PREMIUM_PRICE_1M, "label": "1 месяц"},
        "3_months": {"days": 90, "price": settings.PREMIUM_PRICE_3M, "label": "3 месяца", "discount": "-10%"},
        "6_months": {"days": 180, "price": settings.PREMIUM_PRICE_6M, "label": "6 месяцев", "discount": "-15%"},
        "12_months": {"days": 365, "price": settings.PREMIUM_PRICE_12M, "label": "12 месяцев", "discount": "-20%"},
    }


def get_free_features() -> list[str]:
    from bot.config import settings
    return [
        f"{settings.FREE_TARIFF_PROJECTS} бот",
        "общий пул слотов",
        f"до {settings.FREE_TARIFF_RAM} RAM и {settings.FREE_TARIFF_CPU} CPU",
        f"бот удаляется, если ты неактивен {settings.INACTIVE_DELETE_DAYS} дней",
        f"бэкапы раз в {settings.BACKUP_INTERVAL_HOURS} часа",
    ]


def get_premium_features() -> list[str]:
    from bot.config import settings
    return [
        f"от 2 до {settings.PREMIUM_TARIFF_PROJECTS} ботов - выбираешь ты",
        "отдельный пул слотов",
        f"{settings.PREMIUM_TARIFF_RAM} RAM и {settings.PREMIUM_TARIFF_CPU} CPU на всех твоих ботов",
        "трекинг активности отключен",
        "бэкапы каждый час",
        "авторестарт при ошибках",
        "предоставлен FFmpeg",
    ]
