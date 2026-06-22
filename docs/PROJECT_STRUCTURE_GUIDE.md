# Руководство по структуре проекта для DeployGram

## Поддерживаемые структуры проектов

DeployGram автоматически определяет структуру вашего проекта и настраивает окружение для запуска.

---

## ✅ Структура 1: Плоская (рекомендуется)

Все файлы в корне ZIP-архива:

```
project.zip
├── main.py          ← entry point
├── requirements.txt
├── config.py
└── handlers/
    ├── start.py
    └── commands.py
```

**Entry point:** `main.py`  
**Entry type:** `script`

---

## ✅ Структура 2: С вложенной папкой

ZIP содержит одну папку с проектом внутри:

```
project.zip
└── my_bot/          ← единственная папка
    ├── main.py      ← entry point
    ├── requirements.txt
    └── handlers/
```

**Entry point:** `main.py` (система автоматически найдет в `my_bot/`)  
**Entry type:** `script`

---

## ✅ Структура 3: Модульная структура

Проект как Python-пакет:

```
project.zip
├── bot/
│   ├── __init__.py
│   ├── main.py      ← точка входа
│   └── handlers/
├── requirements.txt
└── README.md
```

**Entry point:** `bot.main` (без .py)  
**Entry type:** `module`  
**Автоматически устанавливается:** `PYTHONPATH=/app`

---

## ✅ Структура 4: С подпапкой и вложенным entry point

```
project.zip
└── telegram_bot/
    ├── src/
    │   └── main.py  ← entry point
    ├── requirements.txt
    └── config.py
```

**Entry point:** `src/main.py`  
**Entry type:** `script`  
**Система автоматически найдет:** `telegram_bot/src/main.py`

---

## 📦 Автопоиск entry point

Если вы не указали entry point, система автоматически ищет в следующем порядке:

1. `main.py`
2. `bot.py`
3. `run.py`
4. `app.py`

---

## 🔧 Requirements.txt

### Где можно разместить:

1. **В корне проекта:**
   ```
   project.zip
   ├── requirements.txt  ← здесь
   └── main.py
   ```

2. **Рядом с entry point:**
   ```
   project.zip
   └── src/
       ├── requirements.txt  ← здесь
       └── main.py
   ```

Система автоматически найдет `requirements.txt` и установит зависимости перед запуском.

---

## 🚫 Неподдерживаемые структуры

### ❌ Несколько папок верхнего уровня без точного указания

```
project.zip
├── bot1/
│   └── main.py
└── bot2/
    └── main.py
```

**Решение:** Укажите полный путь, например: `bot1/main.py`

### ❌ Entry point вне ZIP-архива

Убедитесь, что все файлы упакованы в ZIP правильно.

---

## 💡 Примеры правильных конфигураций

### Пример 1: Простой бот на aiogram

```
my_telegram_bot.zip
├── main.py
├── requirements.txt  # aiogram>=3.0
├── config.py
└── handlers/
    ├── __init__.py
    ├── start.py
    └── echo.py
```

**Настройки в DeployGram:**
- Entry point: `main.py`
- Entry type: `script`
- Python: `3.12`

### Пример 2: Структурированный проект

```
bot_project.zip
└── telegram_bot/
    ├── bot/
    │   ├── __init__.py
    │   ├── main.py
    │   └── handlers/
    ├── requirements.txt
    └── .env.example
```

**Настройки в DeployGram:**
- Entry point: `main.py` (система найдет в `telegram_bot/`)
- Entry type: `script`
- Python: `3.12`

### Пример 3: Модульный запуск

```
my_app.zip
├── app/
│   ├── __init__.py
│   ├── __main__.py  ← python -m app запустит этот файл
│   └── core.py
└── requirements.txt
```

**Настройки в DeployGram:**
- Entry point: `app`
- Entry type: `module`
- Python: `3.12`

---

## 🔍 Диагностика проблем

### Ошибка: "can't open file '/app/main.py'"

**Причина:** Entry point указан неправильно или файл не существует.

**Решение:**
1. Проверьте структуру ZIP:
   ```bash
   unzip -l project.zip
   ```
2. Убедитесь, что путь к entry point правильный
3. Используйте автопоиск - не указывайте entry point, система найдет сама

### Ошибка: "ModuleNotFoundError"

**Причина:** Для модульного запуска неправильно указан путь.

**Решение:**
1. Проверьте наличие `__init__.py` в папках
2. Используйте `script` вместо `module`, если не нужна модульная структура
3. Убедитесь, что путь указан без `.py` для модулей

### Ошибка: "No module named 'aiogram'" (или другая библиотека)

**Причина:** `requirements.txt` не найден или не содержит нужную библиотеку.

**Решение:**
1. Добавьте `requirements.txt` в корень проекта или рядом с entry point
2. Укажите все зависимости:
   ```
   aiogram==3.4.1
   aiohttp==3.9.1
   python-dotenv==1.0.0
   ```

---

## 📝 Рекомендации

1. **Используйте плоскую структуру** для простых ботов
2. **Добавляйте requirements.txt** в корень проекта
3. **Тестируйте локально** перед загрузкой:
   ```bash
   python main.py  # для script
   python -m module_name  # для module
   ```
4. **Используйте .gitignore** и не включайте в ZIP:
   - `.env` (используйте секреты в DeployGram)
   - `__pycache__`
   - `.venv` или `venv`
   - `.git`

5. **Проверяйте ZIP перед загрузкой:**
   ```bash
   unzip -l project.zip
   ```

---

## 🎯 Быстрый чеклист

- [ ] Файлы упакованы в ZIP
- [ ] Entry point существует и указан правильно
- [ ] `requirements.txt` в корне или рядом с entry point
- [ ] Нет лишних файлов (.env, venv, __pycache__)
- [ ] Структура проверена через `unzip -l`
- [ ] Код протестирован локально

---

## 🆘 Получить помощь

Если проблемы остаются:

1. Посмотрите логи в боте (кнопка "📊 Логи")
2. Проверьте доступные файлы через "📁 Файлы"
3. Обратитесь в поддержку с:
   - Структурой ZIP (`unzip -l project.zip`)
   - Логами из бота
   - Настройками entry point
