from __future__ import annotations

import html

from bot.utils.emojis import Emoji


# ─── WELCOME ───

def welcome_text(username: str, projects_count: int = 0) -> str:
    """Приветственный экран с персонализацией."""
    greeting = "Привет" if projects_count == 0 else "С возвращением"

    stats_text = ""
    if projects_count == 0:
        stats_text = "📦 У тебя пока нет проектов"
    elif projects_count == 1:
        stats_text = "📦 У тебя <b>1</b> проект"
    else:
        stats_text = f"📦 У тебя <b>{projects_count}</b> проектов"

    return f"""<b>🚀 DeployGram</b>

<blockquote>{greeting}, <b>{html.escape(str(username))}</b>!
Здесь ты можешь запустить свой Python-проект в облаке за пару минут — без настройки серверов и сложных команд.</blockquote>

{stats_text}

<i>💡 Загрузи код, нажми «Запустить» — и готово!</i>"""


CONTROL_PANEL_TEXT = """<b>📱 Мои проекты</b>

<i>Выбери проект для управления:</i>"""


EMPTY_PROJECTS = """<b>📭 Пока пусто</b>

Создай свой первый проект прямо сейчас — это займёт всего пару минут.

<blockquote><b>1.</b> Загрузи код
<b>2.</b> Выбери версию Python
<b>3.</b> Настрой запуск и нажми «Старт»</blockquote>

<i>Не волнуйся — мы поможем на каждом шаге 😊</i>"""


# ─── ADD BOT: SOURCE ───

ADD_BOT_SOURCE_TEXT = """<b>✨ Новый проект</b>

Запусти свой Python-проект в три шага:

<blockquote><b>1.</b> Загрузи код
<b>2.</b> Настрой запуск
<b>3.</b> Готово! 🚀</blockquote>

<i>Начнём с загрузки кода. Выбери удобный способ:</i>"""

ADD_BOT_ZIP_TEXT = """<b>📦 Шаг 1: Загрузка кода</b>

Отправь ZIP-архив со своим проектом.

<blockquote><b>Что должно быть внутри:</b>
✓ Python-файлы (<code>*.py</code>)
✓ <code>requirements.txt</code> с зависимостями
✓ любые другие файлы проекта</blockquote>

<b>Ограничения:</b> до 100 МБ, только <code>.zip</code>.

<i>💡 Не знаешь, как упаковать? Выдели файлы проекта → ПКМ → «Отправить» → «Сжатая ZIP-папка».</i>"""

ADD_BOT_GITHUB_TEXT = """<b>🔗 Шаг 1: GitHub-репозиторий</b>

Вставь ссылку на публичный репозиторий GitHub.

<blockquote><b>Формат:</b>
<code>https://github.com/username/project</code></blockquote>

Мы автоматически скачаем код из ветки <code>main</code> или <code>master</code> и развернём его.

<i>💡 Репозиторий должен быть публичным.</i>"""


# ─── ADD BOT: PYTHON VERSION ───

def add_bot_python_text(uploaded_file: str = "") -> str:
    """Выбор версии Python."""
    file_text = (
        f"✅ Код загружен: <code>{html.escape(str(uploaded_file))}</code>\n\n"
        if uploaded_file
        else ""
    )
    
    return f"""<b>🐍 Шаг 2: Версия Python</b>

{file_text}Выбери версию Python для запуска:

<blockquote><b>🔥 Рекомендуем Python 3.12</b>
• самая быстрая версия
• последние обновления
• лучшая безопасность

<b>Другие версии:</b>
• Python 3.11 — стабильная
• Python 3.10 — для старых проектов</blockquote>

<i>💡 Не уверен? Выбирай 3.12 — она подходит для 99% проектов.</i>"""

ADD_BOT_PYTHON_TEXT = add_bot_python_text()


# ─── ADD BOT: ENTRY POINT ───

ADD_BOT_ENTRY_TEXT = """🎯 <b>Шаг 3: Точка входа</b>

<b>Какой файл запускать?</b>

Это главный файл, с которого начинается твой проект.

<b>Обычно это:</b>
  • <code>main.py</code>
  • <code>bot.py</code>
  • <code>app.py</code>
  • <code>run.py</code>

💡 <i>Мы попробуем найти его автоматически, но можешь выбрать вручную</i>"""

def add_bot_entry_script_text(filter: str = "*.py") -> str:
    return """📄 <b>Шаг 3: Выбор файла</b>

Выбери главный файл для запуска проекта:

💡 <i>Обычно это main.py, bot.py, или app.py</i>"""

ADD_BOT_ENTRY_MODULE_TEXT = (
    "📄 <b>Конфигурация вызова</b>\n\n"
    "Контекст: Module invocation / python -m\n\n"
    "Передайте валидное пространство имен модуля.\n"
    "Шаблон ввода: <code>app.pkg.main</code>"
)

ADD_BOT_ENTRY_MANUAL_TEXT = (
    "📄 <b>Конфигурация вызова</b>\n\n"
    "Введите точное имя исполняемого файла вместе с расширением.\n"
    "Пример: <code>main.py</code>"
)

def add_bot_entry_confirm_text(entry: str) -> str:
    return (
        f"<b>📄 Шаг 4/4: Проверка</b>\n\n"
        f"<blockquote>Точка входа: <code>{html.escape(str(entry))}</code></blockquote>\n\n"
        f"<i>Проверь параметры и подтверди создание проекта.</i>"
    )


# ─── ADD BOT: SERVER SELECTION ───

ADD_BOT_SERVER_TEXT = (
    f"🖥 <b>Распределение мощностей</b>\n\n"
    f"Выберите доступный кластер для аллокации ресурсов вашего приложения:"
)

ADD_BOT_SERVER_POOL_TEXT = "[ Общие вычислительные ресурсы ]"


# ─── ADD BOT: CONFIRM ───

def add_bot_confirm_text(name: str, python_version: str, entry_point: str) -> str:
    return (
        f"{Emoji.CHECK} <b>Всё готово?</b>\n\n"
        f"<blockquote>📝 Название: <b>{html.escape(str(name))}</b>\n"
        f"🐍 Python: <b>{html.escape(str(python_version))}</b>\n"
        f"📄 Точка входа: <code>{html.escape(str(entry_point))}</code></blockquote>\n\n"
        f"<i>Проверь параметры и создай проект.</i>"
    )

ADD_BOT_NAME_TEXT = "📝 Отправь название проекта (до 50 символов: латиница, цифры, дефис и подчёркивание):"


# ─── ADD BOT: SUCCESS ───

ADD_BOT_SUCCESS_TEXT = (
    f"🤖 <b>Контейнер успешно развернут</b>\n\n"
    f"Процесс инициализирован, виртуальное окружение переведено в рабочий статус.\n\n"
    f"В карточке управления инстансом вам доступны инструменты прямого чтения логов, "
    f"конфигуратор дерева файлов, сборщик внешних пакетов и метрики нагрузки."
)


# ─── BOT CONTROL ───

def bot_control_text(name: str, server_text: str, status: str, uptime: str, cpu: float, ram: float) -> str:
    """Карточка проекта в новом стиле."""
    # Прогресс-бар для CPU
    cpu_bar = _create_progress_bar(cpu, 100)
    
    # Иконка статуса на основе сырого статуса
    if status == "running":
        status_icon = "🟢"
    elif status in ("error", "stopped"):
        status_icon = "🔴" if status == "error" else "⚫"
    else:
        status_icon = "⚫"
    
    return f"""{status_icon} <b>{html.escape(str(name))}</b>

{html.escape(server_text) if server_text else '📍 Локальный сервер'}

<blockquote><b>📊 Статистика</b>
⏱ Работает: <b>{uptime}</b>
💾 RAM: <b>{ram:.0f} MB</b>
⚡ CPU: <b>{cpu:.1f}%</b>
{cpu_bar}</blockquote>

<i>Выбери действие:</i>"""


def _create_progress_bar(value: float, max_value: float, length: int = 10) -> str:
    """Создаёт текстовый прогресс-бар."""
    filled = int((value / max_value) * length)
    empty = length - filled
    
    if value >= 80:
        bar_char = "🟥"
    elif value >= 50:
        bar_char = "🟨"
    else:
        bar_char = "🟩"
    
    return bar_char * filled + "⬜" * empty


# ─── BOT SETTINGS ───

BOT_SETTINGS_TEXT = """<b>⚙️ Настройки проекта</b>

<i>Выбери, что хочешь изменить:</i>"""

BOT_RENAME_TEXT = """<b>📝 Переименовать проект</b>

Отправь новое название:

<blockquote><b>Правила:</b>
• латиница, цифры, <code>_</code> и <code>-</code>
• от 1 до 50 символов</blockquote>

<b>Пример:</b> <code>my-telegram-bot</code>"""

BOT_DELETE_TEXT = (
    "<b>🗑 Удаление проекта</b>\n\n"
    "Контейнер будет остановлен, файлы и резервные копии — удалены.\n\n"
    "<blockquote>⚠️ <b>Это действие нельзя отменить.</b></blockquote>"
)

def bot_deleted_text(name: str) -> str:
    return (
        f"<b>🗑 Проект удалён</b>\n\n"
        f"Проект <b>{html.escape(str(name))}</b> остановлен, а его файлы удалены.\n\n"
        "<i>Слот освобождён — можно создавать новый проект.</i>"
    )


# ─── BOT PYTHON VERSION ───

BOT_PYTHON_TEXT = (
    "<b>🐍 Версия Python</b>\n\n"
    "После смены версии проект перезапустится и заново установит зависимости.\n\n"
    "<i>💡 Для новых проектов лучше выбирать Python 3.12.</i>"
)


# ─── BOT ENTRY POINT ───

def bot_entry_text(entry_type: str, entry_point: str) -> str:
    return (
        "<b>📄 Точка входа</b>\n\n"
        "Выбери способ запуска:\n\n"
        "<blockquote><b>Скрипт</b> — обычный файл\n"
        "<code>python main.py</code>\n\n"
        "<b>Модуль</b> — Python-пакет\n"
        "<code>python -m app.pkg.main</code></blockquote>\n\n"
        f"Сейчас: <b>{html.escape(str(entry_type))}</b>\n"
        f"Путь: <code>{html.escape(str(entry_point))}</code>"
    )

BOT_ENTRY_MODULE_TEXT = (
    "<b>📄 Точка входа · модуль</b>\n\n"
    "Отправь имя Python-модуля, например:\n"
    "<code>app.pkg.main</code>\n\n"
    "<i>Модуль должен находиться внутри проекта.</i>"
)

BOT_ENTRY_SELECT_FILE_TEXT = "Пожалуйста, определите исполняемый файл, используя интерактивный менеджер директорий."


# ─── BOT COOWNERS ───

def bot_coowners_text(name: str) -> str:
    return f"""<b>👥 Совместный доступ</b>

<b>Проект:</b> {html.escape(str(name))}

<blockquote>Дай доступ друзьям или коллегам. Права можно настроить отдельно для каждого совладельца.</blockquote>

<b>Владелец</b> всегда может:
✅ управлять проектом
✅ удалять его

<i>💡 Удалить проект может только владелец.</i>"""

BOT_COOWNER_ADD_TEXT = "👤 Введите уникальный Telegram ID пользователя для делегирования полномочий:"
BOT_COOWNER_ADD_ROLE_TEXT = "👤 Определите системную роль для добавляемого специалиста:"

def bot_coowner_added_text(user_id: int, role: str) -> str:
    return f"{Emoji.CHECK} Идентификатору {user_id} успешно присвоен статус {role}."

def bot_coowner_deleted_text(user_id: int) -> str:
    return f"{Emoji.CHECK} Права доступа для пользователя {user_id} полностью отозваны."

BOT_COOWNER_NOT_FOUND_TEXT = "Заданный идентификатор отсутствует в реестре пользователей платформы."
BOT_COOWNER_ALREADY_EXISTS_TEXT = "Данный пользователь уже включен в список соавторов этого проекта."


# ─── PROJECT MANAGE ───

def project_card_text(
    name: str,
    status: str,
    python_version: str,
    entry_point: str,
    cpu: float = 0.0,
    ram: float = 0.0,
    uptime: str = "—",
    restarts: int = 0,
) -> str:
    """Карточка проекта с мониторингом."""
    from bot.utils.formatters import format_status
    
    status_emoji = {"running": "🟢", "stopped": "⚫", "error": "🔴"}.get(status, "⚪")
    status_text = format_status(status)
    
    # Статистика только для запущенных проектов
    stats_block = ""
    if status == "running":
        cpu_bar = _create_progress_bar(cpu, 100)
        stats_block = f"""

<blockquote><b>📊 Мониторинг</b>
⚡ CPU: <b>{cpu:.1f}%</b>
{cpu_bar}
💾 RAM: <b>{ram:.1f} MB</b>
⏱ Работает: <b>{html.escape(str(uptime))}</b>
🔄 Перезапусков: <b>{restarts}</b></blockquote>"""

    return f"""<b>{status_emoji} {html.escape(str(name))}</b>

{status_text}

<blockquote>🐍 Python: <b>{html.escape(str(python_version))}</b>
📄 Запуск: <code>{html.escape(str(entry_point))}</code></blockquote>{stats_block}

<i>Выбери действие:</i>"""


PROJECT_START_SUCCESS = "✅ <b>Проект запущен!</b>\n\nКонтейнер развернут и работает."
PROJECT_START_ERROR = "❌ <b>Ошибка запуска</b>\n\nПроверь логи для подробностей."
PROJECT_STOP_SUCCESS = "✅ <b>Проект остановлен</b>\n\nКонтейнер остановлен, данные сохранены."
PROJECT_STOP_ERROR = "❌ <b>Ошибка остановки</b>\n\nПопробуй ещё раз."


# ─── BOT LOGS ───

def bot_logs_text(name: str, logs: str) -> str:
    """Логи проекта в новом стиле."""
    return f"""<b>📋 Логи проекта</b>

<b>{html.escape(str(name))}</b>

<blockquote>Последние 3500 символов:</blockquote>

<pre>{html.escape(logs)}</pre>

<i>💡 Используй «Скачать всё», чтобы получить полный файл логов.</i>"""


# ─── BOT FILES ───

def bot_files_text(project_name: str, path: str = "/app") -> str:
    """Файловый менеджер проекта."""
    return f"""<b>📁 Файлы проекта</b>

<b>{html.escape(str(project_name))}</b>

<blockquote>📂 Текущая папка: <code>{html.escape(str(path))}</code></blockquote>

<b>Доступные действия:</b>
👁️ просмотр файлов
💾 скачивание
🗑️ удаление
📤 загрузка новых файлов

<i>💡 Просто отправь файл в чат, чтобы загрузить его в проект.</i>"""


BOT_FILES_TEXT = bot_files_text("project", "/app")  # Для совместимости


def bot_files_path_text(path: str) -> str:
    return f"📁 <b>{path}</b>"


def bot_file_delete_confirm(file_path: str) -> str:
    return f"""<b>🗑️ Удалить файл?</b>

<blockquote><code>{html.escape(str(file_path))}</code></blockquote>

<i>⚠️ Это действие нельзя отменить.</i>"""


BOT_FILE_DELETE_CONFIRM_TEXT = bot_file_delete_confirm  # Для совместимости

BOT_FILE_DELETED_TEXT = "✅ Файл удалён"
BOT_FILE_DELETE_ERROR_TEXT = "❌ Не удалось удалить файл. Возможно, он используется."
BOT_FILE_NOT_FOUND_TEXT = "❌ Файл не найден"


# ─── BOT LIBRARIES ───

BOT_LIBS_TEXT = """<b>📦 Зависимости проекта</b>

<blockquote>Здесь собраны пакеты, установленные в виртуальном окружении проекта.</blockquote>

<b>Что можно сделать:</b>
➕ установить новый пакет
🗑️ удалить ненужный
🔄 обновить версию

<i>💡 Зависимости ставятся через pip.</i>"""

BOT_LIB_ADD_TEXT = """<b>📦 Установка библиотеки</b>

Отправь название пакета из PyPI:

<blockquote><code>aiogram</code>
<code>requests&gt;=2.30.0</code>
<code>python-dotenv</code></blockquote>

<i>💡 После установки перезапусти проект, чтобы изменения применились.</i>"""


# ─── SUBSCRIPTION ───

def subscription_text(is_premium: bool, projects_count: int = 0, max_projects: int = 1) -> str:
    """Экран подписки с персонализацией."""
    from bot.config import settings

    tariff_emoji = "🆓" if not is_premium else "💎"
    tariff_name = "Бесплатный" if not is_premium else "Premium"
    progress = _create_progress_bar(projects_count, max_projects)

    if is_premium:
        features = f"""<blockquote><b>✅ Твои возможности</b>
🚀 до {settings.PREMIUM_TARIFF_PROJECTS} проектов
💪 {settings.PREMIUM_TARIFF_RAM} MB ОЗУ
⚡ {settings.PREMIUM_TARIFF_CPU:g} CPU
💾 автобэкапы каждый час
🎯 приоритетная поддержка</blockquote>"""
        tip = "💜 <i>Спасибо, что поддерживаешь DeployGram!</i>"
    else:
        features = f"""<blockquote><b>✅ Бесплатный тариф</b>
🚀 {settings.FREE_TARIFF_PROJECTS} проект
💪 {settings.FREE_TARIFF_RAM} MB ОЗУ
⚡ {settings.FREE_TARIFF_CPU:g} CPU
💾 автобэкапы каждый час</blockquote>

<b>💎 Premium открывает:</b>
🚀 до {settings.PREMIUM_TARIFF_PROJECTS} проектов
💪 {settings.PREMIUM_TARIFF_RAM} MB ОЗУ
⚡ {settings.PREMIUM_TARIFF_CPU:g} CPU
🎯 приоритетную поддержку"""
        tip = "💡 <i>Обнови тариф, когда проекту станет тесно.</i>"

    return f"""<b>💳 Твоя подписка</b>

{tariff_emoji} <b>Тариф:</b> {tariff_name}

<b>📦 Проекты:</b> {projects_count} из {max_projects}
{progress}

{features}

{tip}"""


SUBSCRIPTION_INFO_TEXT = None


def subscription_info_text() -> str:
    """Информация о Premium."""
    from bot.config import settings

    return f"""<b>💎 DeployGram Premium</b>

<i>Больше мощности для твоих проектов.</i>

<blockquote>🚀 до <b>{settings.PREMIUM_TARIFF_PROJECTS} проектов</b>
💪 <b>{settings.PREMIUM_TARIFF_RAM} MB ОЗУ</b> на проект
⚡ <b>{settings.PREMIUM_TARIFF_CPU:g} CPU</b>
💾 автобэкапы каждый час
🎯 приоритетная поддержка</blockquote>

<b>💰 Стоимость:</b>
• 1 неделя — <b>{settings.PREMIUM_PRICE_1W}₽</b>
• 1 месяц — <b>{settings.PREMIUM_PRICE_1M}₽</b>
• 3 месяца — <b>{settings.PREMIUM_PRICE_3M}₽</b>
• 6 месяцев — <b>{settings.PREMIUM_PRICE_6M}₽</b>
• 1 год — <b>{settings.PREMIUM_PRICE_12M}₽</b>

<i>🎁 Первая неделя — самый простой способ попробовать. Отменить можно в любой момент.</i>"""


SUBSCRIPTION_BUY_TEXT = """<b>💳 Выбери период подписки</b>

<blockquote>Чем дольше период — тем выгоднее цена.</blockquote>

<i>💡 После выбора покажем инструкцию по оплате.</i>"""


def subscription_buy_plan_text(plan_label: str, price: int) -> str:
    """Подтверждение покупки плана."""
    savings_map = {
        "1 неделя": 0,
        "1 месяц": 0,
        "3 месяца": 45,
        "6 месяцев": 135,
        "1 год": 358
    }
    savings = savings_map.get(plan_label, 0)
    savings_text = f"\n🎉 <b>Экономия: {savings}₽</b>" if savings > 0 else ""
    
    from bot.config import settings

    return f"""<b>💎 Premium · {html.escape(str(plan_label))}</b>

<blockquote><b>Стоимость:</b> {price}₽{savings_text}</blockquote>

<b>Что входит:</b>
🚀 до {settings.PREMIUM_TARIFF_PROJECTS} проектов
💪 {settings.PREMIUM_TARIFF_RAM} MB ОЗУ на проект
⚡ {settings.PREMIUM_TARIFF_CPU:g} CPU
🎯 приоритетная поддержка
💾 автобэкапы каждый час

<b>Как оплатить:</b>
<blockquote>1. Напиши @support_username
2. Отправь: «Premium {html.escape(str(plan_label))}»
3. Получи реквизиты для оплаты</blockquote>

<i>Подписка активируется автоматически после оплаты.</i>"""


# ─── BACKUPS ───

BACKUPS_LIST_EMPTY_TEXT = (
    "<b>☁ Резервные копии</b>\n\n"
    "Пока пусто — создай первый проект, и мы начнём автоматически сохранять его файлы."
)

BACKUPS_LIST_TEXT = (
    "<b>☁ Резервные копии</b>\n\n"
    "<blockquote>🟢 — бэкап готов к восстановлению\n"
    "🟡 — создаётся\n"
    "🔴 — ошибка создания</blockquote>\n\n"
    "<i>Выбери проект, чтобы посмотреть его резервные копии.</i>"
)

BACKUP_CREATE_ERROR = "❌ Не удалось создать резервную копию. Попробуй ещё раз."

def backups_bot_text(name: str, count: int) -> str:
    return (
        f"<b>☁ Резервные копии</b>\n\n"
        f"<b>Проект:</b> {html.escape(str(name))}\n"
        f"<b>Сохранено:</b> {count}"
    )


# ─── ADMIN PANEL ───

def admin_panel_text(users: int, projects: int, servers: int) -> str:
    return (
        f"{Emoji.SETTINGS} <b>Админ-панель</b>\n\n"
        f"<blockquote>{Emoji.PROFILE} Пользователи: <b>{users}</b>\n"
        f"{Emoji.FILE} Проекты: <b>{projects}</b>\n"
        f"{Emoji.HOME} Серверы: <b>{servers}</b></blockquote>"
    )

def admin_users_text(count: int) -> str:
    return f"{Emoji.PEOPLE} <b>Пользователи</b> · {count}"

def admin_user_view_text(
    telegram_id: int, username: str, full_name: str,
    tariff: str, balance: float, is_banned: bool,
    projects_count: int, registered_at: str
) -> str:
    status = "🚫 Заблокирован" if is_banned else "✅ Активен"
    return (
        f"{Emoji.PROFILE} <b>Профиль пользователя</b>\n\n"
        f"<blockquote>Telegram ID: <code>{telegram_id}</code>\n"
        f"Username: @{html.escape(str(username or '—'))}\n"
        f"Имя: {html.escape(str(full_name or '—'))}\n"
        f"Тариф: <b>{html.escape(str(tariff))}</b>\n"
        f"Баланс: <b>{balance:.2f}₽</b>\n"
        f"Статус: {status}\n"
        f"Проектов: <b>{projects_count}</b>\n"
        f"Регистрация: {html.escape(str(registered_at))}</blockquote>"
    )

def admin_servers_text(count: int) -> str:
    return f"{Emoji.HOME} <b>Серверы</b> · {count}"

def admin_server_view_text(
    name: str, country: str, ip: str, port: int,
    api_key: bool, free_slots: int, total_slots: int,
    rating: float, ping: int, load_cpu: float, load_ram: float,
    status: str
) -> str:
    status_icon = "🟢 Онлайн" if status == "online" else "🔴 Недоступен"
    api_key_text = "включён" if api_key else "выключен"
    return (
        f"{Emoji.HOME} <b>Сервер · {html.escape(str(name))}</b>\n\n"
        f"<blockquote>🌍 Локация: {html.escape(str(country))}\n"
        f"📡 Адрес: <code>{html.escape(str(ip))}:{port}</code>\n"
        f"🔑 API-ключ: {api_key_text}\n"
        f"💻 Слоты: <b>{free_slots}/{total_slots}</b>\n"
        f"⭐ Рейтинг: <b>{rating:.1f}</b>\n"
        f"📡 Ping: <b>{ping} ms</b>\n"
        f"📊 CPU: <b>{load_cpu:.1f}%</b>\n"
        f"🧠 RAM: <b>{load_ram:.1f}%</b>\n"
        f"Статус: {status_icon}</blockquote>"
    )

def admin_stats_text(users: int, projects: int, active: int, servers: int, online: int) -> str:
    return (
        f"{Emoji.GRAPH_STATS} <b>Статистика платформы</b>\n\n"
        f"<blockquote>👤 Пользователи: <b>{users}</b>\n"
        f"📦 Проекты: <b>{projects}</b>\n"
        f"🟢 Запущено: <b>{active}</b>\n"
        f"🌍 Серверы: <b>{servers}</b>\n"
        f"🟢 Онлайн: <b>{online}</b></blockquote>"
    )

def admin_promos_text(count: int) -> str:
    return f"{Emoji.GIFT} <b>Промокоды</b> · {count}"

def admin_subscriptions_text(free_count: int, premium_count: int, total: int) -> str:
    return (
        f"💎 <b>Тарифы</b>\n\n"
        f"<blockquote>🆓 Free: <b>{free_count}</b>\n"
        f"💎 Premium: <b>{premium_count}</b>\n"
        f"Всего: <b>{total}</b></blockquote>"
    )

def admin_referrals_text(count: int) -> str:
    return (
        f"🔗 <b>Рефералы</b>\n\n"
        f"<blockquote>Приглашений: <b>{count}</b></blockquote>"
    )


# ─── ADMIN: SERVER ADD ───

ADMIN_SERVER_ADD_NAME = f"{Emoji.HOME} Укажите уникальное наименование для новой ноды кластера:"
ADMIN_SERVER_ADD_COUNTRY = f"{Emoji.HOME} Введите географическое расположение сервера:"
ADMIN_SERVER_ADD_IP = f"{Emoji.HOME} Введите публичный IPv4/IPv6 адрес хоста:"
ADMIN_SERVER_ADD_API_KEY = f"{Emoji.HOME} Введите токен аутентификации агента (или «-» при его отсутствии):"
ADMIN_SERVER_ADD_SLOTS = f"{Emoji.HOME} Укажите лимит одновременно размещаемых контейнеров:"

ADMIN_SERVER_ADD_CHECKING = f"{Emoji.LOADING} <b>Выполняется проверка сетевого сопряжения с удаленным агентом...</b>"

def admin_server_add_success(name: str, country: str, ip: str, slots: int, api_key: str) -> str:
    return (
        f"✅ <b>Новый вычислительный узел {name} успешно интегрирован</b>\n\n"
        f"🌍 Локация: {country}\n"
        f"📡 Сетевой интерфейс: {ip}:8080\n"
        f"💻 Доступные слоты: {slots}\n"
        f"🔑 Токен безопасности: {api_key}"
    )

ADMIN_SERVER_ADD_ERROR = (
    f"❌ <b>Не удалось установить стабильное соединение с удаленным хостом</b>\n\n"
    f"Чек-лист для проверки:\n"
    f"1. Убедитесь, что процесс серверного агента запущен\n"
    f"2. Проверьте правила Firewall для входящего порта 8080\n"
    f"3. Проверьте корректность указанного IP адреса"
)


# ─── ADMIN: PROMO CREATE ───

ADMIN_PROMO_CREATE_CODE = f"{Emoji.GIFT} Введите уникальную комбинацию символов промокода:"
ADMIN_PROMO_CREATE_TYPE = f"{Emoji.GIFT} Выберите тип начисляемого бонуса (tariff / projects / balance):"
ADMIN_PROMO_CREATE_VALUE = f"{Emoji.GIFT} Задайте числовой эквивалент награды:"
ADMIN_PROMO_CREATE_MAX = f"{Emoji.GIFT} Установите максимальный лимит использований купона:"

def admin_promo_create_success(code: str) -> str:
    return f"{Emoji.CHECK} Промокод <b>{code}</b> успешно сгенерирован и добавлен в глобальный реестр."


# ─── ADMIN: BROADCAST ───

ADMIN_BROADCAST_TEXT = f"{Emoji.SPEAKER} Сформируйте информационный пакет (текст/медиа) для массовой отправки:"

def admin_broadcast_done(sent: int, failed: int) -> str:
    return (
        f"{Emoji.CHECK} Процедура массового уведомления пользователей завершена.\n\n"
        f"✅ Успешно доставлено: {sent}\n"
        f"❌ Системные сбои доставки: {failed}"
    )


# ─── ADMIN: SETTINGS ───

ADMIN_SETTINGS_TEXT = f"{Emoji.SETTINGS} <b>Глобальные системные триггеры платформы</b>"

def admin_sleep_changed(minutes: int) -> str:
    return f"✅ Параметр автоматического перевода процессов в спящий режим изменен: {minutes} мин."


# ─── ADMIN: PHOTOS ───

ADMIN_PHOTOS_TEXT = (
    f"{Emoji.MEDIA} <b>Менеджер статических медиаресурсов</b>\n\n"
    f"✅ — Изображение активно\n"
    f"⬜ — Используется текстовая разметка по умолчанию\n\n"
    f"Выберите целевой экран интерфейса для кастомизации баннера."
)

def admin_photo_set_text(label: str, status: str) -> str:
    return (
        f"{Emoji.MEDIA} <b>Интерфейс: {label}</b>\n\n"
        f"Текущее состояние медиа: {status}\n\n"
        f"Прикрепите и отправьте новое графическое изображение.\n"
        f"Для сброса настроек отправьте ключевое слово <code>удалить</code>."
    )

def admin_photo_success(label: str) -> str:
    return f"{Emoji.CHECK} Графическое оформление для экрана <b>{label}</b> успешно обновлено."

def admin_photo_deleted(label: str) -> str:
    return f"{Emoji.CHECK} Кастомный баннер для экрана <b>{label}</b> успешно аннулирован."


# ─── SUCCESS MESSAGES ───

def success_bot_renamed(name: str) -> str:
    return f"✅ Готово! Проект переименован в <b>{name}</b>"

def success_python_changed(version: str) -> str:
    return f"✅ Python {version} установлен. Перезапусти проект для применения изменений."

def success_lib_added(lib: str) -> str:
    return f"✅ Библиотека <b>{lib}</b> добавлена в зависимости. Перезапусти проект для установки."


# ─── ERRORS ───

ERROR_NOT_FOUND = "❌ Проект не найден"
ERROR_NO_ACCESS = "⛔ У тебя нет доступа к этому проекту"
ERROR_INVALID_NAME = "❌ Неправильное название. Используй только латиницу, цифры, _ и - (от 1 до 50 символов)"
ERROR_INVALID_ZIP = "❌ Это не ZIP архив. Отправь файл с расширением .zip"
ERROR_INVALID_URL = "❌ Неправильная ссылка. Формат: <code>https://github.com/user/repo</code>"
ERROR_REPO_NOT_FOUND = "❌ Репозиторий не найден или закрыт"
ERROR_DOCKER_UNAVAILABLE = "❌ Сервер временно недоступен"
ERROR_CONTAINER_NOT_RUNNING = "❌ Проект не запущен"
ERROR_ADMIN_ONLY = "⛔ Только для администраторов"

def error_limit_reached(limit: int) -> str:
    return f"❌ Лимит проектов исчерпан (максимум: {limit}). Удали ненужные или обнови тариф."

def error_upload_failed(error: str) -> str:
    return f"❌ Ошибка загрузки файла: {error}"


# ─── BUTTONS ───

BTN_BACK = "Вернуться"
BTN_CANCEL = "Отменить операцию"
BTN_CONFIRM = "✅ Утвердить спецификацию"
BTN_DELETE = "🗑 Удалить"
BTN_YES_DELETE = "✅ Да, подтверждаю безвозвратное удаление"
BTN_NO = "❌ Отклонить"
BTN_CLOSE = "✕ Закрыть терминал"
BTN_ADD = "➕ Добавить"

BTN_START = "▶ Запустить контейнер"
BTN_STOP = "⏹ Инициировать SIGTERM"
BTN_RESTART = "🔄 Выполнить Reboot"
BTN_LOGS = "📋 Вывод stdout/stderr"
BTN_LOGS_FILE = "📄 Скачать лог-файл"
BTN_LOGS_REFRESH = "🔄 Перезапустить поток логов"
BTN_SETTINGS = "⚙ Системная конфигурация"

BTN_LIBRARIES = "📦 Сборщик пакетов Pip"
BTN_LIBRARY_ADD = "➕ Добавить зависимость"
BTN_FILES = "📁 Структура директорий"
BTN_PYTHON_VERSION = "🐍 Версия рантайма Python"
BTN_ENTRY_POINT = "📄 Конфигурация точки входа"
BTN_COOWNERS = "👥 Настройка прав доступа"
BTN_GRAPHS = "📊 Метрики утилизации ресурсов"
BTN_NOTIFICATIONS = "🔔 Настройка системных алертов"
BTN_RENAME = "✏ Модифицировать ID инстанса"
BTN_DELETE_BOT = "🗑 Ликвидировать инстанс"

BTN_ADD_BOT = "➕ Развернуть новый сервис"
BTN_UPLOAD_FILES = "📥 Загрузить локальный .ZIP"
BTN_CONNECT_GITHUB = "🔗 Авторизовать репозиторий GitHub"
BTN_SCRIPT_MODE = "📄 Скриптовый запуск"
BTN_MODULE_MODE = "📦 Модульный пакет"

BTN_FILE_DOWNLOAD = "⬇️ Экспорт"
BTN_FILE_DELETE = "🗑 Стереть"
BTN_FILE_UP = "⬆ На уровень выше"

BTN_COOWNER_ADD = "➕ Предоставить права"
BTN_COOWNER_DELETE = "🗑 Аннулировать доступ"

BTN_SUBSCRIPTION_INFO = "❓ Спецификация коммерческих тарифов"
BTN_SUBSCRIPTION_BUY = "💳 Перейти к оформлению лицензии"

BTN_ADMIN_USERS = "👤 База аккаунтов"
BTN_ADMIN_SERVERS = "🖥 Управление нодами кластера"
BTN_ADMIN_STATS = "📊 Аналитическая панель"
BTN_ADMIN_PROMOS = "🎁 Промокоды и купоны"
BTN_ADMIN_BROADCAST = "📢 Системный пуш-алерт"
BTN_ADMIN_SETTINGS = "⚙ Глобальные триггеры"
BTN_ADMIN_PHOTOS = "🖼 Управление графикой"

BTN_CREATE_BACKUP = "➕ Создать снимок системы"
BTN_RESTORE_BACKUP = "🔄 Восстановить конфигурацию"
BTN_DELETE_BACKUP = "🗑 Стереть архивный снимок"


# ─── PROJECT MONITOR ───

def project_monitor_text(name: str, status_text: str, cpu: float, ram: float, disk: float, uptime: str, restarts: int) -> str:
    return (
        f"<b>{Emoji.GRAPH_STATS} Мониторинг</b>\n\n"
        f"<b>{html.escape(str(name))}</b>\n\n"
        f"<blockquote>Статус: {status_text}\n"
        f"⚡ CPU: <b>{cpu:.1f}%</b>\n"
        f"💾 RAM: <b>{ram:.1f} MB</b>\n"
        f"💽 Диск: <b>{disk:.1f} MB</b>\n"
        f"⏱ Uptime: <b>{html.escape(str(uptime))}</b>\n"
        f"🔄 Перезапусков: <b>{restarts}</b></blockquote>"
    )

def project_graphs_text(hours: int, avg_cpu: float, max_cpu: float, avg_ram: float, max_ram: float, data_points: int) -> str:
    return (
        f"<b>{Emoji.GRAPH_UP} Статистика за {hours} ч</b>\n\n"
        f"<blockquote>⚡ <b>CPU</b>\n"
        f"среднее: {avg_cpu:.1f}%\n"
        f"пик: {max_cpu:.1f}%\n\n"
        f"💾 <b>RAM</b>\n"
        f"среднее: {avg_ram:.1f} MB\n"
        f"пик: {max_ram:.1f} MB</blockquote>\n\n"
        f"<i>{Emoji.INFO} Точек данных: {data_points}</i>"
    )

ERROR_NO_STATS_DATA = "📊 За выбранный период данных пока нет."


# ─── PROJECT SETTINGS ───

def project_settings_text(name: str, python_version: str, entry_point: str, entry_type: str) -> str:
    return (
        f"<b>{Emoji.SETTINGS} Настройки проекта</b>\n\n"
        f"<b>{html.escape(str(name))}</b>\n\n"
        f"<blockquote>🐍 Python: <b>{html.escape(str(python_version))}</b>\n"
        f"📄 Запуск: <code>{html.escape(str(entry_point))}</code>\n"
        f"Режим: {html.escape(str(entry_type))}</blockquote>"
    )

PROJECT_PYTHON_SELECT_TEXT = f"{Emoji.SETTINGS} <b>Версия Python</b>\n\nВыбери версию для проекта:"
PROJECT_ENTRY_INPUT_TEXT = f"{Emoji.PENCIL} <b>Точка входа</b>\n\nОтправь путь к файлу или имя модуля:"
PROJECT_SETTINGS_USE_CARD = "Вернуться к карточке проекта"


# ─── PROJECT LOGS ───

def project_logs_menu_text(name: str) -> str:
    return f"""<b>📋 Логи проекта</b>

<b>{html.escape(str(name))}</b>

<i>Что хочешь сделать?</i>"""

def project_logs_view_text(logs: str) -> str:
    return f"""<b>📋 Логи проекта</b>

<blockquote>Последние 100 строк:</blockquote>

<pre>{html.escape(str(logs))}</pre>

<i>💡 Используй «Скачать», чтобы получить полный файл.</i>"""

def project_logs_file_caption(name: str) -> str:
    return f"📄 Логи проекта <b>{html.escape(str(name))}</b>"

PROJECT_LOGS_CLEARED = "✅ Логи очищены"
PROJECT_LOGS_CLEAR_ERROR = "❌ Не удалось очистить логи. Попробуй ещё раз."


# ─── PROJECT MANAGE ───

def project_delete_confirm_text(name: str) -> str:
    return (
        f"<b>{Emoji.TRASH} Удалить проект?</b>\n\n"
        f"Проект <b>{html.escape(str(name))}</b> будет остановлен, а его файлы и бэкапы — удалены.\n\n"
        "<blockquote>⚠️ <b>Это действие нельзя отменить.</b></blockquote>"
    )

PROJECT_DELETED_TEXT = f"{Emoji.CHECK} <b>Проект удалён</b>\n\nСлот освобождён."
PROJECT_DELETE_ERROR = "❌ Не удалось удалить проект. Попробуй ещё раз."


# ─── PROFILE & SETTINGS ───

def profile_text(
    username: str,
    tariff: str,
    projects_count: int,
    max_projects: int,
    balance: float,
    referral_link: str,
) -> str:
    """Текст профиля пользователя."""
    tariff_icon = "💎" if tariff == "premium" else "🆓"
    tariff_name = "Premium" if tariff == "premium" else "Бесплатный"
    
    # Прогресс-бар для проектов
    progress_bar = _create_progress_bar(projects_count, max_projects)
    
    return f"""<b>👤 Твой профиль</b>

<b>{html.escape(str(username))}</b>

<blockquote>📦 <b>Проекты:</b> {projects_count} из {max_projects}
{progress_bar}

{tariff_icon} <b>Тариф:</b> {tariff_name}
💰 <b>Баланс:</b> {balance:.2f}₽</blockquote>

<b>🔗 Реферальная ссылка:</b>
<code>{html.escape(str(referral_link))}</code>

<i>💡 Приглашай друзей и получай бонусы.</i>"""


SETTINGS_NOT_FOUND = "❌ Настройки не найдены"
SETTINGS_UNKNOWN = "❌ Неизвестная настройка"
SETTINGS_CHANGED = "✅ Настройка изменена"


def notification_settings_text() -> str:
    """Настройки уведомлений."""
    return """<b>🔔 Уведомления</b>

<blockquote><b>📊 Статус проектов</b>
запуск · остановка · ошибки

<b>⚠️ Ресурсы</b>
высокая нагрузка CPU/RAM · мало места

<b>📦 Бэкапы и обновления</b>
создание копии · завершение обновления</blockquote>

<i>💡 Нажми на пункт, чтобы включить или выключить уведомление.</i>"""


# ─── LOCATIONS ───

LOCATIONS_NO_SERVERS = f"{Emoji.HOME} <b>Серверы</b>\n\n<i>Сейчас нет доступных серверов — попробуй позже.</i>"
LOCATIONS_SERVERS_TEXT = f"{Emoji.HOME} <b>Доступные серверы</b>\n\n<i>Выбери площадку для размещения проекта.</i>"
LOCATION_NOT_FOUND = "❌ Сервер не найден."


# ─── SUBSCRIPTION ───

SUBSCRIPTION_PLAN_UNKNOWN = "Запрошена неподдерживаемая или архивная тарифная сетка."

def subscription_buy_confirm_text(plan_label: str, price: int) -> str:
    return (
        f"<b>💳 Premium · {html.escape(str(plan_label))}</b>\n\n"
        f"<blockquote>Стоимость: <b>{price}₽</b></blockquote>\n\n"
        f"<i>Для оплаты напиши в поддержку — мы поможем активировать подписку.</i>"
    )


# ─── COOWNERS ───

COOWNER_ENTER_ID = """<b>👥 Добавить совладельца</b>

Отправь <b>Telegram ID</b> пользователя.

<blockquote><b>Как узнать ID:</b>
1. Пусть человек напишет @userinfobot
2. Бот ответит его ID
3. Отправь это число сюда</blockquote>

<b>Пример:</b> <code>123456789</code>

<i>💡 Пользователь должен хотя бы раз запустить бота.</i>"""

COOWNER_REMOVED = "✅ Доступ отозван"
COOWNER_INVALID_ID = "❌ <b>Неверный формат</b>\n\nID должен быть числом."
COOWNER_SELF_ADD = "❌ <b>Нельзя добавить себя</b>\n\nТы уже владелец проекта."
COOWNER_USER_NOT_FOUND = "❌ <b>Пользователь не найден</b>\n\nОн должен сначала запустить бота."
COOWNER_ALREADY_EXISTS = "❌ <b>Уже добавлен</b>\n\nЭтот пользователь уже имеет доступ."

def coowner_added_text(username: str) -> str:
    return (
        f"<b>✅ Доступ предоставлен</b>\n\n"
        f"<b>{html.escape(str(username))}</b> теперь может управлять этим проектом."
    )


# ─── BOT CREATE ───

BOT_CREATE_INVALID_ZIP = "❌ Сбой парсинга. Загруженный файл не является валидным архивом сжатия .zip."
BOT_CREATE_INVALID_URL = "❌ Ошибка синтаксиса URL. Шаблон ссылки должен соответствовать стандарту:\n<code>https://github.com/user/repo</code>"
BOT_CREATE_REPO_NOT_FOUND = "❌ Запрошенный удаленный репозиторий удален или закрыт настройками приватности VCS."
BOT_CREATE_ARCHIVE_NOT_FOUND = "Пакет исходного кода не обнаружен во временном буфере хоста."
BOT_CREATE_NO_SERVERS = "В данный момент все серверные ноды кластера загружены на 100%. Слоты отсутствуют."
BOT_CREATE_INVALID_NAME = "❌ Ошибка валидации ID: разрешены латинские символы, цифры, знаки дефиса и нижнего подчеркивания (до 50 знаков)."
BOT_CREATE_LIMIT_REACHED = lambda limit: f"Превышена квота на выделение параллельных виртуальных сред для вашего аккаунта (максимум: {limit})"
BOT_CREATE_DOWNLOAD_ERROR = lambda e: f"Стековый сбой сетевого протокола при скачивании исходного пакета: {e}"

BOT_CREATE_NAME_TEXT = "📝 <b>Идентификация нового сервиса</b>\n\nУкажите системный ID проекта (от 1 до 50 символов: латиница, цифры, дефис, нижнее подчеркивание):"
BOT_CREATE_ENTRY_MANUAL_TEXT = (
    "📄 <b>Определение главного файла</b>\n\n"
    "Введите точное имя исполняемого файла конфигурации вручную.\n"
    "Пример: <code>main.py</code>"
)
BOT_CREATE_ENTRY_MODULE_TEXT = (
    "📄 <b>Определение главного файла</b>\n\n"
    "Режим исполнения: Пакетный модуль (вызов через -m)\n\n"
    "Введите валидное имя пространства имен модуля.\n"
    "Пример: <code>app.pkg.main</code>"
)
def bot_create_entry_confirm_text(entry: str) -> str:
    return (
        f"<b>📄 Точка входа</b>\n\n"
        f"<blockquote><code>{html.escape(str(entry))}</code></blockquote>\n\n"
        f"<i>Проверь параметр и подтверди создание проекта.</i>"
    )

def bot_create_confirm_text(name: str, python: str, entry: str) -> str:
    return (
        f"{Emoji.CHECK} <b>Проверь параметры</b>\n\n"
        f"<blockquote>📝 Проект: <b>{html.escape(str(name))}</b>\n"
        f"🐍 Python: <b>{html.escape(str(python))}</b>\n"
        f"📄 Запуск: <code>{html.escape(str(entry))}</code></blockquote>\n\n"
        f"<i>Создать проект?</i>"
    )

BOT_CREATE_SUCCESS_TEXT = (
    f"🤖 <b>Проект создан</b>\n\n"
    f"<blockquote>Контейнер развёрнут и готов к запуску.</blockquote>\n\n"
    f"<i>Открой карточку проекта, чтобы запустить его.</i>"
)


# ─── ADMIN ───

ADMIN_NO_ACCESS = "⛔ У тебя нет доступа к админ-панели."
ADMIN_USER_NOT_FOUND = "❌ Пользователь не найден."
ADMIN_SERVER_NOT_FOUND = "❌ Сервер не найден."
ADMIN_SERVER_DELETED = "✅ Сервер удалён."
ADMIN_REFERRAL_WIP = "🔗 Реферальная статистика скоро появится."

ADMIN_USER_BANNED = "🚫 Пользователь заблокирован"
ADMIN_USER_UNBANNED = "✅ Пользователь разблокирован"
ADMIN_TARIFF_CHANGED = lambda tariff: f"✅ Тариф изменён на {tariff}"
ADMIN_BALANCE_INPUT_ERROR = "❌ Введи число, например 100 или -50."
ADMIN_PROMO_TYPE_ERROR = "❌ Ошибка валидации типа сущности купона. Разрешенные значения: tariff, projects, balance"

def admin_user_status_text(username: str, status: str) -> str:
    return f"{Emoji.PROFILE} <b>@{username}</b> — Статус системной активности аккаунта: {status}"

def admin_user_tariff_text(username: str, tariff: str) -> str:
    return f"{Emoji.PROFILE} <b>@{username}</b> — Действующий тарифный план: {tariff}"

def admin_balance_result_text(amount: float, balance: float) -> str:
    return (
        f"{Emoji.CHECK} Финансовый баланс скорректирован на величину: {amount:.2f}\n"
        f"Текущее состояние внутреннего счета: {balance:.2f}"
    )

def admin_server_delete_confirm_text(name: str) -> str:
    return (
        f"{Emoji.TRASH} <b>Удалить сервер?</b>\n\n"
        f"<blockquote><b>{html.escape(str(name))}</b> будет удалён из инфраструктуры.\n"
        f"Проекты на нём не удалятся, но потеряют привязку к серверу.</blockquote>"
    )

ADMIN_SERVER_ENTER_NAME = f"{Emoji.HOME} Задайте кодовое наименование для регистрируемой ноды:"
ADMIN_SERVER_ENTER_COUNTRY = f"{Emoji.HOME} Укажите страну физического размещения сервера:"
ADMIN_SERVER_ENTER_IP = f"{Emoji.HOME} Задайте статический IPv4/IPv6 адрес хоста:"
ADMIN_SERVER_ENTER_API_KEY = f"{Emoji.HOME} Задайте токен безопасности агента (или «-» для деплоя без авторизации):"
ADMIN_SERVER_ENTER_SLOTS = f"{Emoji.HOME} Установите предел доступных виртуальных слотов памяти:"
ADMIN_SERVER_CHECKING = f"{Emoji.LOADING} <b>Ожидание ответа по сетевому протоколу от удаленного агента...</b>"

ADMIN_PROMO_ENTER_CODE = f"{Emoji.GIFT} Задайте комбинацию символов промокода:"
ADMIN_PROMO_ENTER_TYPE = f"{Emoji.GIFT} Выберите категорию процессинга купона (tariff/projects/balance):"
ADMIN_PROMO_ENTER_VALUE = f"{Emoji.GIFT} Задайте номинал начисляемого вознаграждения:"
ADMIN_PROMO_ENTER_MAX = f"{Emoji.GIFT} Укажите лимит общего пула активаций для данного промокода:"

ADMIN_BROADCAST_ENTER_MESSAGE = f"{Emoji.SPEAKER} Сформируйте информационный пакет сообщений для глобальной пуш-рассылки:"

def admin_broadcast_done_text(sent: int, failed: int) -> str:
    return (
        f"{Emoji.CHECK} Глобальная рассылка пуш-уведомлений пользователям успешно завершена.\n\n"
        f"✅ Успешных доставок: {sent}\n"
        f"❌ Исключений сетевого тайм-аута: {failed}"
    )

ADMIN_SLEEP_CHANGED = lambda minutes: f"✅ Период неактивности до перевода процессов в режим сна изменен: {minutes} минут"
ADMIN_TARIFF_SELECT_TEXT = f"{Emoji.SETTINGS} Выберите целевой тарифный план для активации на аккаунте пользователя:"
ADMIN_BALANCE_INPUT_TEXT = f"{Emoji.COIN} Задайте значение модификации баланса (положительное — пополнение счета, отрицательное — списание ресурсов):"


# ─── SUCCESS ───

SUCCESS_BOT_STARTED = "✅ Проект запущен!"
SUCCESS_BOT_STOPPED = "✅ Проект остановлен"

def success_secret_added(key: str) -> str:
    return f"✅ Переменная <b>{key}</b> добавлена в окружение"

def success_secret_deleted(key: str) -> str:
    return f"✅ Переменная <b>{key}</b> удалена"

SUCCESS_BACKUP_CREATED = "☁ <b>Резервная копия создана</b>\n\n<i>Файлы проекта сохранены.</i>"

def success_entry_changed(entry: str) -> str:
    return f"<b>✅ Точка входа изменена</b>\n\n<code>{html.escape(str(entry))}</code>"

def success_python_changed(version: str) -> str:
    return f"<b>✅ Python обновлён</b>\n\nПроект будет запущен на Python {html.escape(str(version))}."

def success_balance_changed(amount: float, balance: float) -> str:
    return (
        f"<b>✅ Баланс изменён</b>\n\n"
        f"Изменение: <b>{amount:+.2f}₽</b>\n"
        f"Текущий баланс: <b>{balance:.2f}₽</b>"
    )


# ─── COOWNERS (NEW) ───

COOWNER_ENTER_ID = """<b>👥 Добавить совладельца</b>

Введи Telegram ID пользователя:

<blockquote><b>Где найти ID:</b>
• @userinfobot — отправь ему любое сообщение
• это просто число, например <code>123456789</code></blockquote>

<i>💡 Пользователь должен хотя бы раз запустить бота.</i>"""

COOWNER_INVALID_ID = "❌ Это не похоже на Telegram ID. Введи число, например: <code>123456789</code>"
COOWNER_SELF_ADD = "❌ Нельзя добавить самого себя в совладельцы 😊"
COOWNER_USER_NOT_FOUND = "❌ Пользователь не найден. Он должен хотя бы раз запустить бота."
COOWNER_ALREADY_EXISTS = "❌ Этот пользователь уже является совладельцем"
COOWNER_REMOVED = "✅ Совладелец удалён"

def coowner_added_text(username: str) -> str:
    return f"""<b>✅ Совладелец добавлен</b>

<b>{html.escape(str(username))}</b> теперь имеет доступ к проекту.

<blockquote><b>Разрешения по умолчанию:</b>
✅ запуск и остановка
✅ просмотр логов
✅ просмотр настроек</blockquote>

<i>Разрешения можно изменить в списке совладельцев.</i>"""

def coowner_permissions_text(user_id: int) -> str:
    return f"""<b>🔐 Разрешения совладельца</b>

<b>ID:</b> <code>{user_id}</code>

<blockquote>Настрой, что может делать этот совладелец.

<b>Действия</b>
запуск и остановка · просмотр логов

<b>Файлы</b>
редактирование · управление зависимостями

<b>Настройки</b>
просмотр параметров проекта</blockquote>

<i>💡 Нажми на пункт, чтобы включить или выключить разрешение.</i>"""

def success_entry_changed(entry: str) -> str:
    return f"<b>✅ Точка входа изменена</b>\n\n<code>{html.escape(str(entry))}</code>"
