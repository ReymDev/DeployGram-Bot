from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.emojis import Emoji, EmojiID


def get_welcome_keyboard() -> InlineKeyboardMarkup:
    """Главное меню - всегда показываем все кнопки."""
    builder = InlineKeyboardBuilder()
    
    # Главные действия
    builder.row(
        InlineKeyboardButton(
            text="📱 Мои проекты",
            style="success",
            callback_data="control_panel",
        ),
    )
    
    # Дополнительные функции
    builder.row(
        InlineKeyboardButton(text="💳 Подписка", style="primary", callback_data="subscription"),
        InlineKeyboardButton(text="💾 Бэкапы", style="primary", callback_data="backups_list"),
    )
    builder.row(
        InlineKeyboardButton(text="🎁 Промокод", style="primary", callback_data="promo_activate"),
        InlineKeyboardButton(text="🔗 Рефералы", style="primary", callback_data="referrals"),
    )
    builder.row(
        InlineKeyboardButton(text="👤 Профиль", style="primary", callback_data="profile"),
        InlineKeyboardButton(text="⚙️ Настройки", style="primary", callback_data="settings"),
    )

    return builder.as_markup()


def get_control_panel_keyboard(has_bots: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура когда нет проектов - только кнопка Создать проект."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="➕ Создать проект", style="success", callback_data="create_project"),
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", style="primary", callback_data="main_menu"),
    )

    return builder.as_markup()


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return get_control_panel_keyboard()


def get_back_keyboard(callback_data: str = "control_panel") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Назад",
            style="primary",
            callback_data=callback_data,
        ),
    )
    return builder.as_markup()


def get_confirm_keyboard(confirm_data: str, cancel_data: str = "control_panel") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Подтвердить",
            callback_data=confirm_data,
            style="success",
        ),
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data=cancel_data,
            style="primary",
        ),
    )
    return builder.as_markup()
