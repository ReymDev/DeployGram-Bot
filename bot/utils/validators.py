from __future__ import annotations

import re

from pydantic import BaseModel, field_validator


class ProjectCreateData(BaseModel):
    name: str
    source_type: str
    source_url: str | None = None
    python_version: str = "3.12"
    entry_point: str = "main.py"
    entry_type: str = "script"
    server_id: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_-]{1,50}$", v):
            raise ValueError("Имя проекта: буквы, цифры, _ - (1-50 символов)")
        return v

    @field_validator("python_version")
    @classmethod
    def validate_python(cls, v: str) -> str:
        if v not in ("3.10", "3.11", "3.12"):
            raise ValueError("Поддерживаются: 3.10, 3.11, 3.12")
        return v

    @field_validator("source_type")
    @classmethod
    def validate_source(cls, v: str) -> str:
        if v not in ("zip", "github"):
            raise ValueError("Тип источника: zip или github")
        return v
