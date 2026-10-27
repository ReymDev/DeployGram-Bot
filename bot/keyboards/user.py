from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.callbacks import encode_path
from bot.utils.formatters import format_bytes
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


def get_bot_list_keyboard(bots: list, page: int = 0, per_page: int = 6) -> InlineKeyboardMarkup:
    """
    Список проектов в карточном стиле - 2 в ряд для лучшей читаемости.
    
    Args:
        bots: список проектов или список кортежей (project, is_coowner)
        page: номер страницы
        per_page: количество на странице
    """
    builder = InlineKeyboardBuilder()
    start = page * per_page
    end = start + per_page
    page_bots = bots[start:end]

    # Группируем по 2 в ряд
    for i in range(0, len(page_bots), 2):
        row_bots = page_bots[i:i+2]
        row_buttons = []
        
        for item in row_bots:
            # Проверяем формат данных - это может быть Project или (Project, is_coowner)
            if isinstance(item, tuple):
                b, is_coowner = item
            else:
                b = item
                is_coowner = False
            
            # Иконка статуса
            if b.status == "running":
                icon = "🟢"
            elif b.status == "error":
                icon = "🔴"
            else:
                icon = "⚫"
            
            # Добавляем тег совладельца
            coowner_tag = " 👥" if is_coowner else ""
            
            row_buttons.append(
                InlineKeyboardButton(
                    text=f"{icon} {b.name[:14]}{coowner_tag}",
                    style="primary",
                    callback_data=f"bot_view_{b.id}",
                )
            )
        
        builder.row(*row_buttons)

    # Навигация
    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data=f"bots_page_{page - 1}")
        )
    if end < len(bots):
        nav_row.append(
            InlineKeyboardButton(style="primary", text="Вперёд ➡️", callback_data=f"bots_page_{page + 1}")
        )
    if nav_row:
        builder.row(*nav_row)

    # Только кнопка создания проекта
    builder.row(
        InlineKeyboardButton(
            text="✨ Создать проект",
            style="success",
            callback_data="create_project",
        ),
    )
    
    # Кнопка "Назад" в главное меню
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data="main_menu"),
    )
    
    return builder.as_markup()


def get_bot_control_keyboard(bot_id: int, status: str) -> InlineKeyboardMarkup:
    """Панель управления проектом с контекстными кнопками."""
    builder = InlineKeyboardBuilder()

    # Основные действия в зависимости от статуса
    if status == "running":
        builder.row(
            InlineKeyboardButton(
                text="⏹ Остановить",
                style="danger",
                callback_data=f"bot_stop_{bot_id}",
            ),
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="▶️ Запустить",
                style="success",
                callback_data=f"bot_start_{bot_id}",
            ),
        )

    # Информация и мониторинг
    builder.row(
        InlineKeyboardButton(
            text="📜 Логи",
            style="primary",
            callback_data=f"bot_logs_{bot_id}",
        ),
        InlineKeyboardButton(
            text="📊 Мониторинг",
            style="primary",
            callback_data=f"bot_graphs_{bot_id}",
        ),
    )

    # Управление файлами и настройками
    builder.row(
        InlineKeyboardButton(
            text="📂 Файлы",
            style="primary",
            callback_data=f"bot_files_{bot_id}",
        ),
        InlineKeyboardButton(
            text="⚙️ Настройки",
            style="primary",
            callback_data=f"bot_settings_{bot_id}",
        ),
    )

    # Навигация
    builder.row(
        InlineKeyboardButton(style="primary", text="⬅️ К проектам", callback_data="control_panel"),
    )
    return builder.as_markup()


def get_bot_settings_keyboard(bot_id: int) -> InlineKeyboardMarkup:
    """Меню настроек проекта."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✏️ Переименовать", style="primary", callback_data=f"bot_rename_{bot_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="🐍 Python", style="primary", callback_data=f"bot_python_{bot_id}"),
        InlineKeyboardButton(text="🚀 Точка входа", style="primary", callback_data=f"bot_entry_{bot_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="📦 Зависимости", style="primary", callback_data=f"bot_libs_{bot_id}"),
        InlineKeyboardButton(text="🔔 Уведомления", style="primary", callback_data=f"bot_notify_{bot_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="👥 Совладельцы", style="primary", callback_data=f"bot_coowners_{bot_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="🗑 Удалить проект", style="danger", callback_data=f"bot_delete_{bot_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ К проекту", style="primary", callback_data=f"bot_view_{bot_id}"),
    )
    return builder.as_markup()


def get_logs_keyboard(bot_id: int) -> InlineKeyboardMarkup:
    """Действия с логами."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="🔄 Обновить",
            style="primary",
            callback_data=f"bot_logs_{bot_id}",
        ),
        InlineKeyboardButton(
            style="primary",
            text="⬇️ Скачать",
            callback_data=f"logs_file_{bot_id}",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ К проекту",
            style="primary",
            callback_data=f"bot_view_{bot_id}",
        ),
    )
    return builder.as_markup()


def get_subscription_keyboard(is_premium: bool) -> InlineKeyboardMarkup:
    """Клавиатура меню подписки."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="❓ Что даёт Premium?",
            style="primary",
            callback_data="subscription_info",
        ),
    )
    
    if not is_premium:
        builder.row(
            InlineKeyboardButton(
                text="💳 Купить подписку",
                style="success",
                callback_data="subscription_buy",
            ),
        )
    
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data="main_menu"),
    )
    return builder.as_markup()


def get_buy_subscription_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора периода подписки."""
    from bot.config import settings
    builder = InlineKeyboardBuilder()
    
    # 1 неделя - пробный период
    builder.row(
        InlineKeyboardButton(
            text=f"🎁 1 неделя · {settings.PREMIUM_PRICE_1W}₽ · пробная",
            style="success",
            callback_data="buy_1_week"
        )
    )
    
    # 1 месяц
    builder.row(
        InlineKeyboardButton(
            text=f"📅 1 месяц · {settings.PREMIUM_PRICE_1M}₽",
            style="primary",
            callback_data="buy_1_month"
        )
    )
    
    # 3 месяца с экономией
    builder.row(
        InlineKeyboardButton(
            text=f"💰 3 месяца · {settings.PREMIUM_PRICE_3M}₽ · −10%",
            style="success",
            callback_data="buy_3_months"
        )
    )
    
    # 6 месяцев с экономией
    builder.row(
        InlineKeyboardButton(
            text=f"💰 6 месяцев · {settings.PREMIUM_PRICE_6M}₽ · −15%",
            style="success",
            callback_data="buy_6_months"
        )
    )
    
    # 12 месяцев - лучшее предложение
    builder.row(
        InlineKeyboardButton(
            text=f"🔥 1 год · {settings.PREMIUM_PRICE_12M}₽ · −20%",
            style="success",
            callback_data="buy_12_months"
        )
    )
    
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data="subscription")
    )
    return builder.as_markup()


def get_source_keyboard() -> InlineKeyboardMarkup:
    """Выбор метода загрузки кода."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📦 ZIP-архив",
            style="success",
            callback_data="create_type_zip",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🔗 GitHub-репозиторий",
            style="primary",
            callback_data="create_type_github",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="✖️ Отмена", style="primary", callback_data="control_panel"),
    )
    return builder.as_markup()


def get_create_project_step1_keyboard() -> InlineKeyboardMarkup:
    """Шаг 1: выбор источника кода (алиас для get_source_keyboard)."""
    return get_source_keyboard()


def get_entry_type_keyboard() -> InlineKeyboardMarkup:
    """Выбор типа точки входа."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            style="primary",
            text="📄 Скрипт · python file.py",
            callback_data="create_entry_script",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            style="primary",
            text="📦 Модуль · python -m",
            callback_data="create_entry_module",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data="create_project"),
    )
    return builder.as_markup()


def get_confirm_start_keyboard() -> InlineKeyboardMarkup:
    """Подтверждение создания проекта."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(style="success", text="✅ Создать", callback_data="create_confirm"),
        InlineKeyboardButton(text="❌ Отмена", style="primary", callback_data="main_menu"),
    )
    return builder.as_markup()


def get_project_manage_keyboard(project_id: int, status: str) -> InlineKeyboardMarkup:
    """Клавиатура управления проектом (после создания)."""
    return get_bot_control_keyboard(project_id, status)


def get_python_version_keyboard(step: str = "", current: str = "") -> InlineKeyboardMarkup:
    """Выбор версии Python с рекомендацией."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            style="success",
            text="🔥 Python 3.12 · рекомендуем",
            callback_data="create_python_3.12",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            style="primary",
            text="🐍 Python 3.11",
            callback_data="create_python_3.11",
        ),
        InlineKeyboardButton(
            style="primary",
            text="🐍 Python 3.10",
            callback_data="create_python_3.10",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data="create_back"),
    )
    return builder.as_markup()


def get_entry_mode_keyboard() -> InlineKeyboardMarkup:
    """Выбор метода указания точки входа."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            style="primary",
            text="🪄 Определить автоматически",
            callback_data="create_entry_auto",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            style="primary",
            text="📄 Один файл",
            callback_data="create_entry_script",
        ),
        InlineKeyboardButton(
            style="primary",
            text="📦 Python-модуль",
            callback_data="create_entry_module",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data="create_back"),
    )
    return builder.as_markup()


def get_confirm_entry_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            style="primary",
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
    """Старая версия файлового браузера - оставлена для совместимости."""
    builder = InlineKeyboardBuilder()

    # Кнопка "Назад" если не в корне
    if current_path != "/app" and current_path != "/":
        parent = "/".join(current_path.rstrip("/").split("/")[:-1]) or "/app"
        builder.row(
            InlineKeyboardButton(
                style="primary",
                text="📁 ..",
                callback_data=f"file_nav_{bot_id}_{parent}",
            )
        )

    # Показываем папки и файлы (до 10)
    for f in files[:10]:
        is_dir = "/" in f or f.endswith("/") or "." not in f
        
        if is_dir:
            # Папки
            icon = "📁"
            callback = f"file_nav_{bot_id}_{current_path.rstrip('/')}/{f.rstrip('/')}"
            builder.row(
                InlineKeyboardButton(
                    style="primary",
                    text=f"{icon} {f[:30]}",
                    callback_data=callback,
                )
            )
        else:
            # Файлы с определением типа
            if f.endswith(".py"):
                icon = "🐍"
            elif f.endswith((".txt", ".md")):
                icon = "📄"
            elif f.endswith((".json", ".yaml", ".yml")):
                icon = "⚙️"
            elif f.endswith((".zip", ".tar", ".gz")):
                icon = "📦"
            else:
                icon = "📄"
            
            file_path = f"{current_path.rstrip('/')}/{f}"
            builder.row(
                InlineKeyboardButton(
                    style="primary",
                    text=f"{icon} {f[:25]}",
                    callback_data=f"file_view_{bot_id}_{file_path}",
                ),
                InlineKeyboardButton(
                    style="primary",
                    text="💾",
                    callback_data=f"file_download_{bot_id}_{file_path}",
                ),
                InlineKeyboardButton(
                    style="danger",
                    text="🗑️",
                    callback_data=f"file_delete_{bot_id}_{file_path}",
                ),
            )

    # Действия
    builder.row(
        InlineKeyboardButton(style="success", text="➕ Загрузить файл", callback_data=f"file_upload_{bot_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ К проекту", style="primary", callback_data=f"bot_view_{bot_id}"),
    )
    return builder.as_markup()


def get_files_main_menu_keyboard(project_id: int) -> InlineKeyboardMarkup:
    """Главное меню файлового менеджера."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📂 Просмотр",
            style="primary",
            callback_data=f"files_browse_{project_id}",
        ),
        InlineKeyboardButton(
            text="📤 Загрузка",
            style="success",
            callback_data=f"files_upload_{project_id}",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            style="primary",
            text="⬅️ К проекту",
            callback_data=f"bot_view_{project_id}",
        ),
    )
    return builder.as_markup()


def get_file_browser_keyboard(
    project_id: int, files: list[str], current_path: str
) -> InlineKeyboardMarkup:
    """Браузер файлов в режиме просмотра."""
    builder = InlineKeyboardBuilder()

    # Кнопка вверх если не в корне
    if current_path != "/app":
        parent = "/".join(current_path.rstrip("/").split("/")[:-1]) or "/app"
        builder.row(
            InlineKeyboardButton(
                style="primary",
                text="⬆️ Наверх",
                callback_data=f"fbrowse_nav_{project_id}_{encode_path(parent)}",
            )
        )

    # Показываем папки и файлы
    for f in files[:15]:
        # Папки имеют / в конце (благодаря ls -1p)
        is_dir = f.endswith("/")
        
        if is_dir:
            # Папки - открываются по клику
            folder_name = f.rstrip("/")
            icon = "📁"
            folder_path = f"{current_path.rstrip('/')}/{folder_name}"
            callback = f"fbrowse_nav_{project_id}_{encode_path(folder_path)}"
            builder.row(
                InlineKeyboardButton(
                    style="primary",
                    text=f"{icon} {folder_name[:35]}",
                    callback_data=callback,
                )
            )
        else:
            # Файлы - открывают меню действий
            if f.endswith(".py"):
                icon = "🐍"
            elif f.endswith((".txt", ".md", ".log")):
                icon = "📄"
            elif f.endswith((".json", ".yaml", ".yml", ".toml")):
                icon = "⚙️"
            elif f.endswith((".zip", ".tar", ".gz")):
                icon = "📦"
            elif f.endswith((".jpg", ".png", ".gif")):
                icon = "🖼️"
            else:
                icon = "📄"
            
            file_path = f"{current_path.rstrip('/')}/{f}"
            builder.row(
                InlineKeyboardButton(
                    style="primary",
                    text=f"{icon} {f[:35]}",
                    callback_data=f"file_action_{project_id}_{encode_path(file_path)}",
                )
            )

    # Кнопки навигации
    builder.row(
        InlineKeyboardButton(
            text="⬅️ К файлам",
            style="primary",
            callback_data=f"bot_files_{project_id}",
        ),
    )
    return builder.as_markup()


def get_file_upload_browser_keyboard(
    project_id: int, files: list[str], current_path: str
) -> InlineKeyboardMarkup:
    """Браузер файлов в режиме загрузки."""
    builder = InlineKeyboardBuilder()

    # Кнопка загрузки в текущую директорию
    builder.row(
        InlineKeyboardButton(
            text="📤 Загрузить в эту папку",
            style="success",
            callback_data=f"upload_here_{project_id}_{encode_path(current_path)}",
        )
    )

    # Кнопка вверх если не в корне
    if current_path != "/app":
        parent = "/".join(current_path.rstrip("/").split("/")[:-1]) or "/app"
        builder.row(
            InlineKeyboardButton(
                style="primary",
                text="⬆️ Наверх",
                callback_data=f"fupload_nav_{project_id}_{encode_path(parent)}",
            )
        )

    # Показываем только папки
    for f in files[:15]:
        # Папки имеют / в конце (благодаря ls -1p)
        is_dir = f.endswith("/")
        
        if is_dir:
            folder_name = f.rstrip("/")
            folder_path = f"{current_path.rstrip('/')}/{folder_name}"
            callback = f"fupload_nav_{project_id}_{encode_path(folder_path)}"
            builder.row(
                InlineKeyboardButton(
                    style="primary",
                    text=f"📁 {folder_name[:35]}",
                    callback_data=callback,
                )
            )

    # Кнопки навигации
    builder.row(
        InlineKeyboardButton(
            text="⬅️ К файлам",
            style="primary",
            callback_data=f"bot_files_{project_id}",
        ),
    )
    return builder.as_markup()


def get_file_action_keyboard(project_id: int, file_path: str) -> InlineKeyboardMarkup:
    """Меню действий с файлом."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="⬇️ Скачать",
            style="primary",
            callback_data=f"file_download_{project_id}_{encode_path(file_path)}",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🗑️ Удалить",
            style="danger",
            callback_data=f"file_delete_{project_id}_{encode_path(file_path)}",
        ),
    )
    
    # Кнопка назад - возврат в браузер в ту же папку
    parent = "/".join(file_path.rstrip("/").split("/")[:-1]) or "/app"
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            style="primary",
            callback_data=f"fbrowse_nav_{project_id}_{encode_path(parent)}",
        ),
    )
    return builder.as_markup()


def get_python_change_keyboard(bot_id: int, current: str) -> InlineKeyboardMarkup:
    """Выбор версии Python с текущей отмеченной."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=f"{'🔥 ' if current == '3.12' else ''}Python 3.12{' (текущая)' if current == '3.12' else ''}",
            style="primary",
            callback_data=f"set_python_{bot_id}_3.12",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=f"{'✓ ' if current == '3.11' else ''}Python 3.11{' (текущая)' if current == '3.11' else ''}",
            style="primary",
            callback_data=f"set_python_{bot_id}_3.11",
        ),
        InlineKeyboardButton(
            text=f"{'✓ ' if current == '3.10' else ''}Python 3.10{' (текущая)' if current == '3.10' else ''}",
            style="primary",
            callback_data=f"set_python_{bot_id}_3.10",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data=f"bot_settings_{bot_id}"),
    )
    return builder.as_markup()


def get_entry_change_keyboard(bot_id: int, entry_type: str, entry_point: str) -> InlineKeyboardMarkup:
    """Меню изменения точки входа."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=f"📄 Скрипт{'  ✓' if entry_type == 'script' else ''}",
            style="primary",
            callback_data=f"set_entry_{bot_id}_script",
        ),
        InlineKeyboardButton(
            text=f"📦 Модуль{'  ✓' if entry_type == 'module' else ''}",
            style="primary",
            callback_data=f"set_entry_{bot_id}_module",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data=f"bot_settings_{bot_id}"),
    )
    return builder.as_markup()


def get_delete_confirm_keyboard(bot_id: int) -> InlineKeyboardMarkup:
    """Подтверждение удаления проекта."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="✅ Да, удалить",
            style="danger",
            callback_data=f"bot_del_confirm_{bot_id}",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="❌ Отмена",
            style="primary",
            callback_data=f"bot_view_{bot_id}",
        ),
    )
    return builder.as_markup()


def get_server_select_keyboard(servers: list, tariff: str = "free") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            style="primary",
            text="ℹ️ Свободные слоты",
            callback_data="server_pool_info",
        ),
    )

    for s in servers:
        flag = get_flag(s.country)
        free_slots = s.free_slots if tariff == "free" else s.free_slots_premium
        total = s.total_slots
        status_icon = "🟢" if free_slots > 0 else "🔴"
        builder.row(
            InlineKeyboardButton(
                style=("success" if free_slots > 0 else "primary"),
                text=f"{status_icon} {flag} {s.name} · {free_slots}/{total}",
                callback_data=f"create_server_{s.id}",
            )
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data="create_back"),
    )
    return builder.as_markup()


def get_backups_list_keyboard(bots: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for b in bots:
        builder.row(
            InlineKeyboardButton(
                text=f"☁️ {b.name}",
                style="primary",
                callback_data=f"backups_bot_{b.id}",
            )
        )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data="main_menu"),
    )
    return builder.as_markup()


def get_backups_keyboard(bot_id: int, backups: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for b in backups:
        builder.row(
            InlineKeyboardButton(
                text=f"🕓 {b.created_at.strftime('%d.%m · %H:%M')} · {format_bytes(b.size)}",
                style="primary",
                callback_data=f"backup_view_{bot_id}_{b.id}",
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="💾 Создать бэкап",
            callback_data=f"backup_create_{bot_id}",
            style="success",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ К списку", style="primary", callback_data="backups_list"),
    )
    return builder.as_markup()


def get_libs_keyboard(bot_id: int, libs: list[str]) -> InlineKeyboardMarkup:
    """Список установленных библиотек."""
    builder = InlineKeyboardBuilder()

    # Показываем до 10 библиотек
    for lib in libs[:10]:
        builder.row(
            InlineKeyboardButton(
                style="default",
                text=f"📦 {lib}",
                callback_data="noop",
            ),
            InlineKeyboardButton(
                text="🗑️",
                style="danger",
                callback_data=f"lib_del_{bot_id}_{encode_path(lib)}",
            ),
        )

    builder.row(
        InlineKeyboardButton(
            text="➕ Установить библиотеку",
            style="success",
            callback_data=f"lib_add_{bot_id}",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data=f"bot_settings_{bot_id}"),
    )
    return builder.as_markup()


def get_settings_keyboard(
    notify_container_stopped: bool,
    notify_container_started: bool,
    notify_error: bool,
    notify_high_cpu: bool,
    notify_high_ram: bool,
    notify_low_disk: bool,
    notify_backup_created: bool,
    notify_update_done: bool,
    project_id: int = 0,
) -> InlineKeyboardMarkup:
    """Клавиатура настроек уведомлений пользователя."""
    builder = InlineKeyboardBuilder()
    
    def toggle_icon(enabled: bool) -> str:
        return "🔔" if enabled else "🔕"
    
    builder.row(
        InlineKeyboardButton(
            style=("success" if notify_container_stopped else "primary"),
            text=f"{toggle_icon(notify_container_stopped)} Стоп",
            callback_data=(f"toggle_{project_id}_notify_container_stopped" if project_id else "toggle_notify_container_stopped"),
        ),
        InlineKeyboardButton(
            style=("success" if notify_container_started else "primary"),
            text=f"{toggle_icon(notify_container_started)} Старт",
            callback_data=(f"toggle_{project_id}_notify_container_started" if project_id else "toggle_notify_container_started"),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            style=("success" if notify_error else "primary"),
            text=f"{toggle_icon(notify_error)} Ошибки",
            callback_data=(f"toggle_{project_id}_notify_error" if project_id else "toggle_notify_error"),
        ),
        InlineKeyboardButton(
            style=("success" if notify_update_done else "primary"),
            text=f"{toggle_icon(notify_update_done)} Обновления",
            callback_data=(f"toggle_{project_id}_notify_update_done" if project_id else "toggle_notify_update_done"),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            style=("success" if notify_high_cpu else "primary"),
            text=f"{toggle_icon(notify_high_cpu)} CPU",
            callback_data=(f"toggle_{project_id}_notify_high_cpu" if project_id else "toggle_notify_high_cpu"),
        ),
        InlineKeyboardButton(
            style=("success" if notify_high_ram else "primary"),
            text=f"{toggle_icon(notify_high_ram)} RAM",
            callback_data=(f"toggle_{project_id}_notify_high_ram" if project_id else "toggle_notify_high_ram"),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            style=("success" if notify_low_disk else "primary"),
            text=f"{toggle_icon(notify_low_disk)} Диск",
            callback_data=(f"toggle_{project_id}_notify_low_disk" if project_id else "toggle_notify_low_disk"),
        ),
        InlineKeyboardButton(
            style=("success" if notify_backup_created else "primary"),
            text=f"{toggle_icon(notify_backup_created)} Бэкапы",
            callback_data=(f"toggle_{project_id}_notify_backup_created" if project_id else "toggle_notify_backup_created"),
        ),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data="profile"),
    )
    return builder.as_markup()


def get_coowners_keyboard(project_id: int, coowners: list) -> InlineKeyboardMarkup:
    """Клавиатура управления совладельцами проекта."""
    builder = InlineKeyboardBuilder()
    
    for co in coowners:
        builder.row(
            InlineKeyboardButton(
                text=f"👤 ID:{co.user_id} ({co.role})",
                style="primary",
                callback_data=f"coowner_edit_{project_id}_{co.id}",
            ),
            InlineKeyboardButton(
                text="🗑️",
                style="danger",
                callback_data=f"coowner_remove_{project_id}_{co.id}",
            ),
        )
    
    builder.row(
        InlineKeyboardButton(
            text="➕ Добавить совладельца",
            style="success",
            callback_data=f"coowner_add_{project_id}",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data=f"bot_settings_{project_id}"),
    )
    return builder.as_markup()


def get_coowner_permissions_keyboard(project_id: int, coowner_id: int, coowner) -> InlineKeyboardMarkup:
    """Клавиатура настройки разрешений совладельца."""
    builder = InlineKeyboardBuilder()
    
    def perm_icon(enabled: bool) -> str:
        return "✅" if enabled else "❌"
    
    builder.row(
        InlineKeyboardButton(
            text=f"{perm_icon(coowner.can_start_stop)} ▶️ Запуск и остановка",
            style=("success" if coowner.can_start_stop else "primary"),
            callback_data=f"coowner_perm_{project_id}_{coowner_id}_can_start_stop",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=f"{perm_icon(coowner.can_view_logs)} 📜 Просмотр логов",
            style=("success" if coowner.can_view_logs else "primary"),
            callback_data=f"coowner_perm_{project_id}_{coowner_id}_can_view_logs",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=f"{perm_icon(coowner.can_edit_files)} 📂 Редактирование файлов",
            style=("success" if coowner.can_edit_files else "primary"),
            callback_data=f"coowner_perm_{project_id}_{coowner_id}_can_edit_files",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=f"{perm_icon(coowner.can_manage_deps)} 📦 Зависимости",
            style=("success" if coowner.can_manage_deps else "primary"),
            callback_data=f"coowner_perm_{project_id}_{coowner_id}_can_manage_deps",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=f"{perm_icon(coowner.can_view_settings)} ⚙️ Настройки",
            style=("success" if coowner.can_view_settings else "primary"),
            callback_data=f"coowner_perm_{project_id}_{coowner_id}_can_view_settings",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ К совладельцам", style="primary", callback_data=f"bot_coowners_{project_id}"),
    )
    return builder.as_markup()
