from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    ip: Mapped[str] = mapped_column(String(45), nullable=False)
    port: Mapped[int] = mapped_column(Integer, default=8080, nullable=False)
    api_key: Mapped[str] = mapped_column(String(256), nullable=False)
    total_slots: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    free_slots: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    free_slots_premium: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="online", nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    ping: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    load_cpu: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    load_ram: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
