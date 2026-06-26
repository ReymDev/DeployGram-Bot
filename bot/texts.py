from __future__ import annotations

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
    
    return f"""🚀 <b>DeployGram</b>

{greeting}, <b>{username}</b>!

Здесь ты можешь запустить свой Python проект в облаке за пару минут — без настройки серверов и сложных команд.

{stats_text}

💡 <i>Загрузи код, нажми "Запустить" — и готово!</i>"""


CONTROL_PANEL_TEXT = """📱 <b>Мои проекты</b>

Выбери проект для управления:"""


EMPTY_PROJECTS = """📭 <b>Пока пусто</b>

Создай свой первый проект прямо сейчас!

Это займёт всего 2 минуты:
  ① Загрузи код
  ② Выбери Python версию
  ③ Запусти

<i>Не волнуйся — мы поможем на каждом шаге 😊</i>"""


# ─── ADD BOT: SOURCE ───

ADD_BOT_SOURCE_TEXT = """✨ <b>Новый проект</b>

Запусти свой Python проект в 3 шага:

<b>Шаг 1</b> → Загрузи код
<b>Шаг 2</b> → Настрой запуск  
<b>Шаг 3</b> → Готово! 🚀

Начнём с загрузки кода. Выбери удобный способ:"""

ADD_BOT_ZIP_TEXT = """📦 <b>Шаг 1: Загрузка кода</b>

Отправь ZIP-архив со своим проектом.

<b>Что должно быть внутри:</b>
  ✓ Файлы Python (*.py)
  ✓ requirements.txt с зависимостями
  ✓ Другие файлы проекта

<b>Ограничения:</b>
  • Максимум 100 МБ
  • Формат: только .zip

💡 <i>Не знаешь как упаковать? Просто выдели все файлы проекта → ПКМ → "Отправить" → "Сжатая ZIP-папка"</i>"""

ADD_BOT_GITHUB_TEXT = """🔗 <b>Шаг 1: GitHub репозиторий</b>

Вставь ссылку на публичный GitHub репозиторий.

<b>Формат:</b>
<code>https://github.com/username/project</code>

Мы автоматически склонируем код и развернём его.

💡 <i>Репозиторий должен быть публичным или у нас должен быть доступ</i>"""


# ─── ADD BOT: PYTHON VERSION ───

def add_bot_python_text(uploaded_file: str = "") -> str:
    """Выбор версии Python."""
    file_text = f"✅ Код загружен: <code>{uploaded_file}</code>\n\n" if uploaded_file else ""
    
    return f"""🐍 <b>Шаг 2: Версия Python</b>

{file_text}Теперь выбери версию Python для запуска:

<b>🔥 Рекомендуем Python 3.12</b>
  • Самая быстрая версия
  • Последние обновления
  • Лучшая безопасность

<b>Другие версии:</b>
  • Python 3.11 — стабильная
  • Python 3.10 — для старых проектов

💡 <i>Не уверен? Выбирай 3.12 — она подходит для 99% проектов</i>"""

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
        f"📄 <b>Этап 4/4: Проверка деплоя</b>\n\n"
        f"Назначенный триггер: <code>{entry}</code>\n\n"
        f"Утвердите выбранный параметр. Изменение структуры доступно в настройках рантайма."
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
        f"{Emoji.CHECK} <b>Финальная спецификация сборки</b>\n\n"
        f"📝 Идентификатор: <b>{name}</b>\n"
        f"🐍 Окружение: Python {python_version}\n"
        f"📄 Вызов процесса: <code>{entry_point}</code>\n\n"
        f"Запустить процедуру оркестрации и создания контейнера?"
    )

ADD_BOT_NAME_TEXT = "📝 Задайте уникальный системный ID проекта (до 50 символов: a-z, 0-9, символы дефиса и подчеркивания):"


# ─── ADD BOT: SUCCESS ───

ADD_BOT_SUCCESS_TEXT = (
    f"🤖 <b>Контейнер успешно развернут</b>\n\n"
    f"Процесс инициализирован, виртуальное окружение переведено в рабочий статус.\n\n"
    f"В карточке управления инстансом вам доступны инструменты прямого чтения логов, "
    f"конфигуратор дерева файлов, сборщик внешних пакетов и метрики нагрузки."
)


# ─── BOT CONTROL ───

def bot_control_text(name: str, server_text: str, status_text: str, uptime: str, cpu: float, ram: float) -> str:
    """Карточка проекта в новом стиле."""
    # Прогресс-бар для CPU
    cpu_bar = _create_progress_bar(cpu, 100)
    
    # Извлекаем только иконку статуса
    status_icon = "🟢" if "running" in status_text.lower() else ("🔴" if "error" in status_text.lower() else "⚫")
    
    return f"""{status_icon} <b>{name}</b>

{server_text if server_text else '📍 Локальный сервер'}

📊 <b>Статистика</b>

⏱ Работает: {uptime}
💾 RAM: <b>{ram:.0f} MB</b>
⚡ CPU: <b>{cpu:.1f}%</b>
{cpu_bar}

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

BOT_SETTINGS_TEXT = """⚙️ <b>Настройки проекта</b>

Выбери, что хочешь настроить:"""

BOT_RENAME_TEXT = """📝 <b>Переименовать проект</b>

Введи новое название проекта:

<b>Правила:</b>
  • Только латиница, цифры, _ и -
  • От 1 до 50 символов

<b>Пример:</b> <code>my-telegram-bot</code>"""

BOT_DELETE_TEXT = (
    f"🗑 <b>Удаление ресурсов</b>\n\n"
    f"Внимание: данное действие полностью уничтожит выделенный контейнер. "
    f"Данные из локального хранилища будут удалены безвозвратно."
)

def bot_deleted_text(name: str) -> str:
    return (
        f"🗑 <b>Проект деинсталлирован</b>\n\n"
        f"Инфраструктура инстанса <b>{name}</b> успешно ликвидирована, слоты памяти освобождены."
    )


# ─── BOT PYTHON VERSION ───

BOT_PYTHON_TEXT = (
    f"🐍 <b>Смена версии интерпретатора</b>\n\n"
    f"После сохранения изменений проект выполнит автоматическую перезагрузку для применения нового рантайма."
)


# ─── BOT ENTRY POINT ───

def bot_entry_text(entry_type: str, entry_point: str) -> str:
    return (
        f"📄 <b>Корневой вектор выполнения</b>\n\n"
        f"Доступные архитектурные режимы:\n"
        f"• <b>Скрипт</b> — вызов одиночного файла (<code>python file.py</code>)\n"
        f"• <b>Модуль</b> — запуск изолированного пакета (<code>python -m</code>)\n\n"
        f"Активный режим: <b>{entry_type}</b>\n"
        f"Текущий путь: <code>{entry_point}</code>"
    )

BOT_ENTRY_MODULE_TEXT = (
    "📄 <b>Смена точки запуска</b>\n\n"
    "Выбран режим пакетного импорта (-m).\n\n"
    "Передайте имя целевого пакета.\n"
    "Пример структуры: <code>app.pkg.main</code>"
)

BOT_ENTRY_SELECT_FILE_TEXT = "Пожалуйста, определите исполняемый файл, используя интерактивный менеджер директорий."


# ─── BOT COOWNERS ───

def bot_coowners_text(name: str) -> str:
    return f"""👥 <b>Совместный доступ</b>

<b>Проект:</b> {name}

Дай доступ к проекту своим друзьям или коллегам.

<b>Что могут делать совладельцы:</b>
  ✅ Запускать и останавливать
  ✅ Смотреть логи
  ✅ Редактировать файлы
  ❌ Удалять проект
  ❌ Менять владельца

💡 <i>Только ты можешь удалить проект</i>"""

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

📊 <b>Мониторинг:</b>
  ⚡ CPU: <b>{cpu:.1f}%</b>
  {cpu_bar}
  💾 RAM: <b>{ram:.1f} MB</b>
  ⏱ Работает: <b>{uptime}</b>
  🔄 Перезапусков: <b>{restarts}</b>"""
    
    return f"""<b>{status_emoji} {name}</b>

Статус: {status_text}

🐍 Python: <b>{python_version}</b>
📄 Запуск: <code>{entry_point}</code>{stats_block}

Что хочешь сделать?"""


PROJECT_START_SUCCESS = "✅ <b>Проект запущен!</b>\n\nКонтейнер развернут и работает."
PROJECT_START_ERROR = "❌ <b>Ошибка запуска</b>\n\nПроверь логи для подробностей."
PROJECT_STOP_SUCCESS = "✅ <b>Проект остановлен</b>\n\nКонтейнер остановлен, данные сохранены."
PROJECT_STOP_ERROR = "❌ <b>Ошибка остановки</b>\n\nПопробуй ещё раз."
PROJECT_RESTART_SUCCESS = "🔄 <b>Проект перезапущен</b>\n\nКонтейнер перезагружен."
PROJECT_RESTART_ERROR = "❌ <b>Ошибка перезапуска</b>\n\nПроверь статус проекта."


# ─── BOT LOGS ───

def bot_logs_text(name: str, logs: str) -> str:
    """Логи проекта в новом стиле."""
    return f"""📋 <b>Логи проекта</b>

<b>{name}</b>

Последние 3500 символов:

<pre>{logs}</pre>

💡 <i>Используй "Скачать всё" для полного файла логов</i>"""


# ─── BOT FILES ───

def bot_files_text(project_name: str, path: str = "/app") -> str:
    """Файловый менеджер проекта."""
    return f"""📁 <b>Файлы: {project_name}</b>

📂 Текущая папка: <code>{path}</code>

Что можешь сделать:
  👁️ Просмотреть содержимое
  💾 Скачать файл
  🗑️ Удалить
  📤 Загрузить новые

💡 <i>Просто перетащи файл в чат для загрузки</i>"""


BOT_FILES_TEXT = bot_files_text("project", "/app")  # Для совместимости


def bot_files_path_text(path: str) -> str:
    return f"📁 <b>{path}</b>"


def bot_file_delete_confirm(file_path: str) -> str:
    return f"""🗑️ <b>Удалить файл?</b>

<code>{file_path}</code>

⚠️ <i>Это действие нельзя отменить!</i>"""


BOT_FILE_DELETE_CONFIRM_TEXT = bot_file_delete_confirm  # Для совместимости

BOT_FILE_DELETED_TEXT = "✅ Файл удалён"
BOT_FILE_DELETE_ERROR_TEXT = "❌ Не удалось удалить файл. Возможно, он используется."
BOT_FILE_NOT_FOUND_TEXT = "❌ Файл не найден"


# ─── BOT LIBRARIES ───

BOT_LIBS_TEXT = """📦 <b>Зависимости проекта</b>

Управляй Python библиотеками своего проекта:
  • Устанавливай новые
  • Удаляй ненужные
  • Обновляй версии

💡 <i>Библиотеки устанавливаются через pip</i>"""

BOT_LIB_ADD_TEXT = """📦 <b>Установка библиотеки</b>

Отправь название пакета из PyPI:

<b>Примеры:</b>
  • <code>aiogram</code>
  • <code>requests>=2.30.0</code>
  • <code>python-dotenv</code>

💡 <i>После установки проект нужно перезапустить</i>"""


# ─── SUBSCRIPTION ───

def subscription_text(is_premium: bool, projects_count: int = 0, max_projects: int = 3) -> str:
    """Экран подписки с персонализацией."""
    tariff_emoji = "🆓" if not is_premium else "💎"
    tariff_name = "Бесплатный" if not is_premium else "Premium"
    
    progress = _create_progress_bar(projects_count, max_projects)
    
    if is_premium:
        features = """<b>Твои возможности:</b>
  ✅ До 6 проектов одновременно
  ✅ 1 GB ОЗУ на проект
  ✅ 1.0 CPU на все проекты
  ✅ Приоритетная поддержка
  ✅ Автобэкапы каждый час"""
        tip = "💜 <i>Спасибо за поддержку!</i>"
    else:
        features = f"""<b>Твои возможности:</b>
  ✅ {max_projects} проект
  ✅ 256 MB ОЗУ
  ✅ 0.3 CPU на все проекты
  ✅ Базовая поддержка

<b>💎 Premium даёт:</b>
  🚀 В 6 раз больше проектов
  💪 В 4 раза больше ОЗУ
  ⚡ В 3 раза больше CPU
  💾 Автобэкапы каждый час"""
        tip = "💡 <i>Обнови до Premium для больших возможностей</i>"
    
    return f"""💳 <b>Твоя подписка</b>

{tariff_emoji} <b>Тариф:</b> {tariff_name}

📦 <b>Проекты:</b> {projects_count} из {max_projects}
{progress}

{features}

{tip}"""


SUBSCRIPTION_INFO_TEXT = None


def subscription_info_text() -> str:
    """Информация о Premium."""
    return """💎 <b>Обнови до Premium</b>

<b>Получи больше мощности для своих проектов:</b>

🚀 <b>До 6 проектов</b>
   Запускай сколько нужно

💪 <b>1 GB ОЗУ</b>
   В 4 раза больше ресурсов

⚡ <b>1.0 CPU</b>
   В 3 раза быстрее

💾 <b>Автобэкапы</b>
   Каждый час

🎯 <b>Быстрая поддержка</b>
   Ответим за 1 час

<b>💰 Стоимость:</b>
  • 1 неделя — 49₽
  • 1 месяц — 149₽
  • 3 месяца — 402₽ <i>(экономия 45₽)</i>
  • 6 месяцев — 759₽ <i>(экономия 135₽)</i>
  • 1 год — 1430₽ <i>(экономия 358₽)</i>

🎁 <b>Первая неделя всего 49₽!</b>
Можешь отменить в любой момент."""


SUBSCRIPTION_BUY_TEXT = """💳 <b>Выбери период подписки</b>

Чем дольше период — тем больше экономия!

💡 <i>После выбора покажем инструкцию по оплате</i>"""


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
    
    return f"""💎 <b>Premium {plan_label}</b>

<b>Стоимость:</b> {price}₽{savings_text}

<b>Что входит:</b>
  • До 6 проектов
  • 1 GB ОЗУ на проект
  • 1.0 CPU
  • Приоритетная поддержка
  • Автобэкапы каждый час

<b>Как оплатить:</b>
  1. Напиши @support_username
  2. Отправь: "Premium {plan_label}"
  3. Получи реквизиты для оплаты

<i>Подписка активируется автоматически после оплаты</i>"""


# ─── BACKUPS ───

BACKUPS_LIST_EMPTY_TEXT = (
    f"☁ <b>Снимки файловой системы</b>\n\n"
    f"Резервные копии отсутствуют, так как у вас нет активных вычислительных сред."
)

BACKUPS_LIST_TEXT = (
    f"☁ <b>Архив точек восстановления</b>\n\n"
    f"🟢 — Точка восстановления активна\n"
    f"🟡 — Выполняется архивация ресурсов\n"
    f"🔴 — Процесс архивации завершился критическим сбоем\n\n"
    f"Выберите нужный снимок из архива или инициализируйте создание новой копии:"
)

def backups_bot_text(name: str, count: int) -> str:
    return (
        f"☁ <b>Резервные копии инстанса: {name}</b>\n\n"
        f"Доступное количество архивов: {count}"
    )


# ─── ADMIN PANEL ───

def admin_panel_text(users: int, projects: int, servers: int) -> str:
    return (
        f"{Emoji.SETTINGS} <b>Консоль главного администратора</b>\n\n"
        f"{Emoji.PROFILE} Зарегистрированные аккаунты: {users}\n"
        f"{Emoji.FILE} Контейнеров в рантайме: {projects}\n"
        f"{Emoji.HOME} Доступные серверные ноды: {servers}"
    )

def admin_users_text(count: int) -> str:
    return f"{Emoji.PEOPLE} <b>Реестр пользователей системы</b> ({count})"

def admin_user_view_text(
    telegram_id: int, username: str, full_name: str,
    tariff: str, balance: float, is_banned: bool,
    projects_count: int, registered_at: str
) -> str:
    status = "🚫 Ограничен (Ban)" if is_banned else "✅ Активен"
    return (
        f"{Emoji.PROFILE} <b>Параметры профиля</b>\n\n"
        f"Telegram ID: <code>{telegram_id}</code>\n"
        f"Юзернейм: @{username or '—'}\n"
        f"Отображаемое имя: {full_name or '—'}\n"
        f"Текущий план: <b>{tariff}</b>\n"
        f"Финансовый баланс: <b>{balance:.2f}</b>\n"
        f"Статус доступа: {status}\n"
        f"Количество проектов: {projects_count}\n"
        f"Дата создания аккаунта: {registered_at}"
    )

def admin_servers_text(count: int) -> str:
    return f"{Emoji.HOME} <b>Управление вычислительными узлами</b> ({count})"

def admin_server_view_text(
    name: str, country: str, ip: str, port: int,
    api_key: bool, free_slots: int, total_slots: int,
    rating: float, ping: int, load_cpu: float, load_ram: float,
    status: str
) -> str:
    status_icon = "🟢 Сеть стабильна" if status == "online" else "🔴 Хост недоступен"
    api_key_text = "Активен" if api_key else "Выключен"
    return (
        f"{Emoji.HOME} <b>Спецификация ноды: {name}</b>\n\n"
        f"🌍 Локация: {country}\n"
        f"📡 Сетевой адрес: {ip}:{port}\n"
        f"🔑 Авторизация агента: {api_key_text}\n"
        f"💻 Заполненность слотов: {free_slots}/{total_slots}\n"
        f"⭐ Приоритет распределения: {rating:.1f}\n"
        f"📡 Сетевой пинг: {ping}ms\n"
        f"📊 Утилизация CPU: {load_cpu:.1f}%\n"
        f"🧠 Занятость RAM: {load_ram:.1f}%\n"
        f"Текущий статус: {status_icon}"
    )

def admin_stats_text(users: int, projects: int, active: int, servers: int, online: int) -> str:
    return (
        f"{Emoji.GRAPH_STATS} <b>Сводная системная аналитика</b>\n\n"
        f"👤 Всего профилей в БД: {users}\n"
        f"📦 Всего конфигураций: {projects}\n"
        f"🟢 Активных процессов: {active}\n"
        f"🌍 Общее число нод: {servers}\n"
        f"🟢 Серверов онлайн: {online}"
    )

def admin_promos_text(count: int) -> str:
    return f"{Emoji.GIFT} <b>Архив промо-кодов</b> ({count})"

def admin_subscriptions_text(free_count: int, premium_count: int, total: int) -> str:
    return (
        f"💎 <b>Распределение тарифных планов</b>\n\n"
        f"🆓 Базовые аккаунты: {free_count}\n"
        f"💎 Премиум лицензии: {premium_count}\n"
        f"Всего пользователей: {total}"
    )

def admin_referrals_text(count: int) -> str:
    return (
        f"🔗 <b>Статистика партнерской сети</b>\n\n"
        f"Общее количество реферальных связей: {count}"
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
        f"{Emoji.GRAPH_STATS} <b>Телеметрия ресурсов инстанса: {name}</b>\n\n"
        f"Состояние контейнера: {status_text}\n"
        f"Нагрузка на ядро CPU: <b>{cpu:.1f}%</b>\n"
        f"Выделенная память RAM: <b>{ram:.1f} MB</b>\n"
        f"Объем дискового пространства: <b>{disk:.1f} MB</b>\n"
        f"Uptime текущей сессии: <b>{uptime}</b>\n"
        f"Количество аварийных перезапусков: <b>{restarts}</b>"
    )

def project_graphs_text(hours: int, avg_cpu: float, max_cpu: float, avg_ram: float, max_ram: float, data_points: int) -> str:
    return (
        f"{Emoji.GRAPH_UP} <b>Агрегированная статистика за интервал {hours}ч</b>\n\n"
        f"{Emoji.GRAPH_STATS} Вычислительная мощность (CPU):\n"
        f"  Медианное значение: {avg_cpu:.1f}%\n"
        f"  Пиковый всплеск: {max_cpu:.1f}%\n\n"
        f"{Emoji.GRAPH_UP} Оперативная память (RAM):\n"
        f"  Среднее заполнение: {avg_ram:.1f} MB\n"
        f"  Максимальная аллокация: {max_ram:.1f} MB\n\n"
        f"{Emoji.INFO} Всего обработано маркеров телеметрии: {data_points}"
    )

ERROR_NO_STATS_DATA = "За выбранный хронологический период метрики отсутствуют в базе данных."


# ─── PROJECT SETTINGS ───

def project_settings_text(name: str, python_version: str, entry_point: str, entry_type: str) -> str:
    return (
        f"{Emoji.SETTINGS} <b>Спецификация конфигурации: {name}</b>\n\n"
        f"Версия интерпретатора: Python {python_version}\n"
        f"Исполняемый маркер: <code>{entry_point}</code>\n"
        f"Архитектура вызова: {entry_type}"
    )

PROJECT_PYTHON_SELECT_TEXT = f"{Emoji.SETTINGS} Укажите необходимую версию изолированной среды Python:"
PROJECT_ENTRY_INPUT_TEXT = f"{Emoji.PENCIL} Задайте новый корневой скрипт или пространство имен модуля:"
PROJECT_SETTINGS_USE_CARD = "Синхронизировать параметры со стандартной конфигурационной схемой проекта"


# ─── PROJECT LOGS ───

def project_logs_menu_text(name: str) -> str:
    return f"""📋 <b>Логи проекта</b>

<b>{name}</b>

Что хочешь сделать?"""

def project_logs_view_text(logs: str) -> str:
    return f"""📋 <b>Логи проекта</b>

Последние 100 строк:

<pre>{logs}</pre>

💡 <i>Используй "Скачать" для полного файла</i>"""

def project_logs_file_caption(name: str) -> str:
    return f"📄 Логи проекта <b>{name}</b>"

PROJECT_LOGS_CLEARED = "✅ Логи очищены"
PROJECT_LOGS_CLEAR_ERROR = "❌ Не удалось очистить логи. Попробуй ещё раз."


# ─── PROJECT MANAGE ───

def project_delete_confirm_text(name: str) -> str:
    return (
        f"{Emoji.TRASH} <b>Уничтожение изолированной среды</b>\n\n"
        f"Вы собираетесь полностью удалить инстанс <b>{name}</b>.\n"
        f"Это сотрет все ассоциированные контейнеры и локальные папки без возможности восстановления."
    )

PROJECT_DELETED_TEXT = f"{Emoji.CHECK} Виртуальное окружение проекта успешно ликвидировано."
PROJECT_DELETE_ERROR = "Критический сбой API при попытке деинсталлировать контейнер."


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
    
    return f"""👤 <b>Твой профиль</b>

<b>@{username}</b>

📦 <b>Проекты:</b> {projects_count} из {max_projects}
{progress_bar}

{tariff_icon} <b>Тариф:</b> {tariff_name}

💰 <b>Баланс:</b> {balance:.2f}₽

🔗 <b>Реферальная ссылка:</b>
<code>{referral_link}</code>

💡 <i>Приглашай друзей и получай бонусы!</i>"""


SETTINGS_NOT_FOUND = "❌ Настройки не найдены"
SETTINGS_UNKNOWN = "❌ Неизвестная настройка"
SETTINGS_CHANGED = "✅ Настройка изменена"


def notification_settings_text() -> str:
    """Настройки уведомлений."""
    return f"""🔔 <b>Уведомления</b>

Выбери, о чём хочешь получать уведомления:

<b>📊 Статус проектов:</b>
  • Проект запущен
  • Проект остановлен
  • Ошибка запуска

<b>⚠️ Проблемы:</b>
  • Высокая нагрузка CPU
  • Нехватка памяти
  • Мало места на диске

<b>📦 Бэкапы и обновления:</b>
  • Бэкап создан
  • Обновление установлено

💡 <i>Нажми на кнопку чтобы включить/выключить</i>"""


# ─── LOCATIONS ───

LOCATIONS_NO_SERVERS = f"{Emoji.HOME} <b>Вычислительные кластеры</b>\n\nДоступные физические серверные ноды отсутствуют."
LOCATIONS_SERVERS_TEXT = f"{Emoji.HOME} <b>Список активных серверных узлов</b>"
LOCATION_NOT_FOUND = "Выбранный физический сервер не отвечает на запросы кластера."


# ─── SUBSCRIPTION ───

SUBSCRIPTION_PLAN_UNKNOWN = "Запрошена неподдерживаемая или архивная тарифная сетка."

def subscription_buy_confirm_text(plan_label: str, price: int) -> str:
    return (
        f"💳 <b>Активация подписки</b>\n\n"
        f"Выбранный тарифный план: <b>Premium {plan_label}</b>\n"
        f"Фиксированная стоимость: <b>{price}₽</b>\n\n"
        f"Для генерации платежной сессии и проведения транзакции перейдите в диалог с биллингом."
    )


# ─── COOWNERS ───

COOWNER_ENTER_ID = """👥 <b>Добавить совладельца</b>

Отправь <b>Telegram ID</b> пользователя.

<b>Как узнать ID:</b>
  1. Пусть человек напишет @userinfobot
  2. Бот ответит с его ID
  3. Отправь это число сюда

<b>Пример:</b> <code>123456789</code>

💡 <i>Пользователь должен хотя бы раз запустить бота</i>"""

COOWNER_REMOVED = "✅ Доступ отозван"
COOWNER_INVALID_ID = "❌ <b>Неверный формат</b>\n\nID должен быть числом."
COOWNER_SELF_ADD = "❌ <b>Нельзя добавить себя</b>\n\nТы уже владелец проекта."
COOWNER_USER_NOT_FOUND = "❌ <b>Пользователь не найден</b>\n\nОн должен сначала запустить бота."
COOWNER_ALREADY_EXISTS = "❌ <b>Уже добавлен</b>\n\nЭтот пользователь уже имеет доступ."

def coowner_added_text(username: str) -> str:
    return f"✅ <b>Доступ предоставлен!</b>\n\n<b>{username}</b> теперь может управлять этим проектом."


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
        f"📄 <b>Параметр вызова: {entry}</b>\n\n"
        f"Утвердите выбранную точку входа. Изменение сценария запуска доступно в панели управления проектом."
    )

def bot_create_confirm_text(name: str, python: str, entry: str) -> str:
    return (
        f"{Emoji.CHECK} <b>Верификация архитектурной схемы деплоя</b>\n\n"
        f"📝 Проект: <b>{name}</b>\n"
        f"🐍 Рантайм: Python {python}\n"
        f"📄 Инициализатор: <code>{entry}</code>\n\n"
        f"Запустить компиляцию образов и сборку проекта?"
    )

BOT_CREATE_SUCCESS_TEXT = (
    f"🤖 <b>Оркестрация контейнера завершена успешно!</b>\n\n"
    f"Ваш сервис переведен в рабочую фазу выполнения на удаленном узле.\n\n"
    f"Используйте главный дашборд для администрирования параметров рантайма."
)


# ─── ADMIN ───

ADMIN_NO_ACCESS = "⛔ Критическая ошибка авторизации. Требуются root-привилегии суперпользователя."
ADMIN_USER_NOT_FOUND = "Запрошенная учетная запись пользователя отсутствует в глобальной базе данных."
ADMIN_SERVER_NOT_FOUND = "Выбранный физический узел инфраструктуры не зарегистрирован в системе."
ADMIN_SERVER_DELETED = "Вычислительный узел успешно выведен из кластера и удален."
ADMIN_REFERRAL_WIP = "Компонент реферального трекинга находится на стадии разработки и закрытого тестирования."

ADMIN_USER_BANNED = "🚫 К аккаунту применены санкции перманентного ограничения доступа (Ban)"
ADMIN_USER_UNBANNED = "✅ Ограничения доступа с учетной записи пользователя полностью сняты"
ADMIN_TARIFF_CHANGED = lambda tariff: f"✅ Тарифный план учетной записи успешно изменен на {tariff}"
ADMIN_BALANCE_INPUT_ERROR = "❌ Неверный тип данных. Система ожидает исключительно числовой формат формата float/int:"
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
    return f"{Emoji.TRASH} Вы действительно хотите деинсталлировать физический сервер <b>{name}</b> из инфраструктуры?"

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

SUCCESS_BACKUP_CREATED = "☁ Актуальный снимок системы успешно сгенерирован и отправлен в облачный репозиторий!"

def success_entry_changed(entry: str) -> str:
    return f"{Emoji.CHECK} Архитектурный маркер вызова процесса изменен на: <code>{entry}</code>"

def success_python_changed(version: str) -> str:
    return f"✅ Среда рантайма переключена на интерпретатор Python {version}"

def success_balance_changed(amount: float, balance: float) -> str:
    return f"✅ Финансовая транзакция проведена. Изменение: {amount:.2f} | Текущий остаток на счете: {balance:.2f}"