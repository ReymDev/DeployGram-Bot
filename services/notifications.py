from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.user import User

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def send(self, user: User, text: str, keyboard: InlineKeyboardMarkup | None = None) -> None:
        try:
            if user.settings:
                pass
            await self.bot.send_message(
                chat_id=user.telegram_id,
                text=text,
                reply_markup=keyboard,
            )
        except Exception as e:
            logger.error("Failed to send notification to %d: %s", user.telegram_id, e)

    async def notify_container_stopped(self, user: User, project_name: str) -> None:
        if user.settings and not user.settings.notify_container_stopped:
            return
        from bot.utils.emojis import Emoji
        await self.send(user, f"{Emoji.CROSS} Контейнер проекта <b>{project_name}</b> остановлен.")

    async def notify_container_started(self, user: User, project_name: str) -> None:
        if user.settings and not user.settings.notify_container_started:
            return
        from bot.utils.emojis import Emoji
        await self.send(user, f"{Emoji.CHECK} Контейнер проекта <b>{project_name}</b> запущен.")

    async def notify_error(self, user: User, project_name: str, error: str) -> None:
        if user.settings and not user.settings.notify_error:
            return
        from bot.utils.emojis import Emoji
        await self.send(user, f"{Emoji.CROSS} Ошибка запуска <b>{project_name}</b>:\n<code>{error[:500]}</code>")

    async def notify_high_cpu(self, user: User, project_name: str, cpu: float) -> None:
        if user.settings and not user.settings.notify_high_cpu:
            return
        from bot.utils.emojis import Emoji
        await self.send(user, f"{Emoji.NOTIF} Высокая нагрузка CPU ({cpu:.1f}%) на <b>{project_name}</b>")

    async def notify_high_ram(self, user: User, project_name: str, ram: float) -> None:
        if user.settings and not user.settings.notify_high_ram:
            return
        from bot.utils.emojis import Emoji
        await self.send(user, f"{Emoji.NOTIF} Высокая нагрузка RAM ({ram:.1f} MB) на <b>{project_name}</b>")

    async def notify_low_disk(self, user: User, project_name: str, disk: float) -> None:
        if user.settings and not user.settings.notify_low_disk:
            return
        from bot.utils.emojis import Emoji
        await self.send(user, f"{Emoji.NOTIF} Мало места на диске ({disk:.1f} MB) в <b>{project_name}</b>")

    async def notify_backup_created(self, user: User, project_name: str) -> None:
        if user.settings and not user.settings.notify_backup_created:
            return
        from bot.utils.emojis import Emoji
        await self.send(user, f"{Emoji.GIFT} Бэкап проекта <b>{project_name}</b> создан.")

    async def notify_update_done(self, user: User, project_name: str) -> None:
        if user.settings and not user.settings.notify_update_done:
            return
        from bot.utils.emojis import Emoji
        await self.send(user, f"{Emoji.CHECK} Проект <b>{project_name}</b> обновлён.")
