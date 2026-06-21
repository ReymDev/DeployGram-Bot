from __future__ import annotations

from bot.utils.emojis import Emoji


# ─── WELCOME ───

def welcome_text(username: str) -> str:
    from bot.config import settings
    return (
        f"{Emoji.SMILE} <b>Добро пожаловать!</b>\n\n"
        f"Привет, это <b>{settings.BOT_NAME}</b> - дом для твоих ботов!\n\n"
        f"Здесь ты можешь бесплатно захостить свой код или запустить "
        f"готовый пресет всего за пару кликов.\n\n"
        f"Начиная работу, ты принимаешь наши <a href=\"#\">условия</a> "
        f"и <a href=\"#\">политику</a>."
    )

CONTROL_PANEL_TEXT = (
    f"📋 <b>Панель управления</b>\n\n"
    f"Нажми на кнопку с названием бота, чтобы управлять им."
)


# ─── ADD BOT: SOURCE ───

ADD_BOT_SOURCE_TEXT = (
    f"📥 <b>(1/4) Откуда загружаем?</b>\n\n"
    f"Ты можешь загрузить свой код или попробовать пресеты - "
    f"готовых ботов от других пользователей."
)

ADD_BOT_ZIP_TEXT = (
    f"📥 <b>(3/4) Загрузка файлов</b>\n\n"
    f"Отправь .zip архив с файлами, положи requirements.txt в корень, "
    f"если хочешь, чтобы я установил зависимости сразу. "
    f"Либо сможешь сделать это позже в панели."
)

ADD_BOT_GITHUB_TEXT = (
    f"🔗 <b>(3/4) Подключение Github</b>\n\n"
    f"Для первого деплоя с GitHub нажми \"Подключить GitHub\".\n"
    f"Выбери доступ ко всем репо для удобства или только к нужному.\n\n"
    f"Выбери репозиторий из списка ниже:"
)


# ─── ADD BOT: PYTHON VERSION ───

ADD_BOT_PYTHON_TEXT = (
    f"🐍 <b>(2/4) Версия Python</b>\n"
    f"<i>Для Legacy-проектов с aiogram 2.x подойдет 3.10</i>\n\n"
    f"На какой версии будет запущен твой код?"
)


# ─── ADD BOT: ENTRY POINT ───

ADD_BOT_ENTRY_TEXT = (
    f"📄 <b>(4/4) Выбор точки входа</b>\n\n"
    f"Выбери режим запуска:\n"
    f"• <b>Скрипт</b> - для <code>python file.py</code>\n"
    f"• <b>Модуль</b> - для <code>python -m package.module</code>"
)

def add_bot_entry_script_text(filter: str = "*.py") -> str:
    return (
        f"📄 <b>(4/4) Выбор точки входа</b>\n"
        f"<i>Режим: Скриптовый запуск / python <code>file.py</code></i>\n"
        f"<i>Фильтр: {filter}</i>\n\n"
        f"Выбери файл, который ты обычно запускаешь, чтобы твой бот начал работать:"
    )

ADD_BOT_ENTRY_MODULE_TEXT = (
    "📄 <b>Выбор точки входа</b>\n\n"
    "Режим: Модульный запуск / python -m\n\n"
    "Отправь имя модуля вручную.\n"
    "Примеры: <code>app.pkg.main</code>"
)

ADD_BOT_ENTRY_MANUAL_TEXT = (
    "📄 <b>Выбор точки входа</b>\n\n"
    "Отправь имя файла вручную.\n"
    "Пример: <code>main.py</code>"
)

def add_bot_entry_confirm_text(entry: str) -> str:
    return (
        f"📄 <b>(4/4) Выбор точки входа</b>\n\n"
        f"📄 <code>{entry}</code>\n\n"
        f"Подтверди выбор точки входа, ты сможешь изменить ее позже."
    )


# ─── ADD BOT: SERVER SELECTION ───

ADD_BOT_SERVER_TEXT = (
    f"🖥 <b>Выбор сервера</b>\n\n"
    f"Выбери сервер, на котором будет развернут твой бот:"
)

ADD_BOT_SERVER_POOL_TEXT = "[ Free-пул слотов ]"


# ─── ADD BOT: CONFIRM ───

def add_bot_confirm_text(name: str, python_version: str, entry_point: str) -> str:
    return (
        f"{Emoji.CHECK} <b>Подтверждение</b>\n\n"
        f"📝 Название: <b>{name}</b>\n"
        f"🐍 Python: {python_version}\n"
        f"📄 Вход: <code>{entry_point}</code>\n\n"
        f"Создать бота?"
    )

ADD_BOT_NAME_TEXT = "📝 Введи название для бота (1-50 символов, буквы, цифры, _ -):"


# ─── ADD BOT: SUCCESS ───

ADD_BOT_SUCCESS_TEXT = (
    f"🤖 <b>Твой бот готов к работе!</b>\n\n"
    f"Твой бот запущен!\n\n"
    f"Вернись в меню, чтобы управлять им. Тебе доступны: просмотр "
    f"логов. Запуск и остановка, файловый менеджер и установка библиотек."
)


# ─── BOT CONTROL ───

def bot_control_text(name: str, server_text: str, status_text: str, uptime: str, cpu: float, ram: float) -> str:
    return (
        f"📋 <b>Панель управления</b>\n\n"
        f"<b>{name}</b>\n"
        f"{server_text}\n\n"
        f"{status_text} · Аптайм: {uptime}\n"
        f"CPU: {cpu:.2f}% · RAM: {ram:.2f}%"
    )


# ─── BOT SETTINGS ───

BOT_SETTINGS_TEXT = (
    f"⚙ <b>Настройки бота</b>\n\n"
    f"Выбери, что хочешь сделать с ботом:"
)

BOT_RENAME_TEXT = "✏ <b>Смена названия</b>\n\nВведи новое название для бота:"

BOT_DELETE_TEXT = (
    f"🗑 <b>Удаление бота</b>\n\n"
    f"Подтверди удаление бота, восстановить доступ к нему будет "
    f"невозможно - только загрузить заново."
)

def bot_deleted_text(name: str) -> str:
    return (
        f"🗑 <b>Удаление бота</b>\n\n"
        f"Бот <b>{name}</b> удален."
    )


# ─── BOT PYTHON VERSION ───

BOT_PYTHON_TEXT = (
    f"🐍 <b>Смена версии Python</b>\n\n"
    f"Бот перезапустится после смены версии."
)


# ─── BOT ENTRY POINT ───

def bot_entry_text(entry_type: str, entry_point: str) -> str:
    return (
        f"📄 <b>Смена точки входа</b>\n\n"
        f"Выбери режим запуска:\n"
        f"• <b>Скрипт</b> - для <code>python file.py</code>\n"
        f"• <b>Модуль</b> - для <code>python -m package.module</code>\n\n"
        f"Текущий режим: <b>{entry_type}</b>\n"
        f"Текущее значение: <b>{entry_point}</b>"
    )


# ─── BOT LOGS ───

def bot_logs_text(name: str, logs: str) -> str:
    return (
        f"📋 Логи <b>{name}</b> (последние 3500 симв.)\n\n"
        f"<code>{logs}</code>"
    )


# ─── BOT FILES ───

BOT_FILES_TEXT = (
    f"📁 <b>Файловый менеджер</b>\n\n"
    f"Чтобы загрузить новый файл - отправь его, он попадет "
    f"в открытую директорию заменой. Если файлов несколько, "
    f"пришли их архивом, он будет распакован."
)


# ─── BOT LIBRARIES ───

BOT_LIBS_TEXT = (
    f"📦 <b>Менеджер библиотек</b>\n\n"
    f"Тут находятся все твои библиотеки, можешь установить новые "
    f"или удалить текущие."
)

BOT_LIB_ADD_TEXT = (
    "📦 <b>Установка библиотеки</b>\n\n"
    "Отправь название библиотеки.\n"
    "Примеры: <code>aiogram</code>, <code>requests>=2.0</code>"
)


# ─── SUBSCRIPTION ───

def subscription_text(is_premium: bool) -> str:
    from models.subscription import get_free_features, get_premium_features
    if is_premium:
        features = get_premium_features()
        features_text = "\n".join(f"· {f}" for f in features)
        return (
            f"💳 <b>Управление подпиской</b>\n\n"
            f"Статус: {Emoji.CHECK} Premium\n\n"
            f"<b>Premium</b>\n{features_text}"
        )
    features = get_free_features()
    features_text = "\n".join(f"· {f}" for f in features)
    return (
        f"💳 <b>Управление подпиской</b>\n\n"
        f"Статус: {Emoji.CHECK} Free\n\n"
        f"<b>Free</b>\n{features_text}"
    )

SUBSCRIPTION_INFO_TEXT = None  # Will be generated dynamically


def subscription_info_text() -> str:
    from models.subscription import get_premium_features
    features = get_premium_features()
    features_text = "\n".join(f"· {f}" for f in features)
    return (
        f"💳 <b>Преимущества подписки</b>\n\n"
        f"<b>{Emoji.NOTIF} Premium</b>\n{features_text}"
    )

SUBSCRIPTION_BUY_TEXT = (
    f"💳 <b>Покупка/продление подписки</b>\n\n"
    f"На какой срок ты хочешь приобрести подписку?"
)

def subscription_buy_plan_text(plan_label: str, price: int) -> str:
    return (
        f"💳 <b>Покупка подписки</b>\n\n"
        f"Ты выбрал: <b>Premium {plan_label}</b>\n"
        f"Цена: <b>{price}₽</b>\n\n"
        f"Для оплаты свяжитесь с администратором."
    )


# ─── BACKUPS ───

BACKUPS_LIST_EMPTY_TEXT = (
    f"☁ <b>Список бэкапов</b>\n\n"
    f"У тебя пока нет ботов."
)

BACKUPS_LIST_TEXT = (
    f"☁ <b>Список бэкапов</b>\n\n"
    f"🟢 - Бэкап создан\n"
    f"🟡 - Бэкап создается\n"
    f"🔴 - Возникла ошибка при создании бэкапа\n\n"
    f"Выбери существующий бэкап или создай новый:"
)

def backups_bot_text(name: str, count: int) -> str:
    return (
        f"☁ <b>Бэкапы: {name}</b>\n\n"
        f"Количество: {count}"
    )


# ─── ADMIN PANEL ───

def admin_panel_text(users: int, projects: int, servers: int) -> str:
    return (
        f"{Emoji.SETTINGS} <b>Админ-панель</b>\n\n"
        f"{Emoji.PROFILE} Пользователей: {users}\n"
        f"{Emoji.FILE} Проектов: {projects}\n"
        f"{Emoji.HOME} Серверов: {servers}"
    )

def admin_users_text(count: int) -> str:
    return f"{Emoji.PEOPLE} <b>Пользователи</b> ({count})"

def admin_user_view_text(
    telegram_id: int, username: str, full_name: str,
    tariff: str, balance: float, is_banned: bool,
    projects_count: int, registered_at: str
) -> str:
    status = "🚫 Забанен" if is_banned else "✅ Активен"
    return (
        f"{Emoji.PROFILE} <b>Пользователь</b>\n\n"
        f"ID: <code>{telegram_id}</code>\n"
        f"Username: @{username or '—'}\n"
        f"Имя: {full_name or '—'}\n"
        f"Тариф: <b>{tariff}</b>\n"
        f"Баланс: <b>{balance:.2f}</b>\n"
        f"Статус: {status}\n"
        f"Проектов: {projects_count}\n"
        f"Регистрация: {registered_at}"
    )

def admin_servers_text(count: int) -> str:
    return f"{Emoji.HOME} <b>Серверы</b> ({count})"

def admin_server_view_text(
    name: str, country: str, ip: str, port: int,
    api_key: bool, free_slots: int, total_slots: int,
    rating: float, ping: int, load_cpu: float, load_ram: float,
    status: str
) -> str:
    status_icon = "🟢 Онлайн" if status == "online" else "🔴 Оффлайн"
    api_key_text = "Есть" if api_key else "Нет"
    return (
        f"{Emoji.HOME} <b>{name}</b>\n\n"
        f"🌍 Страна: {country}\n"
        f"📡 IP: {ip}:{port}\n"
        f"🔑 API Key: {api_key_text}\n"
        f"💻 Слоты: {free_slots}/{total_slots}\n"
        f"⭐ Рейтинг: {rating:.1f}\n"
        f"📡 Пинг: {ping}ms\n"
        f"📊 CPU: {load_cpu:.1f}%\n"
        f"🧠 RAM: {load_ram:.1f}%\n"
        f"Статус: {status_icon}"
    )

def admin_stats_text(users: int, projects: int, active: int, servers: int, online: int) -> str:
    return (
        f"{Emoji.GRAPH_STATS} <b>Статистика</b>\n\n"
        f"👤 Пользователей: {users}\n"
        f"📦 Всего проектов: {projects}\n"
        f"🟢 Активных: {active}\n"
        f"🌍 Серверов: {servers}\n"
        f"🟢 Онлайн: {online}"
    )

def admin_promos_text(count: int) -> str:
    return f"{Emoji.GIFT} <b>Промокоды</b> ({count})"

def admin_subscriptions_text(free_count: int, premium_count: int, total: int) -> str:
    return (
        f"💎 <b>Подписки</b>\n\n"
        f"🆓 Free: {free_count}\n"
        f"💎 Premium: {premium_count}\n"
        f"Всего: {total}"
    )

def admin_referrals_text(count: int) -> str:
    return (
        f"🔗 <b>Рефералы</b>\n\n"
        f"Всего рефералов: {count}"
    )


# ─── ADMIN: SERVER ADD ───

ADMIN_SERVER_ADD_NAME = f"{Emoji.HOME} Введите название сервера:"
ADMIN_SERVER_ADD_COUNTRY = f"{Emoji.HOME} Введите страну сервера:"
ADMIN_SERVER_ADD_IP = f"{Emoji.HOME} Введите IP адрес сервера:"
ADMIN_SERVER_ADD_API_KEY = f"{Emoji.HOME} Введите API ключ агента (или - если без ключа):"
ADMIN_SERVER_ADD_SLOTS = f"{Emoji.HOME} Введите количество слотов:"

ADMIN_SERVER_ADD_CHECKING = f"{Emoji.LOADING} <b>Проверяю подключение к агенту...</b>"

def admin_server_add_success(name: str, country: str, ip: str, slots: int, api_key: str) -> str:
    return (
        f"✅ <b>Сервер {name} успешно добавлен!</b>\n\n"
        f"🌍 Страна: {country}\n"
        f"📡 IP: {ip}:8080\n"
        f"💻 Слоты: {slots}\n"
        f"🔑 API Key: {api_key}"
    )

ADMIN_SERVER_ADD_ERROR = (
    f"❌ <b>Не удалось подключиться к агенту</b>\n\n"
    f"Убедитесь что:\n"
    f"1. Агент запущен на сервере\n"
    f"2. Порт 8080 открыт в firewall\n"
    f"3. IP адрес верный"
)


# ─── ADMIN: PROMO CREATE ───

ADMIN_PROMO_CREATE_CODE = f"{Emoji.GIFT} Введите код промокода:"
ADMIN_PROMO_CREATE_TYPE = f"{Emoji.GIFT} Введите тип награды (tariff/projects/balance):"
ADMIN_PROMO_CREATE_VALUE = f"{Emoji.GIFT} Введите значение награды:"
ADMIN_PROMO_CREATE_MAX = f"{Emoji.GIFT} Введите макс. количество активаций:"

def admin_promo_create_success(code: str) -> str:
    return f"{Emoji.CHECK} Промокод <b>{code}</b> создан."


# ─── ADMIN: BROADCAST ───

ADMIN_BROADCAST_TEXT = f"{Emoji.SPEAKER} Отправьте сообщение для рассылки:"

def admin_broadcast_done(sent: int, failed: int) -> str:
    return (
        f"{Emoji.CHECK} Рассылка завершена.\n\n"
        f"✅ Отправлено: {sent}\n"
        f"❌ Ошибок: {failed}"
    )


# ─── ADMIN: SETTINGS ───

ADMIN_SETTINGS_TEXT = f"{Emoji.SETTINGS} <b>Настройки</b>"

def admin_sleep_changed(minutes: int) -> str:
    return f"✅ Автосон: {minutes} минут"


# ─── ADMIN: PHOTOS ───

ADMIN_PHOTOS_TEXT = (
    f"{Emoji.MEDIA} <b>Управление фото</b>\n\n"
    f"✅ — фото установлено\n"
    f"⬜ — фото не установлено\n\n"
    f"Нажмите на пункт чтобы установить/заменить фото."
)

def admin_photo_set_text(label: str, status: str) -> str:
    return (
        f"{Emoji.MEDIA} <b>{label}</b>\n\n"
        f"Статус: {status}\n\n"
        f"Отправьте фото для этого экрана.\n"
        f"Или отправьте <code>удалить</code> чтобы убрать фото."
    )

def admin_photo_success(label: str) -> str:
    return f"{Emoji.CHECK} Фото для <b>{label}</b> установлено!"

def admin_photo_deleted(label: str) -> str:
    return f"{Emoji.CHECK} Фото для <b>{label}</b> удалено!"


# ─── ERRORS ───

ERROR_NOT_FOUND = "Бот не найден"
ERROR_NO_ACCESS = "Нет доступа"
ERROR_INVALID_NAME = "❌ Невалидное имя. Используйте буквы, цифры, _ и - (1-50 символов)."
ERROR_INVALID_ZIP = "❌ Отправьте ZIP архив (.zip файл)."
ERROR_INVALID_URL = "❌ Невалидный URL. Используйте формат:\n<code>https://github.com/user/repo</code>"
ERROR_REPO_NOT_FOUND = "❌ Репозиторий не найден или приватный."
ERROR_DOCKER_UNAVAILABLE = "Docker недоступен"
ERROR_CONTAINER_NOT_RUNNING = "Проект не запущен"
ERROR_ADMIN_ONLY = "⛔ Нет доступа"

def error_limit_reached(limit: int) -> str:
    return f"Достигнут лимит ботов ({limit})"

def error_upload_failed(error: str) -> str:
    return f"Ошибка загрузки файла: {error}"


# ─── SUCCESS ───

SUCCESS_BOT_STARTED = f"{Emoji.CHECK} Проект запущен"
SUCCESS_BOT_STOPPED = f"{Emoji.CHECK} Проект остановлен"

def success_bot_renamed(name: str) -> str:
    return f"{Emoji.CHECK} Бот переименован в <b>{name}</b>"

def success_secret_added(key: str) -> str:
    return f"{Emoji.CHECK} Секрет <b>{key}</b> сохранён."

def success_secret_deleted(key: str) -> str:
    return f"{Emoji.CHECK} Секрет <b>{key}</b> удалён."

def success_lib_added(lib: str) -> str:
    return f"{Emoji.CHECK} Библиотека <b>{lib}</b> добавлена.\nПерезапустите бота для применения."

SUCCESS_BACKUP_CREATED = "☁ Бэкап создан!"

def success_entry_changed(entry: str) -> str:
    return f"{Emoji.CHECK} Точка входа: <code>{entry}</code>"

def success_python_changed(version: str) -> str:
    return f"✅ Python изменён на {version}"

def success_balance_changed(amount: float, balance: float) -> str:
    return f"✅ Баланс изменён на {amount:.2f}\nНовый баланс: {balance:.2f}"
