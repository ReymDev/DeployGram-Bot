from __future__ import annotations

import os
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    BOT_TOKEN: str = ""
    ADMIN_IDS: List[int] = []

    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, (int, float)):
            return [int(v)]
        if isinstance(v, str):
            v = v.strip("[]")
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v

    DATABASE_URL: str = "sqlite+aiosqlite:///data/deploygram.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "change-me"

    DEFAULT_TARIFF: str = "free"
    FREE_TARIFF_PROJECTS: int = 1
    FREE_TARIFF_RAM: int = 256
    FREE_TARIFF_CPU: float = 0.3
    FREE_TARIFF_DISK: int = 100

    PREMIUM_TARIFF_PROJECTS: int = 5
    PREMIUM_TARIFF_RAM: int = 1024
    PREMIUM_TARIFF_CPU: float = 1.0
    PREMIUM_TARIFF_DISK: int = 500

    AUTO_SLEEP_MINUTES: int = 0
    BACKUP_INTERVAL_HOURS: int = 24
    INACTIVE_DELETE_DAYS: int = 5

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.DATABASE_URL

    @property
    def is_mysql(self) -> bool:
        return "mysql" in self.DATABASE_URL


settings = Settings()
