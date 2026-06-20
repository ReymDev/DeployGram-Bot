from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ErrorEvent

from bot.config import settings, BASE_DIR
from bot.middlewares.database import DatabaseMiddleware
from bot.middlewares.auth import AuthMiddleware
from bot.middlewares.rate_limit import RateLimitMiddleware
from bot.handlers.user.start import router as start_router
from bot.handlers.user.profile import router as profile_router
from bot.handlers.user.projects import router as projects_router
from bot.handlers.user.project_create import router as create_router
from bot.handlers.user.project_manage import router as manage_router
from bot.handlers.user.project_monitor import router as monitor_router
from bot.handlers.user.project_logs import router as logs_router
from bot.handlers.user.project_secrets import router as secrets_router
from bot.handlers.user.project_files import router as files_router
from bot.handlers.user.project_editor import router as editor_router
from bot.handlers.user.backups import router as backups_router
from bot.handlers.user.coowners import router as coowners_router
from bot.handlers.user.versions import router as versions_router
from bot.handlers.user.settings import router as settings_router
from bot.handlers.user.locations import router as locations_router
from bot.handlers.user.referrals import router as referrals_router
from bot.handlers.user.promos import router as promos_router
from bot.handlers.admin.panel import router as admin_router

LOG_DIR = BASE_DIR / "data"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "bot.log"

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))

logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])
logger = logging.getLogger(__name__)


def setup_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    dp.message.middleware(DatabaseMiddleware())
    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(RateLimitMiddleware())

    dp.callback_query.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())

    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(projects_router)
    dp.include_router(create_router)
    dp.include_router(manage_router)
    dp.include_router(monitor_router)
    dp.include_router(logs_router)
    dp.include_router(secrets_router)
    dp.include_router(files_router)
    dp.include_router(editor_router)
    dp.include_router(backups_router)
    dp.include_router(coowners_router)
    dp.include_router(versions_router)
    dp.include_router(settings_router)
    dp.include_router(locations_router)
    dp.include_router(referrals_router)
    dp.include_router(promos_router)
    dp.include_router(admin_router)

    return dp


async def main() -> None:
    from db.engine import engine
    from models.base import Base
    import models  # noqa: F401 — ensure all models are registered

    logger.info("ADMIN_IDS parsed as: %s", settings.ADMIN_IDS)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables ensured")

    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = setup_dispatcher()

    dp.errors.register(error_handler)

    logger.info("DeployGram bot starting...")
    await dp.start_polling(bot)


async def error_handler(event: ErrorEvent, exception: Exception):
    logger.error("Unhandled exception in update %s: %s", event.update.update_id, exception, exc_info=True)
