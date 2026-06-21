from __future__ import annotations

import json
import logging
from pathlib import Path

from bot.config import BASE_DIR

logger = logging.getLogger(__name__)

PHOTOS_DIR = BASE_DIR / "data" / "photos"
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

PHOTOS_FILE = PHOTOS_DIR / "photos.json"

DEFAULT_PHOTOS = {
    "welcome": None,
    "control_panel": None,
    "subscription": None,
    "premium_info": None,
    "buy_subscription": None,
    "backups": None,
    "create_backup": None,
    "server_selection": None,
    "upload_source": None,
    "python_version": None,
    "file_upload": None,
    "github_repos": None,
    "entry_point": None,
    "entry_point_script": None,
    "entry_point_module": None,
    "entry_confirm": None,
    "bot_ready": None,
    "bot_control": None,
    "logs": None,
    "bot_settings": None,
    "library_manager": None,
    "file_manager": None,
    "python_change": None,
    "entry_change": None,
    "rename_bot": None,
    "delete_bot": None,
    "bot_deleted": None,
    "admin_panel": None,
    "admin_users": None,
    "admin_servers": None,
    "admin_stats": None,
    "admin_promos": None,
    "admin_settings": None,
}

PHOTO_LABELS = {
    "welcome": "Экран приветствия",
    "control_panel": "Панель управления (список ботов)",
    "subscription": "Управление подпиской",
    "premium_info": "Информация о Premium",
    "buy_subscription": "Покупка подписки",
    "backups": "Список бэкапов",
    "create_backup": "Создание бэкапа",
    "server_selection": "Выбор сервера",
    "upload_source": "Откуда загружаем (ZIP/GitHub)",
    "python_version": "Выбор версии Python",
    "file_upload": "Загрузка файлов",
    "github_repos": "Выбор репозитория GitHub",
    "entry_point": "Выбор точки входа (режим)",
    "entry_point_script": "Файловый браузер точки входа",
    "entry_point_module": "Ввод модуля вручную",
    "entry_confirm": "Подтверждение точки входа",
    "bot_ready": "Бот готов к работе",
    "bot_control": "Панель управления ботом",
    "logs": "Логи бота",
    "bot_settings": "Настройки бота",
    "library_manager": "Менеджер библиотек",
    "file_manager": "Файловый менеджер",
    "python_change": "Смена версии Python",
    "entry_change": "Смена точки входа",
    "rename_bot": "Смена названия бота",
    "delete_bot": "Удаление бота",
    "bot_deleted": "Бот удалён",
    "admin_panel": "Админ-панель",
    "admin_users": "Админка - Пользователи",
    "admin_servers": "Админка - Серверы",
    "admin_stats": "Админка - Статистика",
    "admin_promos": "Админка - Промокоды",
    "admin_settings": "Админка - Настройки",
}


def load_photos() -> dict[str, str | None]:
    if PHOTOS_FILE.exists():
        try:
            with open(PHOTOS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key in DEFAULT_PHOTOS:
                    if key not in data:
                        data[key] = DEFAULT_PHOTOS[key]
                return data
        except Exception as e:
            logger.error("Failed to load photos config: %s", e)
    return DEFAULT_PHOTOS.copy()


def save_photos(photos: dict[str, str | None]) -> None:
    try:
        with open(PHOTOS_FILE, "w", encoding="utf-8") as f:
            json.dump(photos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("Failed to save photos config: %s", e)


def get_photo(key: str) -> str | None:
    photos = load_photos()
    return photos.get(key)


def set_photo(key: str, file_id: str) -> None:
    photos = load_photos()
    photos[key] = file_id
    save_photos(photos)


def get_all_photos() -> dict[str, str | None]:
    return load_photos()
