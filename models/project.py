from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.coowner import CoOwner
    from models.log import ProjectLog
    from models.user import User


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    python_version: Mapped[str] = mapped_column(String(10), default="3.12", nullable=False)
    entry_point: Mapped[str] = mapped_column(String(512), default="main.py", nullable=False)
    entry_type: Mapped[str] = mapped_column(String(50), default="script", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="stopped", nullable=False)
    server_id: Mapped[Optional[int]] = mapped_column(ForeignKey("servers.id", ondelete="SET NULL"), nullable=True)
    docker_container_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    restart_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped[User] = relationship("User", back_populates="projects")
    versions: Mapped[list[ProjectVersion]] = relationship(
        "ProjectVersion", back_populates="project", lazy="selectin", order_by="ProjectVersion.created_at.desc()"
    )
    stats: Mapped[list[ProjectStats]] = relationship(
        "ProjectStats", back_populates="project", lazy="selectin"
    )
    backups: Mapped[list] = relationship("Backup", back_populates="project", lazy="selectin")
    coowners: Mapped[list[CoOwner]] = relationship("CoOwner", back_populates="project", lazy="selectin")
    logs: Mapped[list[ProjectLog]] = relationship("ProjectLog", back_populates="project", lazy="selectin")


class ProjectVersion(Base):
    __tablename__ = "project_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    files_hash: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    entry_point: Mapped[str] = mapped_column(String(512), nullable=False)
    secrets: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    python_version: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    project: Mapped[Project] = relationship("Project", back_populates="versions")


class ProjectStats(Base):
    __tablename__ = "project_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    cpu_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    ram_mb: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    disk_mb: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    project: Mapped[Project] = relationship("Project", back_populates="stats")
