# Руководство по развертыванию исправлений

## Что было исправлено

Исправлена критическая ошибка, из-за которой контейнеры не могли найти файлы проекта при запуске:
```
/tmp/venv/bin/python: can't open file '/app/main.py': [Errno 2] No such file or directory
```

## Файлы, которые изменились

1. **agent/main.py** - VPS Agent API
2. **services/docker_manager.py** - Docker менеджер

## Как развернуть исправления

### Вариант 1: Docker Compose (рекомендуется)

Если используете Docker Compose:

```bash
cd docker
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Вариант 2: Перезапуск сервисов

Если сервисы запущены отдельно:

#### Agent (VPS Agent):
```bash
# Найти процесс
ps aux | grep "python.*agent"

# Остановить
kill <PID>

# Запустить заново
cd /path/to/DeployGram
python -m agent
```

#### Bot (Telegram Bot):
```bash
# Найти процесс
ps aux | grep "python.*bot"

# Остановить
kill <PID>

# Запустить заново
cd /path/to/DeployGram
python -m bot
```

### Вариант 3: Systemd (если используется)

```bash
sudo systemctl restart deploygram-agent
sudo systemctl restart deploygram-bot
```

## Проверка исправлений

### 1. Проверьте логи агента

После перезапуска агента, логи должны содержать новые записи:

```
VPS Agent started on 0.0.0.0:8080
Uploading project X to /app/data/projects/X
Extracted files for project X: [...]
Creating container for project X: entry_point=main.py, entry_type=script, project_dir=/app/data/projects/X
Mounting volume: host=/app/data/projects/X -> container=/app for project X
Container created successfully: abc123...
```

### 2. Проверьте логи Docker Manager

```
Creating container deploygram_X_ProjectName: entry_point=main.py, command=python -m venv...
Container created successfully: abc123...
```

### 3. Тест запуска проекта

1. Загрузите тестовый проект через бота
2. Попробуйте запустить проект
3. Проект должен успешно запуститься без ошибки "No such file or directory"

## Откат изменений (если нужно)

Если по какой-то причине нужно откатить изменения:

```bash
cd /path/to/DeployGram
git stash  # Сохранить текущие изменения
git checkout <previous-commit>  # Вернуться к предыдущей версии
# Перезапустить сервисы
```

## Мониторинг после развертывания

### Проверьте работающие контейнеры:
```bash
docker ps --filter "label=deploygram=true"
```

### Проверьте логи конкретного контейнера:
```bash
docker logs <container_id>
```

### Проверьте файлы внутри контейнера:
```bash
docker exec <container_id> ls -la /app
```

## Известные проблемы и решения

### Проблема: Контейнер все еще не находит файлы

**Решение:**
1. Проверьте, что файлы действительно загружены:
   ```bash
   ls -la /app/data/projects/<project_id>/
   ```
2. Проверьте volume в контейнере:
   ```bash
   docker inspect <container_id> | grep -A 10 "Mounts"
   ```
3. Проверьте права доступа:
   ```bash
   ls -la /app/data/projects/
   ```

### Проблема: Агент не запускается

**Решение:**
1. Проверьте логи:
   ```bash
   journalctl -u deploygram-agent -f
   ```
2. Проверьте, что порт 8080 свободен:
   ```bash
   netstat -tulpn | grep 8080
   ```

## Поддержка

Если после развертывания исправлений проблемы остаются:

1. Соберите логи:
   - Логи агента: `/app/data/agent.log` или `journalctl -u deploygram-agent`
   - Логи бота: `/app/data/bot.log` или `journalctl -u deploygram-bot`
   - Логи контейнера: `docker logs <container_id>`

2. Проверьте структуру файлов:
   ```bash
   tree /app/data/projects/<project_id>/
   ```

3. Создайте issue с описанием проблемы и логами
