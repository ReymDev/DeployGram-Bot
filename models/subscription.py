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


FREE_FEATURES = [
    "1 бот",
    "общий пул слотов",
    "до 256 RAM и 0.3 CPU",
    "бот удаляется, если ты неактивен 5 дней",
    "бэкапы раз в 24 часа",
]

PREMIUM_FEATURES = [
    "от 2 до 5 ботов - выбираешь ты",
    "отдельный пул слотов",
    "1024 RAM и 1 CPU на всех твоих ботов",
    "трекинг активности отключен",
    "бэкапы каждый час",
    "авторестарт при ошибках",
    "предоставлен FFmpeg",
]

PREMIUM_PRICES = {
    "1_week": {"days": 7, "price": 49, "label": "1 неделя"},
    "1_month": {"days": 30, "price": 149, "label": "1 месяц"},
    "3_months": {"days": 90, "price": 402, "label": "3 месяца", "discount": "-10%"},
    "6_months": {"days": 180, "price": 759, "label": "6 месяцев", "discount": "-15%"},
    "12_months": {"days": 365, "price": 1430, "label": "12 месяцев", "discount": "-20%"},
}
