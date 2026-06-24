from __future__ import annotations

from bot.utils.emojis import Emoji


# ─── WELCOME ───

def welcome_text(username: str) -> str:
    from bot.config import settings
    return (
        f"{Emoji.SMILE} <b>Добро пожаловать в {settings.BOT_NAME}</b>\n\n"
        f"Управляйте инфраструктурой своих ботов из одного окна.\n\n"
        f"Разверните собственный исходный код или активируйте "
        f"готовый шаблон конфигурации всего в несколько кликов.\n\n"
        f"Продолжая работу, вы соглашаетесь с нашими <a href=\"#\">условиями использования</a> "
        f"и <a href=\"#\">политикой конфиденциальности</a>."
    )

CONTROL_PANEL_TEXT = (
    f"📋 <b>Панель управления</b>\n\n"
    f"Выберите нужный проект из списка ниже, чтобы перейти к его настройкам и мониторингу."
)


# ─── ADD BOT: SOURCE ───

ADD_BOT_SOURCE_TEXT = (
    f"📥 <b>Шаг 1 из 4: Источник деплоя</b>\n\n"
    f"Выберите способ загрузки проекта: вы можете развернуть собственный код "
    f"или использовать готовые пресеты от нашего комьюнити."
)

ADD_BOT_ZIP_TEXT = (
    f"📥 <b>Шаг 3 из 4: Загрузка исходного кода</b>\n\n"
    f"Отправьте проект в формате .zip архива. "
    f"Если в корне находится файл <code>requirements.txt</code>, мы автоматически "
    f"установим все зависимости. Вы также сможете сделать это позже в панели управления."
)

ADD_BOT_GITHUB_TEXT = (
    f"🔗 <b>Шаг 3 из 4: Синхронизация с GitHub</b>\n\n"
    f"Для первой публикации нажмите кнопку «Подключить GitHub».\n"
    f"Вы можете предоставить доступ ко всем репозиториям или выбрать только определенные.\n\n"
    f"Выберите проект для деплоя:"
)


# ─── ADD BOT: PYTHON VERSION ───

ADD_BOT_PYTHON_TEXT = (
    f"🐍 <b>Шаг 2 из 4: Окружение Runtime</b>\n"
    f"<i>Рекомендуется 3.10 для устаревших проектов (например, aiogram 2.x)</i>\n\n"
    f"Укажите версию интерпретатора Python для изоляции вашего кода:"
)


# ─── ADD BOT: ENTRY POINT ───

ADD_BOT_ENTRY_TEXT = (
    f"📄 <b>Шаг 4 из 4: Конфигурация запуска</b>\n\n"
    f"Выберите режим инициализации процесса:\n"
    f"• <b>Скрипт</b> — прямой запуск через <code>python file.py</code>\n"
    f"• <b>Модуль</b> — запуск пакета через <code>python -m package.module</code>"
)

def add_bot_entry_script_text(filter: str = "*.py") -> str:
    return (
        f"📄 <b>Шаг 4 из 4: Выбор исполняемого файла</b>\n"
        f"<i>Контекст: Скрипт / python <code>file.py</code></i>\n"
        f"<i>Фильтр директории: {filter}</i>\n\n"
        f"Укажите главный файл, который должен выполняться при старте контейнера:"
    )

ADD_BOT_ENTRY_MODULE_TEXT = (
    "📄 <b>Конфигурация запуска</b>\n\n"
    "Контекст: Модуль / python -m\n\n"
    "Введите путь к модулю вручную.\n"
    "Пример корректного ввода: <code>app.pkg.main</code>"
)

ADD_BOT_ENTRY_MANUAL_TEXT = (
    "📄 <b>Конфигурация запуска</b>\n\n"
    "Введите имя файла инициализации вручную.\n"
    "Пример корректного ввода: <code>main.py</code>"
)

def add_bot_entry_confirm_text(entry: str) -> str:
    return (
        f"📄 <b>Шаг 4 из 4: Проверка конфигурации</b>\n\n"
        f"Точка входа: <code>{entry}</code>\n\n"
        f"Подтвердите значение. Вы сможете переопределить его в любой момент."
    )


# ─── ADD BOT: SERVER SELECTION ───

ADD_BOT_SERVER_TEXT = (
    f"🖥 <b>Выбор локации</b>\n\n"
    f"Укажите целевой сервер для развертывания инфраструктуры:"
)

ADD_BOT_SERVER_POOL_TEXT = "[ Свободный пул слотов ]"


# ─── ADD BOT: CONFIRM ───

def add_bot_confirm_text(name: str, python_version: str, entry_point: str) -> str:
    return (
        f"{Emoji.CHECK} <b>Проверка параметров конфигурации</b>\n\n"
        f"📝 Имя инстанса: <b>{name}</b>\n"
        f"🐍 Окружение: Python {python_version}\n"
        f"📄 Инициализация: <code>{entry_point}</code>\n\n"
        f"Инициализировать создание проекта?"
    )

ADD_BOT_NAME_TEXT = "📝 Укажите имя проекта (от 1 до 50 символов: буквы, цифры, знаки _ и -):"


# ─── ADD BOT: SUCCESS ───

ADD_BOT_SUCCESS_TEXT = (
    f"🤖 <b>Окружение успешно развернуто!</b>\n\n"
    f"Ваш проект успешно инициализирован и запущен на сервере.\n\n"
    f"Перейдите в панель управления, чтобы получить доступ к менеджеру файлов, "
    f"инструментам сборки зависимостей, логам в реальном времени и управлению питанием."
)


# ─── BOT CONTROL ───

def bot_control_text(name: str, server_text: str, status_text: str, uptime: str, cpu: float, ram: float) -> str:
    return (
        f"📋 <b>Управление проектом</b>\n\n"
        f"ID: <b>{name}</b>\n"
        f"Нода: {server_text}\n\n"
        f"Статус: {status_text} · Аптайм: {uptime}\n"
        f"Нагрузка: CPU {cpu:.2f}% · RAM {ram:.2f}%"
    )


# ─── BOT SETTINGS ───

BOT_SETTINGS_TEXT = (
    f"⚙ <b>Параметры и конфигурация</b>\n\n"
    f"Выберите системный раздел для изменения настроек инстанса:"
)

BOT_RENAME_TEXT = "✏ <b>Переименование инстанса</b>\n\nВведите новое идентификационное имя проекта:"

BOT_DELETE_TEXT = (
    f"🗑 <b>Уничтожение инстанса</b>\n\n"
    f"Подтвердите безвозвратное удаление проекта. Все связанные файлы "
    f"и конфигурации будут стерты без возможности восстановления."
)

def bot_deleted_text(name: str) -> str:
    return (
        f"🗑 <b>Проект удален</b>\n\n"
        f"Инстанс <b>{name}</b> и все его ресурсы успешно стерты из системы."
    )


# ─── BOT PYTHON VERSION ───

BOT_PYTHON_TEXT = (
    f"🐍 <b>Изменение Runtime-окружения</b>\n\n"
    f"Обратите внимание: после смены версии Python проект будет автоматически перезапущен."
)


# ─── BOT ENTRY POINT ───

def bot_entry_text(entry_type: str, entry_point: str) -> str:
    return (
        f"📄 <b>Конфигурация точки входа</b>\n\n"
        f"Выберите формат исполнения кода:\n"
        f"• <b>Скрипт</b> — для прямой команды <code>python file.py</code>\n"
        f"• <b>Модуль</b> — для инициализации пакета <code>python -m package.module</code>\n\n"
        f"Текущий режим: <b>{entry_type}</b>\n"
        f"Текущее значение: <code>{entry_point}</code>"
    )

BOT_ENTRY_MODULE_TEXT = (
    "📄 <b>Изменение конфигурации</b>\n\n"
    "Режим: Модульный запуск / python -m\n\n"
    "Отправьте имя целевого модуля текстом.\n"
    "Пример: <code>app.pkg.main</code>"
)

BOT_ENTRY_SELECT_FILE_TEXT = "Пожалуйста, выберите исполняемый файл через файловый менеджер ниже"


# ─── BOT COOWNERS ───

def bot_coowners_text(name: str) -> str:
    return (
        f"👥 <b>Доступы к проекту: {name}</b>\n\n"
        f"Иерархия привилегий:\n"
        f"  <b>Owner</b> — полный административный доступ и управление лимитами.\n"
        f"  <b>Developer</b> — управление процессами, чтение логов и конфигурация файлов."
    )

BOT_COOWNER_ADD_TEXT = "👤 Введите Telegram ID пользователя, которому хотите делегировать доступ:"
BOT_COOWNER_ADD_ROLE_TEXT = "👤 Укажите уровень прав (роль) для нового участника команды:"

def bot_coowner_added_text(user_id: int, role: str) -> str:
    return f"{Emoji.CHECK} Пользователю {user_id} предоставлен доступ с ролью {role}"

def bot_coowner_deleted_text(user_id: int) -> str:
    return f"{Emoji.CHECK} Права доступа для пользователя {user_id} успешно аннулированы"

BOT_COOWNER_NOT_FOUND_TEXT = "Указанный пользователь не зарегистрирован в системе"
BOT_COOWNER_ALREADY_EXISTS_TEXT = "Этот пользователь уже имеет доступ к данному проекту"


# ─── BOT LOGS ───

def bot_logs_text(name: str, logs: str) -> str:
    return (
        f"📋 TTY-Вывод <b>{name}</b> (последние 3500 символов):\n\n"
        f"<code>{logs}</code>"
    )


# ─── BOT FILES ───

BOT_FILES_TEXT = (
    f"📁 <b>Файловая система</b>\n\n"
    f"Управляйте структурой директорий: выбирайте файлы для загрузки или удаления.\n"
    f"Чтобы импортировать новый файл в текущую папку, просто отправьте его в диалог."
)

def bot_files_path_text(path: str) -> str:
    return f"📁 <b>Директория: {path}</b>"

BOT_FILE_DELETE_CONFIRM_TEXT = lambda file_path: f"🗑 Подтверждаете удаление объекта <b>{file_path}</b>?"
BOT_FILE_DELETED_TEXT = "Файл успешно удален"
BOT_FILE_DELETE_ERROR_TEXT = "Не удалось удалить файл. Проверьте права доступа."
BOT_FILE_NOT_FOUND_TEXT = "Указанный объект отсутствует или не содержит данных"


# ─── BOT LIBRARIES ───

BOT_LIBS_TEXT = (
    f"📦 <b>Пакетный менеджер (Pip)</b>\n\n"
    f"Список установленных зависимостей окружения. Вы можете добавить новые "
    f"библиотеки или удалить неиспользуемые компоненты."
)

BOT_LIB_ADD_TEXT = (
    "📦 <b>Установка пакетов</b>\n\n"
    "Введите точное наименование библиотеки из PyPI.\n"
    "Примеры: <code>aiogram</code>, <code>requests>=2.0</code>"
)


# ─── SUBSCRIPTION ───

def subscription_text(is_premium: bool) -> str:
    from models.subscription import get_free_features, get_premium_features
    if is_premium:
        features = get_premium_features()
        features_text = "\n".join(f"· {f}" for f in features)
        return (
            f"💳 <b>Статус подписки</b>\n\n"
            f"Текущий план: {Emoji.CHECK} Premium\n\n"
            f"<b>Доступные премиум-ресурсы:</b>\n{features_text}"
        )
    features = get_free_features()
    features_text = "\n".join(f"· {f}" for f in features)
    return (
        f"💳 <b>Статус подписки</b>\n\n"
        f"Текущий план: {Emoji.CHECK} Базовый (Free)\n\n"
        f"<b>Лимиты тарифа:</b>\n{features_text}"
    )

SUBSCRIPTION_INFO_TEXT = None


def subscription_info_text() -> str:
    from models.subscription import get_premium_features
    features = get_premium_features()
    features_text = "\n".join(f"· {f}" for f in features)
    return (
        f"💳 <b>Возможности расширенной подписки</b>\n\n"
        f"<b>{Emoji.NOTIF} Привилегии Premium-плана:</b>\n{features_text}"
    )

SUBSCRIPTION_BUY_TEXT = (
    f"💳 <b>Оформление подписки</b>\n\n"
    f"Выберите расчетный период для активации Premium-доступа:"
)

def subscription_buy_plan_text(plan_label: str, price: int) -> str:
    return (
        f"💳 <b>Оплата подписки</b>\n\n"
        f"Выбранный тариф: <b>Premium {plan_label}</b>\n"
        f"Сумма к оплате: <b>{price}₽</b>\n\n"
        f"Для завершения транзакции и выставления счета свяжитесь с администрацией."
    )


# ─── BACKUPS ───

BACKUPS_LIST_EMPTY_TEXT = (
    f"☁ <b>Резервные копии</b>\n\n"
    f"В данный момент у вас нет активных проектов для создания бэкапов."
)

BACKUPS_LIST_TEXT = (
    f"☁ <b>Архив резервных копий</b>\n\n"
    f"🟢 — Снимок успешно сохранен\n"
    f"🟡 — Процесс архивации в очереди\n"
    f"🔴 — Критическая ошибка создания снимка\n\n"
    f"Выберите существующую точку восстановления или создайте актуальный бэкап:"
)

def backups_bot_text(name: str, count: int) -> str:
    return (
        f"☁ <b>Резервные копии инстанса: {name}</b>\n\n"
        f"Всего доступно архивов: {count}"
    )


# ─── ADMIN PANEL ───

def admin_panel_text(users: int, projects: int, servers: int) -> str:
    return (
        f"{Emoji.SETTINGS} <b>Консоль администратора</b>\n\n"
        f"{Emoji.PROFILE} Зарегистрировано пользователей: {users}\n"
        f"{Emoji.FILE} Активных проектов в системе: {projects}\n"
        f"{Emoji.HOME} Подключено нод (серверов): {servers}"
    )

def admin_users_text(count: int) -> str:
    return f"{Emoji.PEOPLE} <b>Менеджмент пользователей</b> ({count})"

def admin_user_view_text(
    telegram_id: int, username: str, full_name: str,
    tariff: str, balance: float, is_banned: bool,
    projects_count: int, registered_at: str
) -> str:
    status = "🚫 Заблокирован" if is_banned else "✅ Активен"
    return (
        f"{Emoji.PROFILE} <b>Карточка аккаунта</b>\n\n"
        f"Telegram ID: <code>{telegram_id}</code>\n"
        f"Username: @{username or '—'}\n"
        f"Имя профиля: {full_name or '—'}\n"
        f"Тарифный план: <b>{tariff}</b>\n"
        f"Баланс счета: <b>{balance:.2f}</b>\n"
        f"Системный статус: {status}\n"
        f"Запущено проектов: {projects_count}\n"
        f"Дата регистрации: {registered_at}"
    )

def admin_servers_text(count: int) -> str:
    return f"{Emoji.HOME} <b>Инфраструктура нод</b> ({count})"

def admin_server_view_text(
    name: str, country: str, ip: str, port: int,
    api_key: bool, free_slots: int, total_slots: int,
    rating: float, ping: int, load_cpu: float, load_ram: float,
    status: str
) -> str:
    status_icon = "🟢 На линии" if status == "online" else "🔴 Нет связи"
    api_key_text = "Валиден" if api_key else "Отсутствует"
    return (
        f"{Emoji.HOME} <b>Узел: {name}</b>\n\n"
        f"🌍 Геолокация: {country}\n"
        f"📡 Адрес хоста: {ip}:{port}\n"
        f"🔑 Токен агента: {api_key_text}\n"
        f"💻 Распределение слотов: {free_slots}/{total_slots}\n"
        f"⭐ Индекс приоритета: {rating:.1f}\n"
        f"📡 Задержка сети: {ping}ms\n"
        f"📊 Нагрузка ядра CPU: {load_cpu:.1f}%\n"
        f"🧠 Выделение RAM: {load_ram:.1f}%\n"
        f"Статус ноды: {status_icon}"
    )

def admin_stats_text(users: int, projects: int, active: int, servers: int, online: int) -> str:
    return (
        f"{Emoji.GRAPH_STATS} <b>Аналитика и метрики платформы</b>\n\n"
        f"👤 Всего пользователей: {users}\n"
        f"📦 Создано инстансов: {projects}\n"
        f"🟢 Работает в рантайме: {active}\n"
        f"🌍 Подключено серверов: {servers}\n"
        f"🟢 Узлов в статусе Online: {online}"
    )

def admin_promos_text(count: int) -> str:
    return f"{Emoji.GIFT} <b>Активные промокоды</b> ({count})"

def admin_subscriptions_text(free_count: int, premium_count: int, total: int) -> str:
    return (
        f"💎 <b>Статистика тарифных планов</b>\n\n"
        f"🆓 Базовый тариф (Free): {free_count}\n"
        f"💎 Премиум-доступ (Premium): {premium_count}\n"
        f"Всего учетных записей: {total}"
    )

def admin_referrals_text(count: int) -> str:
    return (
        f"🔗 <b>Реферальная сеть</b>\n\n"
        f"Всего приглашенных участников: {count}"
    )


# ─── ADMIN: SERVER ADD ───

ADMIN_SERVER_ADD_NAME = f"{Emoji.HOME} Введите уникальное имя для новой ноды:"
ADMIN_SERVER_ADD_COUNTRY = f"{Emoji.HOME} Укажите страну (локацию) сервера:"
ADMIN_SERVER_ADD_IP = f"{Emoji.HOME} Укажите IP-адрес хоста:"
ADMIN_SERVER_ADD_API_KEY = f"{Emoji.HOME} Введите секретный ключ агента (или «-» для деплоя без авторизации):"
ADMIN_SERVER_ADD_SLOTS = f"{Emoji.HOME} Задайте максимальный лимит слотов:"

ADMIN_SERVER_ADD_CHECKING = f"{Emoji.LOADING} <b>Выполняется сопряжение с удаленным агентом...</b>"

def admin_server_add_success(name: str, country: str, ip: str, slots: int, api_key: str) -> str:
    return (
        f"✅ <b>Нода {name} успешно интегрирована в кластер!</b>\n\n"
        f"🌍 Локация: {country}\n"
        f"📡 Сетевой адрес: {ip}:8080\n"
        f"💻 Выделено слотов: {slots}\n"
        f"🔑 Токен доступа: {api_key}"
    )

ADMIN_SERVER_ADD_ERROR = (
    f"❌ <b>Ошибка сетевого сопряжения с удаленным хостом</b>\n\n"
    f"Рекомендации по устранению:\n"
    f"1. Проверьте статус демона агента на целевом сервере\n"
    f"2. Убедитесь, что порт 8080 открыт во внешнем Firewall\n"
    f"3. Корректно ли указан сетевой IPv4/IPv6 адрес"
)


# ─── ADMIN: PROMO CREATE ───

ADMIN_PROMO_CREATE_CODE = f"{Emoji.GIFT} Введите буквенно-цифровой код купона:"
ADMIN_PROMO_CREATE_TYPE = f"{Emoji.GIFT} Задайте тип бонуса (tariff / projects / balance):"
ADMIN_PROMO_CREATE_VALUE = f"{Emoji.GIFT} Укажите номинал вознаграждения:"
ADMIN_PROMO_CREATE_MAX = f"{Emoji.GIFT} Установите лимит общего числа активаций:"

def admin_promo_create_success(code: str) -> str:
    return f"{Emoji.CHECK} Промокод <b>{code}</b> успешно сгенерирован и внесен в реестр."


# ─── ADMIN: BROADCAST ───

ADMIN_BROADCAST_TEXT = f"{Emoji.SPEAKER} Введите текст или медиафайл для глобальной рассылки:"

def admin_broadcast_done(sent: int, failed: int) -> str:
    return (
        f"{Emoji.CHECK} Информационная кампания завершена.\n\n"
        f"✅ Доставлено адресатам: {sent}\n"
        f"❌ Исключения/ошибки сети: {failed}"
    )


# ─── ADMIN: SETTINGS ───

ADMIN_SETTINGS_TEXT = f"{Emoji.SETTINGS} <b>Глобальная конфигурация платформы</b>"

def admin_sleep_changed(minutes: int) -> str:
    return f"✅ Интервал автоматического сна изменен: {minutes} мин."


# ─── ADMIN: PHOTOS ───

ADMIN_PHOTOS_TEXT = (
    f"{Emoji.MEDIA} <b>Менеджер графических ресурсов интерфейса</b>\n\n"
    f"✅ — Медиаресурс активен\n"
    f"⬜ — Используется стандартная верстка\n\n"
    f"Выберите интерфейсный экран для загрузки или обновления баннера."
)

def admin_photo_set_text(label: str, status: str) -> str:
    return (
        f"{Emoji.MEDIA} <b>Экран: {label}</b>\n\n"
        f"Статус отрисовки: {status}\n\n"
        f"Прикрепите и отправьте новое изображение для данного интерфейса.\n"
        f"Отправьте команду <code>удалить</code>, чтобы сбросить баннер до дефолтных настроек."
    )

def admin_photo_success(label: str) -> str:
    return f"{Emoji.CHECK} Графический ресурс для экрана <b>{label}</b> успешно применен!"

def admin_photo_deleted(label: str) -> str:
    return f"{Emoji.CHECK} Медиаресурс для экрана <b>{label}</b> успешно деинсталлирован."


# ─── ERRORS ───

ERROR_NOT_FOUND = "Указанный проект не зарегистрирован в системе."
ERROR_NO_ACCESS = "Недостаточно прав для выполнения данной операции."
ERROR_INVALID_NAME = "❌ Ошибка синтаксиса имени. Разрешены только символы латиницы, цифры, дефис и нижнее подчеркивание (1-50 знаков)."
ERROR_INVALID_ZIP = "❌ Неверный формат данных. Требуется архив расширения .zip."
ERROR_INVALID_URL = "❌ Некорректный синтаксис адреса. Используйте спецификацию:\n<code>https://github.com/user/repo</code>"
ERROR_REPO_NOT_FOUND = "❌ Репозиторий скрыт настройками приватности или не существует."
ERROR_DOCKER_UNAVAILABLE = "Системная подсистема контейнеризации недоступна"
ERROR_CONTAINER_NOT_RUNNING = "Процесс инстанса остановлен"
ERROR_ADMIN_ONLY = "⛔ Доступ ограничен. Требуются привилегии суперадминистратора."

def error_limit_reached(limit: int) -> str:
    return f"Превышен доступный лимит активных инстансов на вашей учетной записи (макс. {limit})"

def error_upload_failed(error: str) -> str:
    return f"Сбой подсистемы ввода-вывода при загрузке: {error}"


# ─── BUTTONS ───

BTN_BACK = "Вернуться"
BTN_CANCEL = "Отмена"
BTN_CONFIRM = "✅ Подтвердить конфигурацию"
BTN_DELETE = "🗑 Удалить"
BTN_YES_DELETE = "✅ Да, подтверждаю удаление"
BTN_NO = "❌ Отклонить"
BTN_CLOSE = "✕ Закрыть"
BTN_ADD = "➕ Добавить"

BTN_START = "▶ Запустить процесс"
BTN_STOP = "⏹ Остановить процесс"
BTN_RESTART = "🔄 Перезапустить"
BTN_LOGS = "📋 Просмотр TTY-логов"
BTN_LOGS_FILE = "📄 Экспорт .log файлом"
BTN_LOGS_REFRESH = "🔄 Обновить терминал"
BTN_SETTINGS = "⚙ Конфигурация инстанса"

BTN_LIBRARIES = "📦 Управление Pip-пакетами"
BTN_LIBRARY_ADD = "➕ Установить зависимость"
BTN_FILES = "📁 Файловый менеджер"
BTN_PYTHON_VERSION = "🐍 Версия Runtime-интерпретатора"
BTN_ENTRY_POINT = "📄 Изменить точку входа"
BTN_COOWNERS = "👥 Делегирование доступов"
BTN_GRAPHS = "📊 Телеметрия и метрики"
BTN_NOTIFICATIONS = "🔔 Настройки алертов"
BTN_RENAME = "✏ Изменить название"
BTN_DELETE_BOT = "🗑 Уничтожить проект"

BTN_ADD_BOT = "➕ Создать новый инстанс"
BTN_UPLOAD_FILES = "📥 Импортировать .ZIP"
BTN_CONNECT_GITHUB = "🔗 Интеграция с GitHub"
BTN_SCRIPT_MODE = "📄 Скриптовый запуск"
BTN_MODULE_MODE = "📦 Модульный пакет"

BTN_FILE_DOWNLOAD = "⬇️ Скачать"
BTN_FILE_DELETE = "🗑 Удалить"
BTN_FILE_UP = "⬆ На уровень выше"

BTN_COOWNER_ADD = "➕ Добавить разработчика"
BTN_COOWNER_DELETE = "🗑 Отзыв прав"

BTN_SUBSCRIPTION_INFO = "❓ Спецификация Premium-тарифа"
BTN_SUBSCRIPTION_BUY = "💳 Оформить Premium-доступ"

BTN_ADMIN_USERS = "👤 Менеджмент аккаунтов"
BTN_ADMIN_SERVERS = "🖥 Управление кластером"
BTN_ADMIN_STATS = "📊 Сводная статистика"
BTN_ADMIN_PROMOS = "🎁 Система промокодов"
BTN_ADMIN_BROADCAST = "📢 Глобальный пуш-ап"
BTN_ADMIN_SETTINGS = "⚙ Системные триггеры"
BTN_ADMIN_PHOTOS = "🖼 Настройка графики"

BTN_CREATE_BACKUP = "➕ Сгенерировать снимок"
BTN_RESTORE_BACKUP = "🔄 Откатить систему"
BTN_DELETE_BACKUP = "🗑 Стереть снимок"


# ─── PROJECT MONITOR ───

def project_monitor_text(name: str, status_text: str, cpu: float, ram: float, disk: float, uptime: str, restarts: int) -> str:
    return (
        f"{Emoji.GRAPH_STATS} <b>Инфраструктурный мониторинг: {name}</b>\n\n"
        f"Текущее состояние: {status_text}\n"
        f"Выделение CPU: <b>{cpu:.1f}%</b>\n"
        f"Аллокация RAM: <b>{ram:.1f} MB</b>\n"
        f"Потребление диска: <b>{disk:.1f} MB</b>\n"
        f"Время непрерывной работы: <b>{uptime}</b>\n"
        f"Системных перезапусков: <b>{restarts}</b>"
    )

def project_graphs_text(hours: int, avg_cpu: float, max_cpu: float, avg_ram: float, max_ram: float, data_points: int) -> str:
    return (
        f"{Emoji.GRAPH_UP} <b>Историческая телеметрия за {hours}ч</b>\n\n"
        f"{Emoji.GRAPH_STATS} Вычислительная мощность (CPU):\n"
        f"  Средний показатель: {avg_cpu:.1f}%\n"
        f"  Пиковая нагрузка: {max_cpu:.1f}%\n\n"
        f"{Emoji.GRAPH_UP} Оперативная память (RAM):\n"
        f"  Среднее выделение: {avg_ram:.1f} MB\n"
        f"  Пиковое выделение: {max_ram:.1f} MB\n\n"
        f"{Emoji.INFO} Агрегировано точек данных: {data_points}"
    )

ERROR_NO_STATS_DATA = "В выбранном временном диапазоне метрики отсутствуют"


# ─── PROJECT SETTINGS ───

def project_settings_text(name: str, python_version: str, entry_point: str, entry_type: str) -> str:
    return (
        f"{Emoji.SETTINGS} <b>Спецификация инстанса: {name}</b>\n\n"
        f"Интерпретатор: Python {python_version}\n"
        f"Скрипт запуска: <code>{entry_point}</code>\n"
        f"Тип архитектуры: {entry_type}"
    )

PROJECT_PYTHON_SELECT_TEXT = f"{Emoji.SETTINGS} Укажите целевую версию среды выполнения Python:"
PROJECT_ENTRY_INPUT_TEXT = f"{Emoji.PENCIL} Задайте новый вектор инициализации (например: main.py или package.module):"
PROJECT_SETTINGS_USE_CARD = "Применить дефолтные параметры из карточки метаданных проекта"


# ─── PROJECT LOGS ───

def project_logs_menu_text(name: str) -> str:
    return f"{Emoji.FILE} <b>Консоль вывода: {name}</b>"

def project_logs_view_text(logs: str) -> str:
    return f"<b>📋 Поток вывода stderr/stdout:</b>\n\n<code>{logs}</code>"

def project_logs_file_caption(name: str) -> str:
    return f"Лог-файл системных событий инстанса {name}"

PROJECT_LOGS_CLEARED = "Буфер вывода успешно очищен."
PROJECT_LOGS_CLEAR_ERROR = "Не удалось очистить буфер событий."


# ─── PROJECT MANAGE ───

def project_delete_confirm_text(name: str) -> str:
    return (
        f"{Emoji.TRASH} <b>Инициализация удаления инстанса</b>\n\n"
        f"Вы абсолютно уверены, что хотите стереть проект <b>{name}</b>?\n"
        f"Данная операция сотрет проект с физического диска без возможности отката."
    )

PROJECT_DELETED_TEXT = f"{Emoji.CHECK} Локальные ресурсы проекта полностью уничтожены."
PROJECT_DELETE_ERROR = "Сбой файловой системы при удалении контейнера."


# ─── PROFILE & SETTINGS ───

SETTINGS_NOT_FOUND = "Конфигурационные данные профиля не обнаружены."
SETTINGS_UNKNOWN = "Запрошен неподдерживаемый системный параметр."
SETTINGS_CHANGED = "Конфигурация успешно обновлена."

def notification_settings_text() -> str:
    return f"{Emoji.NOTIF} <b>Управление системными алертами и событиями</b>"


# ─── LOCATIONS ───

LOCATIONS_NO_SERVERS = f"{Emoji.HOME} <b>Узлы кластера</b>\n\nДоступные физические серверы отсутствуют."
LOCATIONS_SERVERS_TEXT = f"{Emoji.HOME} <b>Доступные вычислительные узлы</b>"
LOCATION_NOT_FOUND = "Целевой сервер обслуживания не обнаружен в сети."


# ─── SUBSCRIPTION ───

SUBSCRIPTION_PLAN_UNKNOWN = "Запрошен несуществующий тарифный план."

def subscription_buy_confirm_text(plan_label: str, price: int) -> str:
    return (
        f"💳 <b>Оформление подписки</b>\n\n"
        f"Выбранный пакет: <b>Premium {plan_label}</b>\n"
        f"Стоимость тарифа: <b>{price}₽</b>\n\n"
        f"Для завершения процедуры транзакции перейдите в чат поддержки клиентов."
    )


# ─── COOWNERS ───

COOWNER_ENTER_ID = f"{Emoji.PROFILE} Перешлите или введите числовой Telegram ID пользователя для предоставления прав:"
COOWNER_REMOVED = "Права совместного управления успешно отозваны."
COOWNER_INVALID_ID = "❌ Ошибка формата данных. ID аккаунта должен быть исключительно числовым значением."
COOWNER_SELF_ADD = "❌ Недопустимая операция. Вы не можете выдать доступ самому себе."
COOWNER_USER_NOT_FOUND = "❌ Пользователь не прошел первичную регистрацию. Ему необходимо хотя бы раз инициализировать сессию с ботом."
COOWNER_ALREADY_EXISTS = "❌ Данный разработчик уже имеет права доступа к этой инфраструктуре."

def coowner_added_text(username: str) -> str:
    return f"{Emoji.CHECK} Пользователь <b>{username}</b> успешно интегрирован в состав разработчиков проекта."


# ─── BOT CREATE ───

BOT_CREATE_INVALID_ZIP = "❌ Ошибка пакета. Отправьте валидный несжатый .zip архив."
BOT_CREATE_INVALID_URL = "❌ Ошибка синтаксиса ссылки. Используйте формат регулярного выражения:\n<code>https://github.com/user/repo</code>"
BOT_CREATE_REPO_NOT_FOUND = "❌ Репозиторий GitHub скрыт настройками приватности либо удален."
BOT_CREATE_ARCHIVE_NOT_FOUND = "Бинарный архив исходного кода не обнаружен в кэше"
BOT_CREATE_NO_SERVERS = "Свободные вычислительные мощности в кластере на данный момент отсутствуют"
BOT_CREATE_INVALID_NAME = "❌ Ошибка валидации имени: допустимы только латинские символы, цифры, знаки _ и - (до 50 символов)."
BOT_CREATE_LIMIT_REACHED = lambda limit: f"Достигнута максимальная квота активных инстансов для вашего уровня аккаунта ({limit})"
BOT_CREATE_DOWNLOAD_ERROR = lambda e: f"Сбой сетевого стрима при скачивании пакета: {e}"

BOT_CREATE_NAME_TEXT = "📝 <b>Идентификатор проекта</b>\n\nУкажите имя инстанса (от 1 до 50 символов: латиница, цифры, дефис, нижнее подчеркивание):"
BOT_CREATE_ENTRY_MANUAL_TEXT = (
    "📄 <b>Конфигурация точки запуска</b>\n\n"
    "Введите имя корневого исполняемого файла вручную.\n"
    "Пример: <code>main.py</code>"
)
BOT_CREATE_ENTRY_MODULE_TEXT = (
    "📄 <b>Конфигурация точки запуска</b>\n\n"
    "Режим выполнения: Пакетный модуль / python -m\n\n"
    "Укажите наименование исполняемого модуля.\n"
    "Пример: <code>app.pkg.main</code>"
)
def bot_create_entry_confirm_text(entry: str) -> str:
    return (
        f"📄 <b>Конфигурация: {entry}</b>\n\n"
        f"Подтвердите выбор точки входа. Значение можно будет динамически скорректировать позже."
    )

def bot_create_confirm_text(name: str, python: str, entry: str) -> str:
    return (
        f"{Emoji.CHECK} <b>Валидация параметров деплоя</b>\n\n"
        f"📝 Проект: <b>{name}</b>\n"
        f"🐍 Среда: Python {python}\n"
        f"📄 Выполнение: <code>{entry}</code>\n\n"
        f"Инициализировать развертывание и сборку?"
    )

BOT_CREATE_SUCCESS_TEXT = (
    f"🤖 <b>Процесс виртуализации успешно завершен!</b>\n\n"
    f"Контейнер инстанса переведен в активную фазу выполнения.\n\n"
    f"Используйте основное меню для контроля параметров рантайма."
)


# ─── ADMIN ───

ADMIN_NO_ACCESS = "⛔ Ошибка аутентификации. Требуются права суперпользователя (Root)."
ADMIN_USER_NOT_FOUND = "Указанная учетная запись не найдена в базе данных."
ADMIN_SERVER_NOT_FOUND = "Физический узел кластера не зарегистрирован."
ADMIN_SERVER_DELETED = "Вычислительный узел успешно удален из инфраструктуры."
ADMIN_REFERRAL_WIP = "Функциональный модуль реферального процессинга находится на стадии инженерной сборки"

ADMIN_USER_BANNED = "🚫 Учетная запись переведена в статус перманентной блокировки"
ADMIN_USER_UNBANNED = "✅ Системные ограничения для учетной записи полностью сняты"
ADMIN_TARIFF_CHANGED = lambda tariff: f"✅ Тарифный план пользователя переопределен на {tariff}"
ADMIN_BALANCE_INPUT_ERROR = "❌ Ошибка валидации типа. Введите корректное числовое значение:"
ADMIN_PROMO_TYPE_ERROR = "❌ Недопустимый тип сущности. Разрешенные параметры: tariff, projects, balance"

def admin_user_status_text(username: str, status: str) -> str:
    return f"{Emoji.PROFILE} <b>@{username}</b> — Системный статус аккаунта: {status}"

def admin_user_tariff_text(username: str, tariff: str) -> str:
    return f"{Emoji.PROFILE} <b>@{username}</b> — Активный тариф: {tariff}"

def admin_balance_result_text(amount: float, balance: float) -> str:
    return (
        f"{Emoji.CHECK} Баланс скорректирован на величину: {amount:.2f}\n"
        f"Актуальное состояние счета: {balance:.2f}"
    )

def admin_server_delete_confirm_text(name: str) -> str:
    return f"{Emoji.TRASH} Инициировать деинсталляцию физического сервера <b>{name}</b> из сети?"

ADMIN_SERVER_ENTER_NAME = f"{Emoji.HOME} Введите уникальное кодовое имя ноды:"
ADMIN_SERVER_ENTER_COUNTRY = f"{Emoji.HOME} Укажите географическую локацию хоста:"
ADMIN_SERVER_ENTER_IP = f"{Emoji.HOME} Задайте IPv4/IPv6 адрес сервера:"
ADMIN_SERVER_ENTER_API_KEY = f"{Emoji.HOME} Укажите токен авторизации агента (или «-» для пропуска защиты):"
ADMIN_SERVER_ENTER_SLOTS = f"{Emoji.HOME} Задайте максимальный лимит доступных слотов виртуализации:"
ADMIN_SERVER_CHECKING = f"{Emoji.LOADING} <b>Ожидание ответа от сетевого интерфейса агента...</b>"

ADMIN_PROMO_ENTER_CODE = f"{Emoji.GIFT} Задайте кодовую комбинацию промокода:"
ADMIN_PROMO_ENTER_TYPE = f"{Emoji.GIFT} Выберите тип процессинга купона (tariff/projects/balance):"
ADMIN_PROMO_ENTER_VALUE = f"{Emoji.GIFT} Задайте математический номинал вознаграждения:"
ADMIN_PROMO_ENTER_MAX = f"{Emoji.GIFT} Определите лимит пула активаций промокода:"

ADMIN_BROADCAST_ENTER_MESSAGE = f"{Emoji.SPEAKER} Сформируйте текстовое уведомление для пакетной рассылки:"

def admin_broadcast_done_text(sent: int, failed: int) -> str:
    return (
        f"{Emoji.CHECK} Пакетная отправка пуш-уведомлений завершена.\n\n"
        f"✅ Успешных доставок: {sent}\n"
        f"❌ Ошибок сетевой маршрутизации: {failed}"
    )

ADMIN_SLEEP_CHANGED = lambda minutes: f"✅ Тайм-аут перехода инстансов в режим сна изменен: {minutes} минут"
ADMIN_TARIFF_SELECT_TEXT = f"{Emoji.SETTINGS} Выберите целевой тарифный план для данного аккаунта:"
ADMIN_BALANCE_INPUT_TEXT = f"{Emoji.COIN} Задайте дельту изменения баланса (положительное число — пополнение, отрицательное — списание):"


# ─── SUCCESS ───

SUCCESS_BOT_STARTED = f"{Emoji.CHECK} Контейнер инстанса успешно запущен в рантайме"
SUCCESS_BOT_STOPPED = f"{Emoji.CHECK} Сигналы процесса успешно остановлены (SIGTERM)"

def success_bot_renamed(name: str) -> str:
    return f"{Emoji.CHECK} Идентификатор инстанса успешно изменен на <b>{name}</b>"

def success_secret_added(key: str) -> str:
    return f"{Emoji.CHECK} Переменная окружения (ENV) <b>{key}</b> добавлена в стек конфигов."

def success_secret_deleted(key: str) -> str:
    return f"{Emoji.CHECK} Переменная окружения (ENV) <b>{key}</b> успешно стерта из контейнера."

def success_lib_added(lib: str) -> str:
    return f"{Emoji.CHECK} Пакет <b>{lib}</b> успешно скомпилирован.\nПерезапустите инстанс для применения новых зависимостей."

SUCCESS_BACKUP_CREATED = "☁ Снимок файловой системы и метаданных успешно сохранен в облачном архиве!"

def success_entry_changed(entry: str) -> str:
    return f"{Emoji.CHECK} Вектор инициализации процесса изменен на: <code>{entry}</code>"

def success_python_changed(version: str) -> str:
    return f"✅ Интерпретатор рантайма успешно переключен на Python {version}"

def success_balance_changed(amount: float, balance: float) -> str:
    return f"✅ Транзакция проведена на сумму {amount:.2f}\nТекущий баланс пользователя: {balance:.2f}"