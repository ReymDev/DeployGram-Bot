from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.emojis import EmojiID


def get_project_list_keyboard(projects: list, page: int = 0, per_page: int = 5) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start = page * per_page
    end = start + per_page
    page_projects = projects[start:end]

    for p in page_projects:
        status_icon = "🟢" if p.status == "running" else "🔴"
        builder.row(
            InlineKeyboardButton(
                text=f"{status_icon} {p.name}",
                callback_data=f"project_view_{p.id}",
            )
        )

    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(text="◁ Назад", callback_data=f"projects_page_{page - 1}")
        )
    if end < len(projects):
        nav_row.append(
            InlineKeyboardButton(text="Вперёд ▷", callback_data=f"projects_page_{page + 1}")
        )
    if nav_row:
        builder.row(*nav_row)

    builder.row(
        InlineKeyboardButton(
            text="➕ Создать",
            callback_data="create_project",
            style="primary",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Меню", callback_data="main_menu"),
    )
    return builder.as_markup()


def get_project_manage_keyboard(project_id: int, status: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if status == "running":
        builder.row(
            InlineKeyboardButton(
                text="⏹ Остановить",
                callback_data=f"project_stop_{project_id}",
                style="danger",
            ),
            InlineKeyboardButton(
                text="🔄 Рестарт",
                callback_data=f"project_restart_{project_id}",
                style="primary",
            ),
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="▶ Запустить",
                callback_data=f"project_start_{project_id}",
                style="success",
            ),
        )

    builder.row(
        InlineKeyboardButton(
            text="📊 Мониторинг",
            callback_data=f"project_monitor_{project_id}",
            icon_custom_emoji_id=EmojiID.GRAPH_STATS,
            style="default",
        ),
        InlineKeyboardButton(
            text="📋 Логи",
            callback_data=f"project_logs_{project_id}",
            icon_custom_emoji_id=EmojiID.EYE,
            style="default",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="📁 Файлы",
            callback_data=f"project_files_{project_id}",
            icon_custom_emoji_id=EmojiID.FILE,
            style="default",
        ),
        InlineKeyboardButton(
            text="🖋 Редактор",
            callback_data=f"project_editor_{project_id}",
            icon_custom_emoji_id=EmojiID.PENCIL,
            style="default",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🔒 Секреты",
            callback_data=f"project_secrets_{project_id}",
            icon_custom_emoji_id=EmojiID.LOCK,
            style="default",
        ),
        InlineKeyboardButton(
            text="💾 Бэкапы",
            callback_data=f"project_backups_{project_id}",
            icon_custom_emoji_id=EmojiID.BACKUP,
            style="default",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="👥 Совладельцы",
            callback_data=f"project_coowners_{project_id}",
            icon_custom_emoji_id=EmojiID.PEOPLE,
            style="default",
        ),
        InlineKeyboardButton(
            text="📜 Версии",
            callback_data=f"project_versions_{project_id}",
            icon_custom_emoji_id=EmojiID.CALENDAR,
            style="default",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="⚙ Настройки",
            callback_data=f"project_settings_{project_id}",
            icon_custom_emoji_id=EmojiID.SETTINGS,
            style="default",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🗑 Удалить",
            callback_data=f"project_delete_{project_id}",
            style="danger",
            icon_custom_emoji_id=EmojiID.TRASH,
        ),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data="my_projects"),
    )
    return builder.as_markup()


def get_create_project_step1_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📁 ZIP архив",
            callback_data="create_type_zip",
            icon_custom_emoji_id=EmojiID.FILE,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🔗 GitHub",
            callback_data="create_type_github",
            icon_custom_emoji_id=EmojiID.LINK,
        ),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data="main_menu"),
    )
    return builder.as_markup()


def get_python_version_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ver in ("3.10", "3.11", "3.12"):
        builder.row(
            InlineKeyboardButton(
                text=f"Python {ver}",
                callback_data=f"create_python_{ver}",
                style="default",
                icon_custom_emoji_id=EmojiID.CODE,
            )
        )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data="create_project"),
    )
    return builder.as_markup()


def get_entry_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📄 Скрипт (main.py)",
            callback_data="create_entry_script",
            style="default",
            icon_custom_emoji_id=EmojiID.FILE,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="📦 Модуль (-m)",
            callback_data="create_entry_module",
            style="default",
            icon_custom_emoji_id=EmojiID.BOX,
        ),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data="create_project"),
    )
    return builder.as_markup()


def get_server_select_keyboard(servers: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for s in servers:
        builder.row(
            InlineKeyboardButton(
                text=f"🌍 {s.name} ({s.country}) — {s.free_slots} слотов",
                callback_data=f"create_server_{s.id}",
                icon_custom_emoji_id=EmojiID.EARTH,
            )
        )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data="create_project"),
    )
    return builder.as_markup()


def get_settings_keyboard(
    notify_stopped: bool,
    notify_started: bool,
    notify_error: bool,
    notify_high_cpu: bool,
    notify_high_ram: bool,
    notify_low_disk: bool,
    notify_backup: bool,
    notify_update: bool,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    def _icon(val: bool) -> str:
        return "✅" if val else "❌"

    items = [
        ("notify_container_stopped", "Контейнер остановлен", notify_stopped),
        ("notify_container_started", "Контейнер запущен", notify_started),
        ("notify_error", "Ошибка запуска", notify_error),
        ("notify_high_cpu", "Высокая нагрузка CPU", notify_high_cpu),
        ("notify_high_ram", "Высокая нагрузка RAM", notify_high_ram),
        ("notify_low_disk", "Мало места на диске", notify_low_disk),
        ("notify_backup_created", "Бэкап создан", notify_backup),
        ("notify_update_done", "Обновление завершено", notify_update),
    ]

    for data, label, val in items:
        icon_id = EmojiID.CHECK if val else EmojiID.CROSS
        builder.row(
            InlineKeyboardButton(
                text=f"{_icon(val)} {label}",
                callback_data=f"toggle_{data}",
                icon_custom_emoji_id=icon_id,
            )
        )

    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data="profile"),
    )
    return builder.as_markup()


def get_confirm_start_keyboard(project_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Запустить",
            callback_data=f"project_confirm_start_{project_id}",
            style="success",
            icon_custom_emoji_id=EmojiID.CHECK,
        ),
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data=f"project_view_{project_id}",
            style="danger",
            icon_custom_emoji_id=EmojiID.CROSS,
        ),
    )
    return builder.as_markup()


def get_logs_keyboard(project_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="👁 Последние 3500 символов",
            callback_data=f"logs_view_{project_id}",
            icon_custom_emoji_id=EmojiID.EYE,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="⬇ Скачать лог",
            callback_data=f"logs_download_{project_id}",
            icon_custom_emoji_id=EmojiID.DOWNLOAD,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🗑 Очистить",
            callback_data=f"logs_clear_{project_id}",
            style="danger",
            icon_custom_emoji_id=EmojiID.TRASH,
        ),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data=f"project_view_{project_id}"),
    )
    return builder.as_markup()


def get_versions_keyboard(project_id: int, versions: list, page: int = 0, per_page: int = 5) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start = page * per_page
    end = start + per_page
    page_versions = versions[start:end]

    for v in page_versions:
        builder.row(
            InlineKeyboardButton(
                text=f"v{v.version_number} — {v.created_at.strftime('%d.%m %H:%M')}",
                callback_data=f"version_view_{project_id}_{v.id}",
                icon_custom_emoji_id=EmojiID.CALENDAR,
            )
        )

    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(text="◁", callback_data=f"versions_page_{project_id}_{page - 1}")
        )
    if end < len(versions):
        nav_row.append(
            InlineKeyboardButton(text="▷", callback_data=f"versions_page_{project_id}_{page + 1}")
        )
    if nav_row:
        builder.row(*nav_row)

    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data=f"project_view_{project_id}"),
    )
    return builder.as_markup()


def get_coowners_keyboard(project_id: int, coowners: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for co in coowners:
        builder.row(
            InlineKeyboardButton(
                text=f"👤 ID:{co.user_id} ({co.role})",
                callback_data=f"coowner_view_{project_id}_{co.id}",
                icon_custom_emoji_id=EmojiID.PEOPLE,
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="➕ Добавить",
            callback_data=f"coowner_add_{project_id}",
            style="primary",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data=f"project_view_{project_id}"),
    )
    return builder.as_markup()


def get_backups_keyboard(project_id: int, backups: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for b in backups:
        builder.row(
            InlineKeyboardButton(
                text=f"💾 {b.created_at.strftime('%d.%m %H:%M')}",
                callback_data=f"backup_view_{project_id}_{b.id}",
                icon_custom_emoji_id=EmojiID.BACKUP,
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="➕ Создать бэкап",
            callback_data=f"backup_create_{project_id}",
            style="primary",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data=f"project_view_{project_id}"),
    )
    return builder.as_markup()


def get_secrets_keyboard(project_id: int, secrets: dict[str, str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for key, val in secrets.items():
        hidden = val[:3] + "****" if len(val) > 3 else "****"
        builder.row(
            InlineKeyboardButton(
                text=f"🔒 {key} = {hidden}",
                callback_data=f"secret_view_{project_id}_{key}",
                icon_custom_emoji_id=EmojiID.LOCK,
            ),
            InlineKeyboardButton(
                text="🗑",
                callback_data=f"secret_del_{project_id}_{key}",
                style="danger",
            ),
        )

    builder.row(
        InlineKeyboardButton(
            text="➕ Добавить секрет",
            callback_data=f"secret_add_{project_id}",
            style="primary",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data=f"project_view_{project_id}"),
    )
    return builder.as_markup()


def get_file_manager_keyboard(
    project_id: int, files: list[str], current_path: str
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if current_path != "/":
        parent = "/".join(current_path.strip("/").split("/")[:-1]) or "/"
        builder.row(
            InlineKeyboardButton(
                text="◁ Назад",
                callback_data=f"file_nav_{project_id}_{parent}",
            )
        )

    for f in files:
        is_dir = "/" in f or f.endswith("/")
        icon = "📁" if is_dir else "📄"
        emoji_id = EmojiID.FILE
        callback = f"file_nav_{project_id}_{current_path}/{f}" if is_dir else f"file_view_{project_id}_{current_path}/{f}"
        builder.row(
            InlineKeyboardButton(
                text=f"{icon} {f}",
                callback_data=callback,
                icon_custom_emoji_id=emoji_id,
            ),
        )

    builder.row(
        InlineKeyboardButton(
            text="➕ Создать",
            callback_data=f"file_create_{project_id}_{current_path}",
            style="primary",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Меню проекта", callback_data=f"project_view_{project_id}"),
    )
    return builder.as_markup()


def get_file_action_keyboard(project_id: int, file_path: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🖋 Редактировать",
            callback_data=f"file_edit_{project_id}_{file_path}",
            icon_custom_emoji_id=EmojiID.PENCIL,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="⬇ Скачать",
            callback_data=f"file_download_{project_id}_{file_path}",
            icon_custom_emoji_id=EmojiID.DOWNLOAD,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🗑 Удалить",
            callback_data=f"file_delete_{project_id}_{file_path}",
            style="danger",
            icon_custom_emoji_id=EmojiID.TRASH,
        ),
    )
    parent = "/".join(file_path.strip("/").split("/")[:-1]) or "/"
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data=f"file_nav_{project_id}_{parent}"),
    )
    return builder.as_markup()
