# 🔧 ИСПРАВЛЕНИЯ (25.06.2026)

## ✅ Исправлено в коммите `0cab95d`

### 1️⃣ Ошибка получения логов контейнера (500 Error)

**Проблема:**
- Агент возвращал ошибку 500 при запросе `/container/{id}/logs`
- Логи были пустыми в боте

**Причина:**
- Некорректная логика фильтрации логов с использованием `StartedAt`
- Фильтр удалял все логи, включая полезные

**Решение:**
- Убрана проблемная логика с `since=started_at`
- Используется только `tail=N` для получения последних строк
- Улучшена фильтрация pip сообщений (только служебные)
- Добавлено детальное логирование с типом ошибки
- Возвращается понятное сообщение если логи пусты

**Файлы:**
- `services/docker_manager.py` → `get_container_logs()`
- `agent/main.py` → `container_logs()`

---

### 2️⃣ Uptime показывался как "—"

**Проблема:**
- В карточке проекта uptime отображался как "—" вместо реального времени
- `⏱ Работает: —`

**Причина:**
- `get_container_stats()` не возвращал `uptime_seconds`
- Отсутствовал расчет времени работы контейнера

**Решение:**
- Добавлен расчет uptime через `dateutil.parser`
- Используется `StartedAt` из атрибутов контейнера
- Возвращается `uptime_seconds` в stats
- Обновлен `format_uptime()` для показа "только что" при 0 секундах

**Файлы:**
- `services/docker_manager.py` → `get_container_stats()`
- `bot/utils/formatters.py` → `format_uptime()`
- `requirements.txt` → добавлен `python-dateutil>=2.8.0`

---

## 📋 Что нужно сделать после деплоя

1. **Установить зависимости:**
   ```bash
   cd ~/DeployGram-Bot
   docker compose -p mainbot down
   docker compose -p mainbot build
   docker compose -p mainbot up -d
   ```

2. **Проверить логи:**
   ```bash
   docker compose -p mainbot logs -f agent
   docker compose -p mainbot logs -f bot
   ```

3. **Тестирование в боте:**
   - Открыть проект
   - Проверить что uptime показывается корректно
   - Нажать "📋 Логи" и убедиться что логи загружаются
   - Проверить что нет ошибок 500 в логах агента

---

## 🎯 Ожидаемый результат

**До:**
```
⏱ Работает: —
📋 Логи: (пусто)
agent-1 | 500 error
```

**После:**
```
⏱ Работает: 2ч 15м
📋 Логи: 
2026-06-25 17:40:15 | INFO | Bot started
2026-06-25 17:40:16 | INFO | Connected to database
✅ Зависимости установлены
```

---

## 🔍 Логирование для диагностики

Теперь в логах агента будет:

```
INFO:__main__:Getting logs for container 493e90... (tail=100)
INFO:__main__:Successfully retrieved logs for container 493e90...: 1523 chars
```

При ошибке:
```
ERROR:__main__:Failed to get logs for container 493e90...
Error: Container not found
Error Type: NotFound
Traceback: ...
```

---

## 📊 Технические детали

### Расчет uptime:
```python
started_at = container.attrs["State"]["StartedAt"]  # "2026-06-25T17:39:45.123Z"
start_time = parser.parse(started_at)              # datetime object
now = datetime.datetime.now(timezone.utc)
uptime_seconds = int((now - start_time).total_seconds())
```

### Фильтрация логов:
- ❌ Удаляем: `Collecting`, `Downloading`, `Installing collected packages`, `Requirement already satisfied`, `[notice]`
- ✅ Оставляем: `Successfully installed` → заменяем на "✅ Зависимости установлены"
- ✅ Оставляем: все логи приложения

---

## 🚀 Следующие шаги

После проверки работы этих исправлений, можно приступать к:

1. ✨ Обновлению остальных хендлеров под новый дизайн
2. 🎨 Удалению всех оставшихся рамок из текстов
3. 📝 Замене `<code>` на `<pre>` для логов
4. 🧪 Настройке Feature Flag системы

---

**Коммит:** `0cab95d`
**Дата:** 25.06.2026
**Автор:** Kiro AI
