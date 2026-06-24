from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.emojis import EmojiID


COUNTRY_FLAGS = {
    "Россия": "🇷🇺",
    "Germany": "🇩🇪",
    "Германия": "🇩🇪",
    "Netherlands": "🇳🇱",
    "Нидерланды": "🇳🇱",
    "Finland": "🇫🇮",
    "Финляндия": "🇫🇮",
    "USA": "🇺🇸",
    "США": "🇺🇸",
    "France": "🇫🇷",
    "Франция": "🇫🇷",
    "UK": "🇬🇧",
    "Великобритания": "🇬🇧",
    "Japan": "🇯🇵",
    "Япония": "🇯🇵",
    "Singapore": "🇸🇬",
    "Сингапур": "🇸🇬",
}


def get_flag(country: str) -> str:
    for key, flag in COUNTRY_FLAGS.items():
        if key.lower() in country.lower():
            return flag
    return "🏳"


def get_bot_list_keyboard(bots: list, page: int = 0, per_page: int = 5) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start = page * per_page
    end = start + per_page
    page_bots = bots[start:end]

    for b in page_bots:
        status_icon = "🟢" if b.status == "running" else "🔴"
        builder.row(
            InlineKeyboardButton(
                text=f"{status_icon} {b.name}",
                callback_data=f"bot_view_{b.id}",
            )
        )

    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(text="◀", callback_data=f"bots_page_{page - 1}")
        )
    if end < len(bots):
        nav_row.append(
            InlineKeyboardButton(text="▶", callback_data=f"bots_page_{page + 1}")
        )
    if nav_row:
        builder.row(*nav_row)

    builder.row(
        InlineKeyboardButton(
            text="➕ Добавить бота",
            callback_data="add_bot",
            style="primary",
        ),
    )
    return builder.as_markup()


def get_bot_control_keyboard(bot_id: int, status: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if status == "running":
        builder.row(
            InlineKeyboardButton(
                text="⏹ Остановить",
                callback_data=f"bot_stop_{bot_id}",
                style="danger",
            ),
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="▶ Запустить",
                callback_data=f"bot_start_{bot_id}",
                style="success",
            ),
        )

    builder.row(
        InlineKeyboardButton(
            text="📋 Логи",
            callback_data=f"bot_logs_{bot_id}",
        ),
        InlineKeyboardButton(
            text="⚙ Настройки бота",
            callback_data=f"bot_settings_{bot_id}",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="control_panel"),
    )
    return builder.as_markup()


def get_bot_settings_keyboard(bot_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📦 Библиотеки", callback_data=f"bot_libs_{bot_id}"),
        InlineKeyboardButton(text="📁 Файлы", callback_data=f"bot_files_{bot_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="🐍 Версия Python", callback_data=f"bot_python_{bot_id}"),
        InlineKeyboardButton(text="📄 Точка входа", callback_data=f"bot_entry_{bot_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="👥 Совладельцы", callback_data=f"bot_coowners_{bot_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="📊 Графики", callback_data=f"bot_graphs_{bot_id}"),
        InlineKeyboardButton(text="🔔 Уведомления", callback_data=f"bot_notify_{bot_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="✏ Переименовать", callback_data=f"bot_rename_{bot_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="🗑 Удалить бота", callback_data=f"bot_delete_{bot_id}", style="danger"),
    )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data=f"bot_view_{bot_id}"),
    )
    return builder.as_markup()


def get_logs_keyboard(bot_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📄 Отправить файлом",
            callback_data=f"logs_file_{bot_id}",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🔄 Обновить логи",
            callback_data=f"bot_logs_{bot_id}",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="✕ Закрыть",
            callback_data=f"bot_view_{bot_id}",
            style="danger",
        ),
    )
    return builder.as_markup()


def get_subscription_keyboard(is_premium: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="❓ Что дает подписка \"Premium\"?",
            callback_data="subscription_info",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="💳 Купить подписку",
            callback_data="subscription_buy",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="control_panel"),
    )
    return builder.as_markup()


def get_buy_subscription_keyboard() -> InlineKeyboardMarkup:
    from bot.config import settings
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=f"1 неделя ({settings.PREMIUM_PRICE_1W}₽)", callback_data="buy_1_week"))
    builder.row(InlineKeyboardButton(text=f"1 месяц ({settings.PREMIUM_PRICE_1M}₽)", callback_data="buy_1_month"))
    builder.row(InlineKeyboardButton(text=f"-10% | 3 месяца ({settings.PREMIUM_PRICE_3M}₽)", callback_data="buy_3_months"))
    builder.row(InlineKeyboardButton(text=f"-15% | 6 месяцев ({settings.PREMIUM_PRICE_6M}₽)", callback_data="buy_6_months"))
    builder.row(InlineKeyboardButton(text=f"-20% | 12 месяцев ({settings.PREMIUM_PRICE_12M}₽)", callback_data="buy_12_months"))
    builder.row(InlineKeyboardButton(text="Назад", callback_data="subscription"))
    return builder.as_markup()


def get_source_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📥 Загрузить файлы",
            callback_data="create_source_zip",
        ),
        InlineKeyboardButton(
            text="🔗 Подключить Github",
            callback_data="create_source_github",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="control_panel"),
    )
    return builder.as_markup()


def get_python_version_keyboard(step: str = "", current: str = "") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"{'✅ ' if current == '3.10' else ''}3.10",
            callback_data=f"create_python_3.10",
        ),
        InlineKeyboardButton(
            text=f"{'✅ ' if current == '3.11' else ''}3.11",
            callback_data=f"create_python_3.11",
        ),
        InlineKeyboardButton(
            text=f"{'✅ ' if current == '3.12' else ''}3.12",
            callback_data=f"create_python_3.12",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="create_back"),
    )
    return builder.as_markup()


def get_entry_mode_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📄 Скрипт",
            callback_data="create_entry_script",
        ),
        InlineKeyboardButton(
            text="📦 Модуль",
            callback_data="create_entry_module",
        ),
    )
    return builder.as_markup()


def get_confirm_entry_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="⬆ ..",
            callback_data="entry_parent",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="✅ Подтвердить",
            callback_data="create_confirm",
            style="success",
        ),
    )
    return builder.as_markup()


def get_file_manager_keyboard(
    bot_id: int, files: list[str], current_path: str
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Кнопка "Назад" если не в корне
    if current_path != "/app" and current_path != "/":
        parent = "/".join(current_path.rstrip("/").split("/")[:-1]) or "/app"
        builder.row(
            InlineKeyboardButton(
                text="⬆ ..",
                callback_data=f"file_nav_{bot_id}_{parent}",
            )
        )

    # Показываем папки и файлы
    for f in files[:20]:  # Ограничение 20 файлов
        is_dir = "/" in f or f.endswith("/") or "." not in f  # Простая эвристика
        icon = "📁" if is_dir else "📄"
        
        if is_dir:
            # Для папок - переход внутрь
            callback = f"file_nav_{bot_id}_{current_path.rstrip('/')}/{f.rstrip('/')}"
            builder.row(
                InlineKeyboardButton(
                    text=f"{icon} {f}",
                    callback_data=callback,
                )
            )
        else:
            # Для файлов - кнопки скачать и удалить
            file_path = f"{current_path.rstrip('/')}/{f}"
            builder.row(
                InlineKeyboardButton(
                    text=f"{icon} {f}",
                    callback_data=f"file_view_{bot_id}_{file_path}",
                ),
                InlineKeyboardButton(
                    text="⬇️",
                    callback_data=f"file_download_{bot_id}_{file_path}",
                ),
                InlineKeyboardButton(
                    text="🗑",
                    callback_data=f"file_delete_{bot_id}_{file_path}",
                ),
            )

    builder.row(
        InlineKeyboardButton(text="Назад", callback_data=f"bot_settings_{bot_id}"),
    )
    return builder.as_markup()


def get_python_change_keyboard(bot_id: int, current: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"{'✅ ' if current == '3.10' else ''}3.10",
            callback_data=f"set_python_{bot_id}_3.10",
        ),
        InlineKeyboardButton(
            text=f"{'✅ ' if current == '3.11' else ''}3.11",
            callback_data=f"set_python_{bot_id}_3.11",
        ),
        InlineKeyboardButton(
            text=f"{'✅ ' if current == '3.12' else ''}3.12",
            callback_data=f"set_python_{bot_id}_3.12",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data=f"bot_settings_{bot_id}"),
    )
    return builder.as_markup()


def get_entry_change_keyboard(bot_id: int, entry_type: str, entry_point: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"{'✅ ' if entry_type == 'script' else ''}Скрипт",
            callback_data=f"set_entry_{bot_id}_script",
        ),
        InlineKeyboardButton(
            text=f"{'✅ ' if entry_type == 'module' else ''}Модуль",
            callback_data=f"set_entry_{bot_id}_module",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data=f"bot_settings_{bot_id}"),
    )
    return builder.as_markup()


def get_delete_confirm_keyboard(bot_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🗑 Удалить",
            callback_data=f"bot_del_confirm_{bot_id}",
            style="danger",
        ),
        InlineKeyboardButton(
            text="Отмена",
            callback_data=f"bot_view_{bot_id}",
        ),
    )
    return builder.as_markup()


def get_server_select_keyboard(servers: list, tariff: str = "free") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="[ Free-пул слотов ]",
            callback_data="server_pool_info",
        ),
    )

    for s in servers:
        flag = get_flag(s.country)
        free_slots = s.free_slots if tariff == "free" else s.free_slots_premium
        occupied = s.total_slots - free_slots
        total = s.total_slots
        status_icon = "🟢" if free_slots > 0 else "🔴"
        builder.row(
            InlineKeyboardButton(
                text=f"{status_icon} | {flag} {s.name} ({occupied}/{total})",
                callback_data=f"create_server_{s.id}",
            )
        )

    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="create_back"),
    )
    return builder.as_markup()


def get_backups_list_keyboard(bots: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for b in bots:
        builder.row(
            InlineKeyboardButton(
                text=f"☁ {b.name}",
                callback_data=f"backups_bot_{b.id}",
            )
        )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="control_panel"),
    )
    return builder.as_markup()


def get_backups_keyboard(bot_id: int, backups: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for b in backups:
        builder.row(
            InlineKeyboardButton(
                text=f"☁ {b.created_at.strftime('%d.%m %H:%M')}",
                callback_data=f"backup_view_{bot_id}_{b.id}",
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="➕ Создать бэкап",
            callback_data=f"backup_create_{bot_id}",
            style="primary",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="Назад к списку", callback_data="backups_list"),
    )
    return builder.as_markup()


def get_libs_keyboard(bot_id: int, libs: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for lib in libs:
        builder.row(
            InlineKeyboardButton(
                text=f"🗑 {lib}",
                callback_data=f"lib_del_{bot_id}_{lib}",
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="➕ Установить библиотеку",
            callback_data=f"lib_add_{bot_id}",
            style="primary",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="Отмена", callback_data=f"bot_settings_{bot_id}"),
    )
    return builder.as_markup()
