# 🔧 Быстрое резюме исправления

## Проблема
```
/tmp/venv/bin/python: can't open file '/app/main.py': [Errno 2] No such file or directory
```

## Причина
Volume монтировался с несуществующего пути хоста → контейнер не видел файлы проекта.

## Решение в одну строку

### ❌ Было:
```python
# agent/main.py:71
project_dir = f"/data/projects/{project_id}"  # Путь не существует!
```

### ✅ Стало:
```python
# agent/main.py:71
project_dir = self._get_project_dir(str(project_id))  # /app/data/projects/{project_id}
```

## Измененные файлы

1. **agent/main.py**
   - `create_container()` - исправлен путь к project_dir
   - `upload_project()` - добавлено логирование файлов
   - `create_container()` - добавлено логирование параметров

2. **services/docker_manager.py**
   - `create_container()` - добавлено логирование volume и команды

## Как применить

```bash
# 1. Остановить сервисы
docker-compose down  # или systemctl stop deploygram-*

# 2. Пересобрать (если используется Docker)
docker-compose build --no-cache

# 3. Запустить
docker-compose up -d  # или systemctl start deploygram-*
```

## Проверка

```bash
# 1. Проверить логи агента
docker logs deploygram-agent | grep "Mounting volume"

# 2. Попробовать запустить проект через бота

# 3. Проверить volume в контейнере
docker inspect <container_id> | grep -A 10 "Mounts"
```

## Ожидаемый результат

✅ Проекты запускаются без ошибок  
✅ Логи показывают правильные пути  
✅ Volume монтируется корректно  

## Дополнительная документация

- [BUGFIX_ENTRY_POINT.md](BUGFIX_ENTRY_POINT.md) - детали исправления
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - полная инструкция развертывания
- [docs/PROJECT_STRUCTURE_GUIDE.md](docs/PROJECT_STRUCTURE_GUIDE.md) - для пользователей
- [CHANGELOG.md](CHANGELOG.md) - история изменений
