from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.user import get_settings_keyboard
from bot.utils.emojis import Emoji

router = Router()


@router.callback_query(F.data == "project_settings")
async def project_settings(callback: CallbackQuery):
    await callback.answer("Настройки проекта в разработке", show_alert=True)
