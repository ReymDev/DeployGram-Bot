# Исправление: Верификация остановки контейнеров

## Проблема
Пользователь нажимал "Остановить" на проекте, интерфейс показывал "остановлено", но бот продолжал работать.

## Причина
После команды `docker.stop_container()` не было проверки что контейнер действительно остановился. Возможные сценарии:
1. Команда не выполнилась
2. Контейнер перезапустился автоматически
3. Процесс завис
4. VPS Agent не выполнил команду

## Решение

### Изменения в `services/project.py`

Добавлена верификация после остановки контейнера:

```python
async def stop_project(self, project_id: int):
    # ... существующий код ...
    
    await docker.stop_container(container_id)
    
    # ✅ НОВОЕ: Верификация остановки
    await asyncio.sleep(2)  # Ждем остановки
    status = await docker.get_container_status(container_id)
    
    if status.get("running"):
        logger.error(f"Container {container_id} still running after stop")
        return False, "Ошибка остановки: контейнер все еще работает"
    
    # Только после проверки обновляем статус в БД
    await self.project_repo.update(project_id, status="stopped")
    return True, "Проект остановлен"
```

### Что изменилось

**До:**
1. Отправить команду stop
2. Сразу обновить статус в БД как "stopped"
3. Вернуть успех

**После:**
1. Отправить команду stop
2. Подождать 2 секунды
3. **Проверить что контейнер действительно остановился**
4. Если все еще работает → вернуть ошибку
5. Только если остановлен → обновить БД

### Логирование

Добавлено детальное логирование:
- `Stopping container {id} on VPS {ip}` - начало остановки
- `Container {id} still running after stop command` - ошибка
- `Project {id} stopped successfully` - успех

## Тестирование

### Нормальная остановка
1. Нажать "Остановить"
2. Увидеть "✅ Проект остановлен"
3. Контейнер действительно остановлен

### Ошибка остановки
1. Нажать "Остановить"
2. Увидеть "❌ Ошибка остановки: контейнер все еще работает"
3. Контейнер продолжает работать
4. Статус в БД остается "running"

## Проверка на сервере

После деплоя можно проверить:

```bash
# 1. Остановить проект через интерфейс
# 2. Проверить логи
cd ~/DeployGram-Bot/docker
docker compose -p mainbot logs --tail 50 bot | grep -i "stop"

# Должны увидеть:
# Stopping container abc123 on VPS 1.2.3.4
# Project 5 stopped successfully
```

Если контейнер не остановится:
```
# В логах будет:
# Container abc123 still running after stop command
# И пользователь увидит ошибку в интерфейсе
```

## Для отладки

Если проблема повторяется:

1. **Проверить контейнер вручную:**
```bash
docker ps | grep <project_name>
docker stop <container_id>
docker ps -a | grep <container_id>  # Должен быть Exited
```

2. **Проверить политику перезапуска:**
```bash
docker inspect <container_id> | grep -A 5 "RestartPolicy"
```

Если там `"Name": "always"` - нужно изменить на `"no"`.

3. **Проверить VPS Agent:**
```bash
curl http://<vps_ip>:<port>/containers/<container_id>/status
```

## Дополнительные улучшения (TODO)

1. Добавить retry логику - попытаться остановить 3 раза
2. Добавить force stop если graceful не сработал
3. Отправлять уведомление владельцу если контейнер не останавливается
4. Добавить телеметрию неудачных остановок

## Файлы изменены

- `services/project.py` - добавлена верификация в `stop_project()`
