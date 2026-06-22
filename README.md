# DeployGram

Telegram-бот для хостинга Python-проектов в Docker-контейнерах.

## 🔥 Последние обновления

### v1.1.0 - Исправление критических ошибок (2024)

**Исправлена ошибка:** `can't open file '/app/main.py': [Errno 2] No such file or directory`

**Что было сделано:**
- ✅ Исправлен путь монтирования volume в VPS Agent
- ✅ Добавлено детальное логирование для диагностики
- ✅ Улучшена обработка структуры ZIP-архивов
- ✅ Добавлена документация по структуре проектов

**Подробности:**
- [BUGFIX_ENTRY_POINT.md](BUGFIX_ENTRY_POINT.md) - техническое описание исправления
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - руководство по развертыванию
- [docs/PROJECT_STRUCTURE_GUIDE.md](docs/PROJECT_STRUCTURE_GUIDE.md) - структура проектов для пользователей

---

## Возможности

- Загрузка проектов через ZIP архив или GitHub
- Автоматический поиск entry point (main.py, bot.py, run.py, app.py)
- Поддержка Python 3.10, 3.11, 3.12
- Изоляция контейнеров (CPU, RAM, Disk лимиты)
- Мониторинг в реальном времени (CPU, RAM, Disk)
- Файловый менеджер с inline-навигацией
- Мобильный редактор кода
- Система секретов (ENV переменные)
- Бэкапы (Premium)
- Совладельцы с ролями (Owner, Developer)
- Система версий с откатом
- Реферальная система
- Промокоды
- Админ-панель с рассылками
- VPS Agent для удалённых серверов

## Технологии

- Python 3.12
- aiogram 3.x
- SQLAlchemy 2.x (async)
- Alembic
- Redis
- Docker SDK
- aiohttp
- APScheduler
- Pydantic Settings

## Структура проекта

```
DeployGram/
├── bot/              # Telegram-бот
│   ├── handlers/     # Хендлеры (user + admin)
│   ├── keyboards/    # Inline-клавиатуры
│   ├── middlewares/  # Middleware
│   ├── states/       # FSM состояния
│   └── utils/        # Утилиты, эмодзи, шаблоны
├── models/           # SQLAlchemy модели
├── repositories/     # Репозитории (Repository Pattern)
├── services/         # Сервисный слой
├── db/               # Движок БД + Alembic
├── agent/            # VPS Agent
├── docker/           # Docker файлы
└── README.md
```

## Установка

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/your/repo.git
cd DeployGram
```

### 2. Настройте переменные окружения

```bash
cp .env.example .env
```

Отредактируйте `.env`:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789
DATABASE_URL=sqlite+aiosqlite:///data/deploygram.db
REDIS_URL=redis://localhost:6379/0
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Запустите миграции

```bash
alembic upgrade head
```

### 5. Запустите бота

```bash
python -m bot
```

## Docker Compose

```bash
cd docker
docker-compose up -d
```

Это запустит:
- Telegram-бота
- VPS Agent (порт 8080)
- Redis

## Конфигурация

### Тарифы

| Параметр | Free | Premium |
|----------|------|---------|
| Проектов | 1 | 5 |
| RAM | 256 MB | 1024 MB |
| CPU | 0.3 | 1.0 |
| Disk | 100 MB | 500 MB |

### Безопасность контейнеров

- CPU лимиты через `--cpus`
- RAM лимиты через `--memory`
- Disk лимиты через `--storage-opt`
- Нет root прав (user 1000:1000)
- Изолированная файловая система

## Команды бота

- `/start` — Начало работы, регистрация
- `/admin` — Админ-панель (только для ADMIN_IDS)

## Разработка

```bash
# Установка dev зависимостей
pip install -r requirements.txt
pip install ruff mypy

# Линтинг
ruff check .

# Типы
mypy .
```

## Лицензия

MIT
