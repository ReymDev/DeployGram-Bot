from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.emojis import Emoji, EmojiID


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📦 Мои проекты",
            callback_data="my_projects",
            icon_custom_emoji_id=EmojiID.FILE,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="➕ Создать проект",
            callback_data="create_project",
            icon_custom_emoji_id=EmojiID.CHECK,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🌍 Серверы",
            callback_data="locations",
            icon_custom_emoji_id=EmojiID.HOME,
        ),
        InlineKeyboardButton(
            text="👤 Профиль",
            callback_data="profile",
            icon_custom_emoji_id=EmojiID.PROFILE,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🔗 Рефералы",
            callback_data="referrals",
            icon_custom_emoji_id=EmojiID.LINK,
        ),
        InlineKeyboardButton(
            text="🎁 Промокод",
            callback_data="promo_activate",
            icon_custom_emoji_id=EmojiID.GIFT,
        ),
    )
    return builder.as_markup()


def get_back_keyboard(callback_data: str = "main_menu") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="◁ Назад",
            callback_data=callback_data,
        ),
    )
    return builder.as_markup()


def get_confirm_keyboard(confirm_data: str, cancel_data: str = "main_menu") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Да",
            callback_data=confirm_data,
            style="success",
        ),
        InlineKeyboardButton(
            text="❌ Нет",
            callback_data=cancel_data,
            style="danger",
        ),
    )
    return builder.as_markup()
