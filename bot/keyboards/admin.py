from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.emojis import EmojiID


def get_admin_keyboard(users_count: int, projects_count: int, servers_count: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"👤 Пользователи ({users_count})",
            callback_data="admin_users",
            icon_custom_emoji_id=EmojiID.PROFILE,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="💎 Подписки",
            callback_data="admin_subscriptions",
        ),
        InlineKeyboardButton(
            text="🌍 Локации",
            callback_data="admin_locations",
            icon_custom_emoji_id=EmojiID.HOME,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=f"🖥 Серверы ({servers_count})",
            callback_data="admin_servers",
        ),
        InlineKeyboardButton(
            text=f"📊 Статистика",
            callback_data="admin_stats",
            icon_custom_emoji_id=EmojiID.GRAPH_STATS,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🎁 Промокоды",
            callback_data="admin_promos",
            icon_custom_emoji_id=EmojiID.GIFT,
        ),
        InlineKeyboardButton(
            text="🔗 Рефералы",
            callback_data="admin_referrals",
            icon_custom_emoji_id=EmojiID.LINK,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="📢 Рассылки",
            callback_data="admin_broadcast",
            icon_custom_emoji_id=EmojiID.SPEAKER,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="⚙ Настройки",
            callback_data="admin_settings",
            icon_custom_emoji_id=EmojiID.SETTINGS,
        ),
    )
    return builder.as_markup()


def get_admin_users_keyboard(users: list, page: int = 0, per_page: int = 5) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start = page * per_page
    end = start + per_page
    page_users = users[start:end]

    for u in page_users:
        status_icon = "🚫" if u.is_banned else "✅"
        builder.row(
            InlineKeyboardButton(
                text=f"{status_icon} {u.username or u.telegram_id} ({u.tariff})",
                callback_data=f"admin_user_view_{u.id}",
            )
        )

    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(text="◁", callback_data=f"admin_users_page_{page - 1}")
        )
    if end < len(users):
        nav_row.append(
            InlineKeyboardButton(text="▷", callback_data=f"admin_users_page_{page + 1}")
        )
    if nav_row:
        builder.row(*nav_row)

    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data="admin_panel"),
    )
    return builder.as_markup()


def get_admin_user_detail_keyboard(user_id: int, is_banned: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if is_banned:
        builder.row(
            InlineKeyboardButton(
                text="✅ Разбан",
                callback_data=f"admin_user_unban_{user_id}",
                style="success",
            ),
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="🚫 Забанить",
                callback_data=f"admin_user_ban_{user_id}",
                style="danger",
            ),
        )

    builder.row(
        InlineKeyboardButton(
            text="💎 Изменить тариф",
            callback_data=f"admin_user_tariff_{user_id}",
        ),
        InlineKeyboardButton(
            text="💰 Баланс",
            callback_data=f"admin_user_balance_{user_id}",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data="admin_users"),
    )
    return builder.as_markup()


def get_admin_servers_keyboard(servers: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for s in servers:
        status_icon = "🟢" if s.status == "online" else "🔴"
        builder.row(
            InlineKeyboardButton(
                text=f"{status_icon} {s.name} ({s.country})",
                callback_data=f"admin_server_view_{s.id}",
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="➕ Добавить сервер",
            callback_data="admin_server_add",
            style="primary",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data="admin_panel"),
    )
    return builder.as_markup()


def get_admin_promos_keyboard(promos: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for p in promos:
        builder.row(
            InlineKeyboardButton(
                text=f"🎁 {p.code} ({p.activated_count}/{p.max_activations})",
                callback_data=f"admin_promo_view_{p.id}",
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="➕ Создать промокод",
            callback_data="admin_promo_create",
            style="primary",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data="admin_panel"),
    )
    return builder.as_markup()


def get_admin_settings_keyboard(auto_sleep: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    options = [0, 30, 60, 360, 1440]
    labels = ["Выключен", "30 минут", "1 час", "6 часов", "24 часа"]

    for opt, label in zip(options, labels):
        icon = "✅" if auto_sleep == opt else "  "
        builder.row(
            InlineKeyboardButton(
                text=f"{icon} Автосон: {label}",
                callback_data=f"admin_sleep_{opt}",
            )
        )

    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data="admin_panel"),
    )
    return builder.as_markup()
