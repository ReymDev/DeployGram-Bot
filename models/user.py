from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.project import Project
    from models.referral import Referral


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    tariff: Mapped[str] = mapped_column(String(50), default="free", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    referral_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    settings: Mapped[Optional[UserSettings]] = relationship(
        "UserSettings", back_populates="user", uselist=False, lazy="selectin"
    )
    projects: Mapped[list[Project]] = relationship("Project", back_populates="user", lazy="selectin")
    referrals_made: Mapped[list[Referral]] = relationship(
        "Referral", foreign_keys="Referral.referrer_id", back_populates="referrer", lazy="selectin"
    )


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    notify_container_stopped: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_container_started: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_error: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_high_cpu: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_high_ram: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_low_disk: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_backup_created: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_update_done: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="settings")
