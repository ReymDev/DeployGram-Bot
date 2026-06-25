# 🚀 РУКОВОДСТВО ПО ВНЕДРЕНИЮ НОВОГО ДИЗАЙНА

## 📋 СОДЕРЖАНИЕ
1. [Быстрый старт](#быстрый-старт)
2. [Пошаговая инструкция](#пошаговая-инструкция)
3. [Feature Flag система](#feature-flag-система)
4. [Примеры миграции](#примеры-миграции)
5. [Тестирование](#тестирование)
6. [Откат изменений](#откат-изменений)

---

## ⚡ БЫСТРЫЙ СТАРТ

### Что уже сделано ✅

```
bot/new_design/
├── texts_v2.py           # ✅ Новые тексты
├── keyboards_v2.py       # ✅ Новые клавиатуры  
├── handlers/
│   └── start_v2.py       # ✅ Пример нового хендлера
├── DESIGN_CONCEPT.md     # ✅ Концепция дизайна
└── IMPLEMENTATION_GUIDE.md # ✅ Эта инструкция
```

### Что нужно сделать 📝

1. **Добавить Feature Flag** (5 минут)
2. **Создать адаптер** (10 минут)
3. **Обновить хендлеры** (2-3 дня)
4. **Протестировать** (1-2 дня)
5. **Запустить A/B тест** (1-2 недели)

---

## 📖 ПОШАГОВАЯ ИНСТРУКЦИЯ

### Шаг 1: Добавить Feature Flag

**Файл:** `bot/config.py`

```python
# В конец файла добавить:

# ═══════════════════════════════════════════════════════════════
# 🎨 ДИЗАЙН
# ═══════════════════════════════════════════════════════════════

USE_NEW_DESIGN = os.getenv("USE_NEW_DESIGN", "false").lower() == "true"
```

**Файл:** `.env`

```bash
# Добавить переменную (по умолчанию выключено)
USE_NEW_DESIGN=false
```

---

### Шаг 2: Создать адаптер дизайна

**Создать файл:** `bot/adapters/design.py`

```python
"""
Адаптер для переключения между старым и новым дизайном.
"""

from bot.config import settings


def get_texts():
    """Получить модуль с текстами."""
    if settings.USE_NEW_DESIGN:
        from bot.new_design import texts_v2
        return texts_v2
    else:
        from bot import texts
        return texts


def get_keyboards():
    """Получить модуль с клавиатурами."""
    if settings.USE_NEW_DESIGN:
        from bot.new_design import keyboards_v2
        return keyboards_v2
    else:
        from bot.keyboards import user
        return user


# Синглтон экземпляры для удобства
texts = get_texts()
keyboards = get_keyboards()
```

**Создать файл:** `bot/adapters/__init__.py`

```python
from bot.adapters.design import texts, keyboards

__all__ = ["texts", "keyboards"]
```

---

### Шаг 3: Обновить хендлеры

#### Пример 1: Простое обновление (start.py)

**Было:**
```python
from bot import texts
from bot.keyboards.user import get_main_keyboard

@router.message(CommandStart())
async def cmd_start(message: Message, db_user):
    await message.answer(
        texts.WELCOME_TEXT,
        reply_markup=get_main_keyboard()
    )
```

**Стало:**
```python
from bot.adapters import texts, keyboards

@router.message(CommandStart())
async def cmd_start(message: Message, db_user, project_service):
    # Если новый дизайн - используем адаптивное приветствие
    if hasattr(texts, 'home_screen'):
        projects = await project_service.get_user_projects(db_user.id)
        text = texts.home_screen(message.from_user.first_name, len(projects))
        kb = keyboards.home_menu(has_projects=len(projects) > 0)
    else:
        text = texts.WELCOME_TEXT
        kb = keyboards.get_main_keyboard()
    
    await message.answer(text, reply_markup=kb, parse_mode="HTML")
```

#### Пример 2: Полная замена хендлера

**Вариант A: Условный импорт**

```python
# bot/handlers/user/start.py

from bot.config import settings

if settings.USE_NEW_DESIGN:
    from bot.new_design.handlers.start_v2 import router
else:
    # Старый код здесь
    from aiogram import Router
    router = Router()
    
    @router.message(CommandStart())
    async def cmd_start(message: Message):
        # ... старый код
```

**Вариант B: Отдельные роутеры**

```python
# bot/main.py

from bot.config import settings

if settings.USE_NEW_DESIGN:
    from bot.new_design.handlers import start_v2 as start_router
else:
    from bot.handlers.user import start as start_router

dp.include_router(start_router.router)
```

---

### Шаг 4: Обновить регистрацию роутеров

**Файл:** `bot/main.py`

```python
def setup_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    # Middlewares
    dp.message.middleware(DatabaseMiddleware())
    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(OperationRateLimitMiddleware())

    dp.callback_query.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(OperationRateLimitMiddleware())

    # Роутеры с поддержкой нового дизайна
    if settings.USE_NEW_DESIGN:
        from bot.new_design.handlers import start_v2
        dp.include_router(start_v2.router)
        # TODO: Добавить остальные v2 хендлеры
    else:
        from bot.handlers.user import start
        dp.include_router(start.router)
    
    # Роутеры без изменений (работают с обоими дизайнами через адаптер)
    dp.include_router(admin_router)
    
    return dp
```

---

## 🔧 FEATURE FLAG СИСТЕМА

### Способы включения нового дизайна

#### 1. Глобальное включение (через .env)

```bash
# .env
USE_NEW_DESIGN=true
```

Перезапустить бота:
```bash
docker compose -p mainbot restart
```

#### 2. A/B тестирование (по user_id)

**Создать файл:** `bot/utils/ab_test.py`

```python
"""
A/B тестирование нового дизайна.
"""

def should_use_new_design(user_id: int) -> bool:
    """
    Определить, показывать ли пользователю новый дизайн.
    
    Правила:
    - 50% пользователей видят новый дизайн (чётные ID)
    - 50% видят старый дизайн (нечётные ID)
    """
    from bot.config import settings
    
    # Если глобально включен - всем показываем новый
    if settings.USE_NEW_DESIGN:
        return True
    
    # Если глобально выключен - A/B тест по user_id
    # Чётные ID -> новый дизайн
    return user_id % 2 == 0
```

**Обновить:** `bot/middlewares/design.py`

```python
"""
Middleware для A/B тестирования дизайна.
"""

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from bot.utils.ab_test import should_use_new_design


class DesignMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        # Определяем, какой дизайн показывать
        if event.from_user:
            data["use_new_design"] = should_use_new_design(event.from_user.id)
        else:
            data["use_new_design"] = False
        
        return await handler(event, data)
```

Зарегистрировать middleware в `bot/main.py`:

```python
from bot.middlewares.design import DesignMiddleware

dp.message.middleware(DesignMiddleware())
dp.callback_query.middleware(DesignMiddleware())
```

Использовать в хендлерах:

```python
@router.message(CommandStart())
async def cmd_start(message: Message, use_new_design: bool = False):
    if use_new_design:
        # Новый дизайн
        from bot.new_design import texts_v2, keyboards_v2
        text = texts_v2.home_screen(...)
        kb = keyboards_v2.home_menu(...)
    else:
        # Старый дизайн
        from bot import texts
        text = texts.WELCOME_TEXT
        kb = ...
```

#### 3. Бета-доступ (для определённых пользователей)

```python
# bot/config.py

BETA_USERS = list(map(int, os.getenv("BETA_USERS", "").split(",")))

def is_beta_user(user_id: int) -> bool:
    return user_id in BETA_USERS
```

```bash
# .env
BETA_USERS=123456789,987654321
```

---

## 📊 ПРИМЕРЫ МИГРАЦИИ

### Миграция 1: Главный экран (start.py)

**Этап 1: Адаптер**

```python
# bot/handlers/user/start.py

from bot.adapters import texts, keyboards
from bot.config import settings

@router.message(CommandStart())
async def cmd_start(message: Message, db_user, project_service):
    if settings.USE_NEW_DESIGN:
        # Новый дизайн
        projects = await project_service.get_user_projects(db_user.id)
        text = texts.home_screen(message.from_user.first_name, len(projects))
        kb = keyboards.home_menu(has_projects=len(projects) > 0)
    else:
        # Старый дизайн
        text = texts.welcome_text(message.from_user.first_name)
        kb = keyboards.get_main_keyboard()
    
    await message.answer(text, reply_markup=kb, parse_mode="HTML")
```

**Этап 2: Полная замена (после тестирования)**

```python
# Просто использовать новый хендлер
from bot.new_design.handlers.start_v2 import router
```

### Миграция 2: Список проектов (bot_manage.py)

**Старый код:**
```python
@router.callback_query(F.data == "control_panel")
async def control_panel(callback: CallbackQuery, db_user, project_service):
    projects = await project_service.get_user_projects(db_user.id)
    
    text = "📋 <b>Обзор инфраструктуры</b>"
    await callback.message.edit_text(
        text,
        reply_markup=get_bot_list_keyboard(projects)
    )
```

**Новый код (через адаптер):**
```python
from bot.adapters import texts, keyboards

@router.callback_query(F.data.in_(["control_panel", "my_projects"]))
async def show_projects(callback: CallbackQuery, db_user, project_service):
    projects = await project_service.get_user_projects(db_user.id)
    
    if hasattr(texts, 'MY_PROJECTS_TITLE'):
        # Новый дизайн
        text = texts.MY_PROJECTS_TITLE if projects else texts.EMPTY_PROJECTS
        kb = keyboards.projects_list(projects) if projects else keyboards.create_project_upload_method()
    else:
        # Старый дизайн
        text = texts.CONTROL_PANEL_TEXT
        kb = keyboards.get_bot_list_keyboard(projects)
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Чек-лист для тестирования

#### Новый пользователь (нет проектов)

- [ ] Команда /start показывает приветствие
- [ ] Кнопка "Создать первый проект" работает
- [ ] Кнопка "Как это работает?" открывает помощь
- [ ] Создание проекта проходит все 3 шага
- [ ] После создания показывается "Всё готово!"
- [ ] Запуск проекта работает

#### Опытный пользователь (есть проекты)

- [ ] Команда /start показывает количество проектов
- [ ] Список проектов отображается корректно
- [ ] Пагинация работает (если >6 проектов)
- [ ] Открытие проекта показывает панель управления
- [ ] Все действия (старт/стоп/рестарт) работают
- [ ] Логи показываются правильно
- [ ] Файловый менеджер работает
- [ ] Настройки открываются

#### Подписка и платежи

- [ ] Меню подписки показывает текущий тариф
- [ ] Прогресс-бар лимита проектов корректен
- [ ] Upgrade до Premium работает
- [ ] Промокод активируется

#### Граничные случаи

- [ ] Проект не найден - показывает ошибку
- [ ] Нет доступа - показывает ошибку
- [ ] Лимит проектов - предлагает обновиться
- [ ] Файл слишком большой - показывает ошибку
- [ ] Сетевая ошибка - обрабатывается корректно

### Автоматические тесты

**Создать файл:** `tests/test_new_design.py`

```python
"""
Тесты нового дизайна.
"""

import pytest
from bot.new_design import texts_v2, keyboards_v2


class TestTexts:
    """Тесты текстов."""
    
    def test_home_screen_new_user(self):
        """Приветствие для нового пользователя."""
        text = texts_v2.home_screen("Тест", 0)
        assert "Привет" in text
        assert "пока нет проектов" in text
    
    def test_home_screen_existing_user(self):
        """Приветствие для существующего пользователя."""
        text = texts_v2.home_screen("Тест", 3)
        assert "С возвращением" in text
        assert "3" in text
    
    def test_project_card(self):
        """Карточка проекта."""
        text = texts_v2.project_card(
            name="test",
            status="running",
            uptime="1ч 30м",
            memory=128.0,
            cpu=25.5
        )
        assert "test" in text
        assert "Работает" in text
        assert "128" in text
        assert "25.5" in text


class TestKeyboards:
    """Тесты клавиатур."""
    
    def test_home_menu_new_user(self):
        """Главное меню для нового пользователя."""
        kb = keyboards_v2.home_menu(has_projects=False)
        buttons = kb.inline_keyboard
        
        # Проверяем наличие "Создать первый проект"
        assert any("Создать первый" in b.text for row in buttons for b in row)
    
    def test_home_menu_existing_user(self):
        """Главное меню для существующего пользователя."""
        kb = keyboards_v2.home_menu(has_projects=True)
        buttons = kb.inline_keyboard
        
        # Проверяем наличие "Мои проекты"
        assert any("Мои проекты" in b.text for row in buttons for b in row)
    
    def test_project_control_buttons(self):
        """Кнопки управления проектом."""
        kb = keyboards_v2.project_control(1, "running", is_owner=True)
        buttons = kb.inline_keyboard
        
        # Проверяем наличие основных кнопок
        button_texts = [b.text for row in buttons for b in row]
        assert "Остановить" in button_texts
        assert "Логи" in button_texts
        assert "Настройки" in button_texts
```

Запустить тесты:

```bash
pytest tests/test_new_design.py -v
```

---

## 🔄 ОТКАТ ИЗМЕНЕНИЙ

### Быстрый откат (через .env)

```bash
# .env
USE_NEW_DESIGN=false
```

Перезапустить:
```bash
docker compose -p mainbot restart
```

### Откат через Git

```bash
# Откатить последний коммит
git revert HEAD

# Откатить конкретный коммит
git revert <commit-hash>

# Пуш
git push origin main
```

### Откат через Docker

```bash
# Откатить на предыдущую версию образа
docker compose -p mainbot down
docker pull your-registry/deploygram-bot:previous-tag
docker compose -p mainbot up -d
```

---

## 📈 МОНИТОРИНГ И МЕТРИКИ

### Что отслеживать

1. **Конверсия:**
   - % пользователей, создавших первый проект
   - Время от регистрации до первого проекта

2. **Ошибки:**
   - Количество ошибок при создании
   - Количество неудачных запусков

3. **Engagement:**
   - Количество проектов на пользователя
   - Частота использования

4. **Фидбек:**
   - Оценки пользователей
   - Комментарии в поддержке

### Логирование

```python
# В каждом хендлере добавить:
import logging

logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def cmd_start(message: Message, use_new_design: bool = False):
    logger.info(
        f"User {message.from_user.id} started bot. "
        f"Design: {'new' if use_new_design else 'old'}"
    )
    # ... код хендлера
```

---

## ✅ ЧЕКЛИСТ ГОТОВНОСТИ К ЗАПУСКУ

### Перед включением на 10% пользователей

- [ ] Feature flag работает
- [ ] Адаптер создан и протестирован
- [ ] Главный экран работает для нового дизайна
- [ ] Создание проекта работает
- [ ] Управление проектом работает
- [ ] Все тесты проходят
- [ ] Логирование настроено
- [ ] Откат протестирован

### Перед включением на 50% пользователей

- [ ] 10% тест прошёл успешно (>3 дня)
- [ ] Метрики показывают улучшение
- [ ] Критических ошибок нет
- [ ] Фидбек положительный
- [ ] Команда готова к поддержке

### Перед полным переходом

- [ ] 50% тест прошёл успешно (>1 неделя)
- [ ] Все метрики улучшились
- [ ] Нет жалоб на новый дизайн
- [ ] Документация обновлена
- [ ] Команда обучена

---

## 📞 ПОДДЕРЖКА

**Документация:** `bot/new_design/DESIGN_CONCEPT.md`
**Примеры:** `bot/new_design/handlers/start_v2.py`
**Тесты:** `tests/test_new_design.py`

**Для вопросов:** Обратитесь к команде разработки
