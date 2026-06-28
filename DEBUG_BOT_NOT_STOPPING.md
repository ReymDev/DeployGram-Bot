# Отладка: Бот не останавливается

## Проблема
Пользователь нажал "Остановить" на проекте test2:
- Интерфейс показывает: "Работает: —", RAM: 0 MB, CPU: 0%
- Но бот test2 продолжает отвечать в Telegram

## Команды для проверки на сервере

### 1. Проверить все запущенные контейнеры
```bash
docker ps -a | grep test2
```

Ищем контейнеры с именем содержащим "test2".

### 2. Проверить статус в базе данных
```bash
cd ~/DeployGram-Bot
python3 << EOF
from sqlalchemy import create_engine, select
from models.project import Project
import os

db_url = os.getenv("DATABASE_URL", "sqlite:///./data/bot.db")
engine = create_engine(db_url)

with engine.connect() as conn:
    result = conn.execute(select(Project).where(Project.name == "test2"))
    project = result.fetchone()
    if project:
        print(f"Project ID: {project.id}")
        print(f"Status: {project.status}")
        print(f"Container ID: {project.docker_container_id}")
    else:
        print("Project 'test2' not found")
EOF
```

### 3. Проверить конкретный контейнер
Если нашли container_id из пункта 2:
```bash
docker inspect <container_id> | grep "Running"
```

### 4. Принудительно остановить контейнер
```bash
# Если контейнер все еще работает
docker stop <container_id>
docker rm <container_id>
```

### 5. Проверить все процессы Python
```bash
ps aux | grep python | grep test2
```

### 6. Проверить логи остановки
```bash
cd ~/DeployGram-Bot
docker compose -p mainbot logs --tail 100 bot | grep -i "stop\|test2"
```

## Возможные причины

### Причина 1: VPS Agent не отвечает
Если проект на VPS сервере, проверить:
```bash
# В базе данных проверить server_id проекта
# Затем проверить доступность VPS Agent
curl http://<server_ip>:<port>/health
```

### Причина 2: Docker команда не выполнилась
Проверить есть ли ошибки в логах:
```bash
cd ~/DeployGram-Bot/docker
docker compose -p mainbot logs --tail 200 bot | grep -i error
```

### Причина 3: Контейнер перезапускается автоматически
```bash
docker inspect <container_id> | grep -A 5 "RestartPolicy"
```

Если там `"Name": "always"` - это проблема.

## Решение проблем

### Если контейнер работает локально
```bash
# Найти ID контейнера
docker ps | grep test2

# Остановить
docker stop <container_id>

# Удалить
docker rm <container_id>

# Обновить статус в БД (через Python)
# UPDATE projects SET status='stopped', docker_container_id=NULL WHERE name='test2'
```

### Если проект на VPS
Проблема может быть в VPS Agent - он не останавливает контейнеры.

### Если процесс висит вне Docker
```bash
# Найти процесс
ps aux | grep test2

# Убить процесс
kill -9 <PID>
```

## Исправление в коде

Нужно добавить проверку что контейнер действительно остановился после команды stop.

В `services/project.py`:
```python
async def stop_project(self, project_id: int) -> tuple[bool, str]:
    # ... существующий код ...
    
    # После остановки - проверить что контейнер действительно остановлен
    if project.server_id:
        # VPS проверка
        status = await client.get_container_status(container_id)
        if status.get("running"):
            # Контейнер все еще работает!
            return False, "Ошибка остановки контейнера"
    else:
        # Локальная проверка
        status = await self.docker.get_container_status(container_id)
        if status.get("running"):
            return False, "Ошибка остановки контейнера"
    
    return True, "Проект остановлен"
```

## Временное решение для пользователя

1. Нажать "Остановить" еще раз
2. Подождать 10-15 секунд
3. Проверить статус
4. Если не помогло - написать в поддержку

## Логирование для отладки

Добавить в `services/project.py` детальное логирование:
```python
logger.info(f"Stopping project {project_id}, container {container_id}")
# ... выполнение остановки ...
logger.info(f"Stop command sent for {container_id}")
# ... проверка статуса ...
logger.info(f"Container {container_id} status after stop: {status}")
```
