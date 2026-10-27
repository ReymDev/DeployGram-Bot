"""
🎹 НОВАЯ СИСТЕМА КЛАВИАТУР DeployGram v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

КОНЦЕПЦИЯ: Минимализм, понятные иконки, логичная группировка
СТРУКТУРА: Карточные кнопки, визуальное разделение, интуитивность
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ═══════════════════════════════════════════════════════════════
# 🏠 ГЛАВНОЕ МЕНЮ
# ═══════════════════════════════════════════════════════════════

def home_menu(has_projects: bool = False) -> InlineKeyboardMarkup:
    """
    Главное меню - 2 режима в зависимости от наличия проектов.
    """
    builder = InlineKeyboardBuilder()
    
    if has_projects:
        # Для пользователей с проектами - быстрый доступ
        builder.row(
            InlineKeyboardButton(style="primary", text="📱 Мои проекты", callback_data="my_projects")
        )
        builder.row(
            InlineKeyboardButton(text="✨ Создать проект", style="success", callback_data="create_new")
        )
    else:
        # Для новых пользователей - призыв к действию
        builder.row(
            InlineKeyboardButton(style="primary", text="🚀 Создать первый проект", callback_data="create_first")
        )
        builder.row(
            InlineKeyboardButton(style="primary", text="📖 Как это работает?", callback_data="help_quick_start")
        )
    
    # Общие кнопки
    builder.row(
        InlineKeyboardButton(style="primary", text="💳 Подписка", callback_data="subscription"),
        InlineKeyboardButton(style="primary", text="📖 Помощь", callback_data="help_menu")
    )
    
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
# 📱 МОИ ПРОЕКТЫ
# ═══════════════════════════════════════════════════════════════

def projects_list(projects: list, page: int = 0, items_per_page: int = 6) -> InlineKeyboardMarkup:
    """
    Список проектов с карточным отображением.
    Группировка: 2 проекта в строке для лучшей читаемости.
    """
    builder = InlineKeyboardBuilder()
    
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    page_projects = projects[start_idx:end_idx]
    
    # Группируем по 2 в строке
    for i in range(0, len(page_projects), 2):
        row_projects = page_projects[i:i+2]
        
        row_buttons = []
        for proj in row_projects:
            # Иконка статуса
            if proj.status == "running":
                icon = "🟢"
            elif proj.status == "error":
                icon = "🔴"
            else:
                icon = "⚫"
            
            row_buttons.append(
                InlineKeyboardButton(
                    text=f"{icon} {proj.name[:12]}",  # Ограничение длины
                    style="primary",
                    callback_data=f"proj:{proj.id}"
                )
            )
        
        builder.row(*row_buttons)
    
    # Навигация
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data=f"projects:page:{page-1}")
        )
    if end_idx < len(projects):
        nav_buttons.append(
            InlineKeyboardButton(style="primary", text="Вперёд ➡️", callback_data=f"projects:page:{page+1}")
        )
    if nav_buttons:
        builder.row(*nav_buttons)
    
    # Действия
    builder.row(
        InlineKeyboardButton(style="primary", text="✨ Новый проект", callback_data="create_new")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="🏠 Главная", callback_data="home")
    )
    
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
# 🎯 УПРАВЛЕНИЕ ПРОЕКТОМ
# ═══════════════════════════════════════════════════════════════

def project_control(project_id: int, status: str, is_owner: bool = True) -> InlineKeyboardMarkup:
    """
    Панель управления проектом с контекстными кнопками.
    """
    builder = InlineKeyboardBuilder()
    
    # Основные действия в зависимости от статуса
    if status == "running":
        builder.row(
            InlineKeyboardButton(style="primary", text="⏸️ Остановить", callback_data=f"proj:{project_id}:stop")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="▶️ Запустить", style="success", callback_data=f"proj:{project_id}:start")
        )
    
    # Информация и мониторинг
    builder.row(
        InlineKeyboardButton(style="primary", text="📋 Логи", callback_data=f"proj:{project_id}:logs"),
        InlineKeyboardButton(style="primary", text="📊 Статистика", callback_data=f"proj:{project_id}:stats")
    )
    
    # Управление файлами и настройками
    builder.row(
        InlineKeyboardButton(style="primary", text="📁 Файлы", callback_data=f"proj:{project_id}:files"),
        InlineKeyboardButton(style="primary", text="⚙️ Настройки", callback_data=f"proj:{project_id}:settings")
    )
    
    # Опасная зона (только для владельца)
    if is_owner:
        builder.row(
            InlineKeyboardButton(style="primary", text="👥 Доступ", callback_data=f"proj:{project_id}:sharing")
        )
        builder.row(
            InlineKeyboardButton(style="primary", text="🗑️ Удалить проект", callback_data=f"proj:{project_id}:delete")
        )
    
    # Навигация
    builder.row(
        InlineKeyboardButton(style="primary", text="⬅️ К проектам", callback_data="my_projects")
    )
    
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
# ✨ СОЗДАНИЕ ПРОЕКТА
# ═══════════════════════════════════════════════════════════════

def create_project_upload_method() -> InlineKeyboardMarkup:
    """
    Выбор метода загрузки кода.
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(style="primary", text="📦 Загрузить ZIP", callback_data="create:upload:zip")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="🔗 Из GitHub", callback_data="create:upload:github")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="🎨 Шаблон проекта", callback_data="create:upload:template")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", style="primary", callback_data="home")
    )
    
    return builder.as_markup()


def python_version_selector() -> InlineKeyboardMarkup:
    """
    Выбор версии Python с рекомендацией.
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(style="primary", text="🔥 Python 3.12 (рекомендуем)", callback_data="create:python:3.12")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="Python 3.11", callback_data="create:python:3.11"),
        InlineKeyboardButton(style="primary", text="Python 3.10", callback_data="create:python:3.10")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data="create:back:upload")
    )
    
    return builder.as_markup()


def entry_point_method() -> InlineKeyboardMarkup:
    """
    Выбор метода указания точки входа.
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(style="primary", text="🎯 Найти автоматически", callback_data="create:entry:auto")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="📝 Указать файл", callback_data="create:entry:manual")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data="create:back:python")
    )
    
    return builder.as_markup()


def entry_point_files(files: list[str], project_id: int = 0) -> InlineKeyboardMarkup:
    """
    Список найденных точек входа.
    """
    builder = InlineKeyboardBuilder()
    
    # Показываем до 8 файлов
    for file in files[:8]:
        builder.row(
            InlineKeyboardButton(style="primary", text=f"📄 {file}", callback_data=f"create:entry:select:{file}")
        )
    
    builder.row(
        InlineKeyboardButton(style="primary", text="✏️ Ввести вручную", callback_data="create:entry:manual")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data="create:back:python")
    )
    
    return builder.as_markup()


def project_ready_actions(project_id: int) -> InlineKeyboardMarkup:
    """
    Финальные действия после создания проекта.
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(style="primary", text="🚀 Запустить сейчас", callback_data=f"proj:{project_id}:start")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="⚙️ Проверить настройки", callback_data=f"proj:{project_id}:settings"),
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="📱 К проектам", callback_data="my_projects")
    )
    
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
# 📁 ФАЙЛОВЫЙ МЕНЕДЖЕР
# ═══════════════════════════════════════════════════════════════

def file_browser(project_id: int, files: list, current_path: str = "/app") -> InlineKeyboardMarkup:
    """
    Браузер файлов с иконками типов.
    """
    builder = InlineKeyboardBuilder()
    
    # Папка назад (если не в корне)
    if current_path != "/app":
        parent_path = "/".join(current_path.rstrip("/").split("/")[:-1]) or "/app"
        builder.row(
            InlineKeyboardButton(style="primary", text="📁 ..", callback_data=f"files:{project_id}:nav:{parent_path}")
        )
    
    # Файлы и папки (показываем до 10)
    for item in files[:10]:
        # Определяем иконку по расширению
        if item.endswith("/"):
            icon = "📁"
            action = "nav"
        elif item.endswith(".py"):
            icon = "🐍"
            action = "view"
        elif item.endswith((".txt", ".md")):
            icon = "📄"
            action = "view"
        elif item.endswith((".json", ".yaml", ".yml")):
            icon = "⚙️"
            action = "view"
        else:
            icon = "📄"
            action = "view"
        
        builder.row(
            InlineKeyboardButton(
                style="primary",
                text=f"{icon} {item[:30]}",
                callback_data=f"files:{project_id}:{action}:{current_path}/{item}"
            )
        )
    
    # Действия
    builder.row(
        InlineKeyboardButton(style="primary", text="➕ Создать файл", callback_data=f"files:{project_id}:create"),
        InlineKeyboardButton(style="primary", text="📤 Загрузить", callback_data=f"files:{project_id}:upload")
    )
    
    builder.row(
        InlineKeyboardButton(style="primary", text="⬅️ К проекту", callback_data=f"proj:{project_id}")
    )
    
    return builder.as_markup()


def file_actions(project_id: int, file_path: str) -> InlineKeyboardMarkup:
    """
    Действия с файлом.
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(style="primary", text="👁️ Просмотр", callback_data=f"files:{project_id}:read:{file_path}")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="✏️ Редактировать", callback_data=f"files:{project_id}:edit:{file_path}"),
        InlineKeyboardButton(style="primary", text="💾 Скачать", callback_data=f"files:{project_id}:download:{file_path}")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="🗑️ Удалить", callback_data=f"files:{project_id}:delete:{file_path}")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data=f"files:{project_id}:back")
    )
    
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
# ⚙️ НАСТРОЙКИ ПРОЕКТА
# ═══════════════════════════════════════════════════════════════

def project_settings_menu(project_id: int) -> InlineKeyboardMarkup:
    """
    Меню настроек проекта.
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(style="primary", text="📝 Переименовать", callback_data=f"settings:{project_id}:rename")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="🐍 Изменить Python", callback_data=f"settings:{project_id}:python"),
        InlineKeyboardButton(style="primary", text="🎯 Точка входа", callback_data=f"settings:{project_id}:entry")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="🔐 Переменные окружения", callback_data=f"settings:{project_id}:env")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="📦 Зависимости", callback_data=f"settings:{project_id}:deps")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="🌍 Сменить сервер", callback_data=f"settings:{project_id}:server")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="⬅️ К проекту", callback_data=f"proj:{project_id}")
    )
    
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
# 📋 ЛОГИ И МОНИТОРИНГ
# ═══════════════════════════════════════════════════════════════

def logs_actions(project_id: int) -> InlineKeyboardMarkup:
    """
    Действия с логами.
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(style="primary", text="🔄 Обновить", callback_data=f"proj:{project_id}:logs:refresh")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="💾 Скачать всё", callback_data=f"proj:{project_id}:logs:download"),
        InlineKeyboardButton(style="primary", text="🗑️ Очистить", callback_data=f"proj:{project_id}:logs:clear")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="⬅️ К проекту", callback_data=f"proj:{project_id}")
    )
    
    return builder.as_markup()


def stats_timerange(project_id: int, current: str = "24h") -> InlineKeyboardMarkup:
    """
    Выбор временного диапазона статистики.
    """
    builder = InlineKeyboardBuilder()
    
    periods = [
        ("1ч", "1h"),
        ("24ч", "24h"),
        ("7д", "7d"),
        ("30д", "30d")
    ]
    
    row_buttons = []
    for label, value in periods:
        if value == current:
            row_buttons.append(
                InlineKeyboardButton(style="primary", text=f"✓ {label}", callback_data="noop")
            )
        else:
            row_buttons.append(
                InlineKeyboardButton(style="primary", text=label, callback_data=f"proj:{project_id}:stats:{value}")
            )
    
    builder.row(*row_buttons)
    builder.row(
        InlineKeyboardButton(style="primary", text="⬅️ К проекту", callback_data=f"proj:{project_id}")
    )
    
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
# 💳 ПОДПИСКА И ПЛАТЕЖИ
# ═══════════════════════════════════════════════════════════════

def subscription_menu() -> InlineKeyboardMarkup:
    """
    Меню управления подпиской.
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(style="primary", text="🎁 Промокод", callback_data="subscription:promo"),
        InlineKeyboardButton(style="primary", text="📜 История", callback_data="subscription:history")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="⬅️ Главная", callback_data="home")
    )
    
    return builder.as_markup()


def premium_purchase() -> InlineKeyboardMarkup:
    """
    Покупка Premium подписки.
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(style="primary", text="💳 Оплатить 299₽/мес", callback_data="pay:premium:monthly")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="🎯 Попробовать неделю бесплатно", callback_data="pay:premium:trial")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", style="primary", callback_data="subscription")
    )
    
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
# 👥 СОВМЕСТНЫЙ ДОСТУП
# ═══════════════════════════════════════════════════════════════

def sharing_menu(project_id: int, coowners: list) -> InlineKeyboardMarkup:
    """
    Управление совладельцами.
    """
    builder = InlineKeyboardBuilder()
    
    # Список совладельцев
    for co in coowners[:5]:  # Показываем до 5
        builder.row(
            InlineKeyboardButton(
                style="primary",
                text=f"👤 {co.username or f'ID{co.user_id}'}",
                callback_data="noop"
            ),
            InlineKeyboardButton(
                style="primary",
                text="🗑️",
                callback_data=f"sharing:{project_id}:remove:{co.id}"
            )
        )
    
    # Добавление
    builder.row(
        InlineKeyboardButton(style="primary", text="➕ Добавить совладельца", callback_data=f"sharing:{project_id}:add")
    )
    
    builder.row(
        InlineKeyboardButton(style="primary", text="⬅️ К проекту", callback_data=f"proj:{project_id}")
    )
    
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
# 📖 ПОМОЩЬ
# ═══════════════════════════════════════════════════════════════

def help_menu() -> InlineKeyboardMarkup:
    """
    Меню помощи.
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(style="primary", text="🚀 Быстрый старт", callback_data="help:quick_start")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="❓ Частые вопросы", callback_data="help:faq"),
        InlineKeyboardButton(style="primary", text="📖 Документация", callback_data="help:docs")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="💬 Написать в поддержку", callback_data="help:support")
    )
    builder.row(
        InlineKeyboardButton(style="primary", text="⬅️ Главная", callback_data="home")
    )
    
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
# 🔧 УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

def confirm_action(action_callback: str, cancel_callback: str = "home") -> InlineKeyboardMarkup:
    """
    Универсальное подтверждение действия.
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(style="primary", text="✅ Да, продолжить", callback_data=action_callback)
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", style="primary", callback_data=cancel_callback)
    )
    
    return builder.as_markup()


def back_button(callback_data: str) -> InlineKeyboardMarkup:
    """
    Простая кнопка "Назад".
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", style="primary", callback_data=callback_data)
    )
    return builder.as_markup()


def close_button() -> InlineKeyboardMarkup:
    """
    Кнопка закрытия.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(style="primary", text="❌ Закрыть", callback_data="delete_message")
    )
    return builder.as_markup()
