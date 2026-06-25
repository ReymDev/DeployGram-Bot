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
    
    return f"""╔══════════════════════════════════════╗
║  🚀 <b>DeployGram</b>
╚══════════════════════════════════════╝

{greeting}, <b>{username}</b>!

Здесь ты можешь запустить свой Python проект в облаке за пару минут — без настройки серверов и сложных команд.

{stats_text}

💡 <i>Загрузи код, нажми "Запустить" — и готово!</i>"""


CONTROL_PANEL_TEXT = """╭─────────────────────────────────────╮
│  📱 <b>Мои проекты</b>
╰─────────────────────────────────────╯

Выбери проект для управления:"""


EMPTY_PROJECTS = """📭 <b>Пока пусто</b>

Создай свой первый проект прямо сейчас!

Это займёт всего 2 минуты:
  ① Загрузи код
  ② Выбери Python версию
  ③ Запусти

<i>Не волнуйся — мы поможем на каждом шаге 😊</i>"""


# ─── ADD BOT: SOURCE ───

ADD_BOT_SOURCE_TEXT = """╔══════════════════════════════════════╗
║  ✨ <b>Новый проект</b>
╚══════════════════════════════════════╝

Запусти свой Python проект в 3 шага:

<b>Шаг 1</b> → Загрузи код
<b>Шаг 2</b> → Настрой запуск  
<b>Шаг 3</b> → Готово! 🚀

Начнём с загрузки кода. Выбери удобный способ:"""

ADD_BOT_ZIP_TEXT = """╭─────────────────────────────────────╮
│  📦 <b>Шаг 1:</b> Загрузка кода
╰─────────────────────────────────────╯

Отправь ZIP-архив со своим проектом.

<b>Что должно быть внутри:</b>
  ✓ Файлы Python (*.py)
  ✓ requirements.txt с зависимостями
  ✓ Другие файлы проекта

<b>Ограничения:</b>
  • Максимум 100 МБ
  • Формат: только .zip

💡 <i>Не знаешь как упаковать? Просто выдели все файлы проекта → ПКМ → "Отправить" → "Сжатая ZIP-папка"</i>"""

ADD_BOT_GITHUB_TEXT = """╭─────────────────────────────────────╮
│  🔗 <b>Шаг 1:</b> GitHub репозиторий
╰─────────────────────────────────────╯

Вставь ссылку на публичный GitHub репозиторий.

<b>Формат:</b>
<code>https://github.com/username/project</code>

Мы автоматически склонируем код и развернём его.

💡 <i>Репозиторий должен быть публичным или у нас должен быть доступ</i>"""


# ─── ADD BOT: PYTHON VERSION ───

def add_bot_python_text(uploaded_file: str = "") -> str:
    """Выбор версии Python."""
    file_text = f"✅ Код загружен: <code>{uploaded_file}</code>\n\n" if uploaded_file else ""
    
    return f"""╭─────────────────────────────────────╮
│  🐍 <b>Шаг 2:</b> Версия Python
╰─────────────────────────────────────╯

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

ADD_BOT_ENTRY_TEXT = """╭─────────────────────────────────────╮
│  🎯 <b>Шаг 3:</b> Точка входа
╰─────────────────────────────────────╯

<b>Какой файл запускать?</b>

Это главный файл, с которого начинается твой проект.

<b>Обычно это:</b>
  • <code>main.py</code>
  • <code>bot.py</code>
  • <code>app.py</code>
  • <code>run.py</code>

💡 <i>Мы попробуем найти его автоматически, но можешь выбрать вручную</i>"""

def add_bot_entry_script_text(filter: str = "*.py") -> str:
    return f"""╭─────────────────────────────────────╮
│  📄 <b>Шаг 3:</b> Выбор файла
╰─────────────────────────────────────╯

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
    
    return f"""╭─────────────────────────────────────╮
│ {status_icon} <b>{name}</b>
├─────────────────────────────────────┤
│ {server_text if server_text else 'Локальный сервер'}
│ 
│ 📊 <b>Статистика</b>
│ 
│ ⏱ Работает: {uptime}
│ 💾 RAM: <b>{ram:.0f} MB</b>
│ ⚡ CPU: <b>{cpu:.1f}%</b>
│ {cpu_bar}
╰─────────────────────────────────────╯

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

BOT_SETTINGS_TEXT = """╭─────────────────────────────────────╮
│  ⚙️ <b>Настройки проекта</b>
╰─────────────────────────────────────╯

Выбери, что хочешь настроить:"""

BOT_RENAME_TEXT = """╭─────────────────────────────────────╮
│  📝 <b>Переименовать проект</b>
╰─────────────────────────────────────╯

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
    return (
        f"👥 <b>Управление уровнями доступа: {name}</b>\n\n"
        f"Градация ролей в системе:\n"
        f"  <b>Owner</b> — абсолютные административные права, управление квотами и балансом.\n"
        f"  <b>Developer</b> — контроль жизненного цикла процессов, работа с логами и файловой системой."
    )

BOT_COOWNER_ADD_TEXT = "👤 Введите уникальный Telegram ID пользователя для делегирования полномочий:"
BOT_COOWNER_ADD_ROLE_TEXT = "👤 Определите системную роль для добавляемого специалиста:"

def bot_coowner_added_text(user_id: int, role: str) -> str:
    return f"{Emoji.CHECK} Идентификатору {user_id} успешно присвоен статус {role}."

def bot_coowner_deleted_text(user_id: int) -> str:
    return f"{Emoji.CHECK} Права доступа для пользователя {user_id} полностью отозваны."

BOT_COOWNER_NOT_FOUND_TEXT = "Заданный идентификатор отсутствует в реестре пользователей платформы."
BOT_COOWNER_ALREADY_EXISTS_TEXT = "Данный пользователь уже включен в список соавторов этого проекта."


# ─── BOT LOGS ───

def bot_logs_text(name: str, logs: str) -> str:
    """Логи проекта в новом стиле."""
    return f"""╭─────────────────────────────────────╮
│  📋 <b>Логи проекта</b>
╰─────────────────────────────────────╯

<b>{name}</b>

Последние 3500 символов:

<code>{logs}</code>

💡 <i>Используй "Скачать всё" для полного файла логов</i>"""


# ─── BOT FILES ───

BOT_FILES_TEXT = """╭─────────────────────────────────────╮
│  📁 <b>Файловый менеджер</b>
╰─────────────────────────────────────╯

Здесь можно:
  • 👁️ Просматривать файлы
  • 💾 Скачивать
  • 🗑️ Удалять
  • ➕ Загружать новые

💡 <i>Просто перетащи файлы в чат для загрузки</i>"""

def bot_files_path_text(path: str) -> str:
    return f"📁 <b>Рабочая область: {path}</b>"

BOT_FILE_DELETE_CONFIRM_TEXT = lambda file_path: f"🗑 Вы действительно хотите окончательно удалить объект <b>{file_path}</b>?"
BOT_FILE_DELETED_TEXT = "Файл успешно удален из хранилища инстанса."
BOT_FILE_DELETE_ERROR_TEXT = "Не удалось выполнить операцию удаления. Объект заблокирован процессом."
BOT_FILE_NOT_FOUND_TEXT = "Запрошенный путь пуст или не существует в данной директории."


# ─── BOT LIBRARIES ───

BOT_LIBS_TEXT = """╭─────────────────────────────────────╮
│  📦 <b>Зависимости проекта</b>
╰─────────────────────────────────────╯

Управляй Python библиотеками своего проекта:
  • Устанавливай новые
  • Удаляй ненужные
  • Обновляй версии

💡 <i>Библиотеки устанавливаются через pip</i>"""

BOT_LIB_ADD_TEXT = """╭─────────────────────────────────────╮
│  📦 <b>Установка библиотеки</b>
╰─────────────────────────────────────╯

Отправь название пакета из PyPI:

<b>Примеры:</b>
  • <code>aiogram</code>
  • <code>requests>=2.30.0</code>
  • <code>python-dotenv</code>

💡 <i>После установки проект нужно перезапустить</i>"""


# ─── SUBSCRIPTION ───

def subscription_text(is_premium: bool) -> str:
    from models.subscription import get_free_features, get_premium_features
    if is_premium:
        features = get_premium_features()
        features_text = "\n".join(f"· {f}" for f in features)
        return (
            f"💳 <b>Аналитика тарифного плана</b>\n\n"
            f"Текущий статус: {Emoji.CHECK} Premium Лицензия\n\n"
            f"<b>Доступные расширенные лимиты:</b>\n{features_text}"
        )
    features = get_free_features()
    features_text = "\n".join(f"· {f}" for f in features)
    return (
        f"💳 <b>Аналитика тарифного плана</b>\n\n"
        f"Текущий статус: {Emoji.CHECK} Базовый доступ\n\n"
        f"<b>Действующие ограничения аккаунта:</b>\n{features_text}"
    )

SUBSCRIPTION_INFO_TEXT = None


def subscription_info_text() -> str:
    from models.subscription import get_premium_features
    features = get_premium_features()
    features_text = "\n".join(f"· {f}" for f in features)
    return (
        f"💳 <b>Спецификация Premium-лицензии</b>\n\n"
        f"<b>{Emoji.NOTIF} Преимущества коммерческого плана:</b>\n{features_text}"
    )

SUBSCRIPTION_BUY_TEXT = (
    f"💳 <b>Пролонгация и смена тарифа</b>\n\n"
    f"Выберите необходимый расчетный период для активации облачных преимуществ:"
)

def subscription_buy_plan_text(plan_label: str, price: int) -> str:
    return (
        f"💳 <b>Оплата коммерческого плана</b>\n\n"
        f"Конфигурация: <b>Premium {plan_label}</b>\n"
        f"Итого к оплате: <b>{price}₽</b>\n\n"
        f"Для выставления инвойса и проведения транзакции свяжитесь с биллинг-менеджером."
    )


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
    return f"{Emoji.FILE} <b>Терминал логирования: {name}</b>"

def project_logs_view_text(logs: str) -> str:
    return f"<b>📋 Поток вывода stdout/stderr процессов:</b>\n\n<code>{logs}</code>"

def project_logs_file_caption(name: str) -> str:
    return f"Системный дамп логов для инстанса {name}"

PROJECT_LOGS_CLEARED = "Буфер вывода терминала успешно сброшен."
PROJECT_LOGS_CLEAR_ERROR = "Ошибка подсистемы при попытке очистить буфер логов."


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

SETTINGS_NOT_FOUND = "Конфигурационный профиль текущей сессии не обнаружен."
SETTINGS_UNKNOWN = "Запрошен недокументированный или устаревший параметр."
SETTINGS_CHANGED = "Системная конфигурация успешно обновлена."

def notification_settings_text() -> str:
    return f"{Emoji.NOTIF} <b>Конфигурация каналов push-оповещений и триггеров алертов</b>"


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

COOWNER_ENTER_ID = f"{Emoji.PROFILE} Передайте уникальный числовой Telegram ID аккаунта для авторизации доступа:"
COOWNER_REMOVED = "Права совместного администрирования инстанса отозваны."
COOWNER_INVALID_ID = "❌ Ошибка валидации. Идентификатор аккаунта должен состоять исключительно из числовых символов."
COOWNER_SELF_ADD = "❌ Недопустимое действие. Вы не можете делегировать права самому себе."
COOWNER_USER_NOT_FOUND = "❌ Пользователь не обнаружен. Ему необходимо пройти первичный процесс авторизации на нашей платформе."
COOWNER_ALREADY_EXISTS = "❌ Данный специалист уже авторизован в списке разработчиков этого инстанса."

def coowner_added_text(username: str) -> str:
    return f"{Emoji.CHECK} Пользователю <b>{username}</b> успешно делегированы права соавтора проекта."


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