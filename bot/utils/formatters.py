from __future__ import annotations

from typing import Optional

from bot.utils.emojis import Emoji


def format_bytes(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes / 1024**2:.1f} MB"
    return f"{size_bytes / 1024**3:.2f} GB"


def format_uptime(seconds: int) -> str:
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def format_status(status: str) -> str:
    statuses = {
        "running": f"{Emoji.CHECK} Работает",
        "stopped": f"{Emoji.CROSS} Остановлен",
        "starting": f"{Emoji.LOADING} Запускается",
        "error": f"{Emoji.CROSS} Ошибка",
        "creating": f"{Emoji.LOADING} Создаётся",
    }
    return statuses.get(status, status)


def truncate_text(text: str, max_length: int = 3500) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 20] + "\n\n... (обрезано)"
