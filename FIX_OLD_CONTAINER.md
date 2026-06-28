# Исправление: Старый контейнер не останавливается

## Проблема
При запуске проекта создаются новые контейнеры, но старый контейнер `deploygram_1_test2` (созданный 2 дня назад) продолжает работать.

```
CONTAINER ID   IMAGE              STATUS          NAMES
824cc7f26d44   python:3.12-slim   Up 6 hours      deploygram_1_test2  ← СТАРЫЙ
```

Новые контейнеры создаются и останавливаются, но ID не совпадает со старым.

## Причина
При создании контейнера Agent удаляет старый контейнер по имени:
```python
# Из логов:
INFO:services.docker_manager:Removed old container: deploygram_1_test2
```

Но после этого Docker создает новый контейнер с **другим ID**, а старый остается работать!

Возможные причины:
1. Старый контейнер был создан вручную, не через DeployGram
2. Container name conflict - Docker не может удалить старый контейнер
3. Старый контейнер не принадлежит к этому проекту (другой network/volume)

## Временное решение (на сервере)

### Шаг 1: Остановить и удалить старый контейнер
```bash
# Остановить
docker stop 824cc7f26d44

# Удалить
docker rm 824cc7f26d44

# Проверить
docker ps | grep deploygram_1_test2
```

### Шаг 2: Очистить все остановленные контейнеры
```bash
docker container prune -f
```

### Шаг 3: Проверить volumes
```bash
# Показать все volumes
docker volume ls | grep deploygram

# Если есть неиспользуемые - удалить
docker volume prune -f
```

### Шаг 4: Перезапустить проект через DeployGram
Теперь проект должен создать новый контейнер и работать правильно.

## Долгосрочное решение

### Исправление в коде

Нужно улучшить логику create_container в Agent:

```python
async def create_container(self, ...):
    container_name = f"deploygram_{project_id}_{project_name}"
    
    # 1. Найти ВСЕ контейнеры с этим именем
    existing = self.client.containers.list(
        all=True,  # Включая остановленные
        filters={"name": container_name}
    )
    
    # 2. Остановить и удалить ВСЕ найденные
    for container in existing:
        try:
            container.stop(timeout=10)
            container.remove(force=True)
            logger.info(f"Removed old container: {container.id}")
        except Exception as e:
            logger.warning(f"Failed to remove {container.id}: {e}")
    
    # 3. Создать новый контейнер
    new_container = self.client.containers.create(...)
    return new_container.id
```

### Проверка в stop_project

Добавить проверку что контейнер действительно остановился:

```python
async def stop_project(self, project_id):
    # ... остановка ...
    
    # Проверка через имя контейнера
    container_name = f"deploygram_{project_id}_*"
    running = await self.docker.list_containers(filters={"name": container_name, "status": "running"})
    
    if running:
        logger.error(f"Containers still running: {running}")
        # Принудительная остановка
        for c in running:
            await self.docker.stop_container(c.id)
```

## Команды для отладки

### Найти все контейнеры проекта
```bash
docker ps -a | grep deploygram_1
```

### Проверить container_id в БД
```bash
cd ~/DeployGram-Bot
sqlite3 data/bot.db "SELECT id, name, docker_container_id, status FROM projects WHERE name='test2';"
```

### Сравнить ID
- ID в БД: `???`
- ID в docker ps: `824cc7f26d44`

Если не совпадают - проблема!

### Принудительная очистка
```bash
# Остановить ВСЕ контейнеры проекта 1
docker ps -a | grep "deploygram_1" | awk '{print $1}' | xargs docker stop
docker ps -a | grep "deploygram_1" | awk '{print $1}' | xargs docker rm

# Очистить volumes проекта 1
docker volume ls | grep "deploygram.*_1" | awk '{print $2}' | xargs docker volume rm
```

## Предотвращение

### 1. Добавить healthcheck
```python
# При создании контейнера
container = self.client.containers.create(
    ...
    healthcheck={
        "test": ["CMD", "python", "-c", "print('ok')"],
        "interval": 30000000000,  # 30 секунд
        "timeout": 10000000000,   # 10 секунд
        "retries": 3
    }
)
```

### 2. Добавить labels
```python
container = self.client.containers.create(
    ...
    labels={
        "deploygram.project_id": str(project_id),
        "deploygram.project_name": project_name,
        "deploygram.created_at": str(datetime.now())
    }
)
```

Затем можно искать контейнеры по labels:
```python
containers = self.client.containers.list(
    all=True,
    filters={"label": f"deploygram.project_id={project_id}"}
)
```

### 3. Периодическая очистка
Добавить задачу в scheduler:
```python
async def cleanup_orphaned_containers(self):
    """Удалить контейнеры которых нет в БД."""
    # Получить все deploygram контейнеры
    # Сверить с БД
    # Удалить лишние
```

## Статус исправления

- ⏳ **Временное решение:** Остановить старый контейнер вручную
- 🔜 **Улучшение create_container:** TODO
- 🔜 **Проверка по имени:** TODO  
- 🔜 **Labels и cleanup:** TODO
