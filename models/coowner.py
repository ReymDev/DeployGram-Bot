from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.project import Project


class CoOwner(Base):
    __tablename__ = "coowners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), default="developer", nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Разрешения для совладельцев
    can_start_stop: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_view_logs: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_edit_files: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_manage_deps: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_view_settings: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    project: Mapped[Project] = relationship("Project", back_populates="coowners")
