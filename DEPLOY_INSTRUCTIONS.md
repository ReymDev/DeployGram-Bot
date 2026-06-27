# Инструкция по деплою изменений на VPS

## Текущее состояние
- **VPS коммит**: `64b8383` (fix: project rename - add HTML parse mode)
- **Локальный коммит**: `efed85c` (fix: restore subscription/backups/promo/referrals buttons in projects list)
- **Требуется обновление**: ДА

## Команды для применения на сервере

### 1. Подключиться к серверу
```bash
ssh root@94.183.254.95
```

### 2. Перейти в директорию проекта
```bash
cd ~/DeployGram-Bot
```

### 3. Получить изменения с GitHub
```bash
git pull origin main
```

### 4. Применить миграцию БД
```bash
alembic upgrade head
```

### 5. Перезапустить бота
```bash
cd docker
docker compose -p mainbot restart bot
```

### 6. Проверить логи
```bash
docker compose -p mainbot logs --tail=50 bot
```

### 7. Следить за логами в реальном времени (опционально)
```bash
docker compose -p mainbot logs -f bot
```
Выход: `Ctrl+C`

---

## Новые коммиты (что будет применено)

### `f478895` - fix: referral system, deps display, coowner permissions, notifications UI
- ✅ Исправлена реферальная система (теперь правильно засчитывает приглашенных)
- ✅ Зависимости из requirements.txt отображаются в интерфейсе
- ✅ Добавлена система разрешений для совладельцев
- ✅ Исправлен UI уведомлений
- ⚠️ **ТРЕБУЕТ миграции БД** (добавлены поля в таблицу coowners)

### `bf22241` - fix: remove subscription/backups/promo/referrals buttons from projects list
- Убраны кнопки из списка проектов (откачено в следующем коммите)

### `b4b7fda` - fix: remove create project button from welcome menu
- Убрана кнопка "Создать проект" из главного меню

### `4b452bb` - fix: correct button layout
- Промежуточное исправление (откачено в следующем коммите)

### `efed85c` - fix: restore subscription/backups/promo/referrals buttons in projects list
- ✅ **Финальная версия кнопок:**
  - Главное меню: "Мои проекты" + "Подписка", "Бэкапы", "Промокод", "Рефералы"
  - Список проектов (есть проекты): проекты + "Создать проект" + "Подписка", "Бэкапы", "Промокод", "Рефералы"
  - Пока пусто (нет проектов): "Создать проект" + "Подписка", "Бэкапы", "Промокод", "Рефералы"

---

## Измененные файлы
1. `services/referral.py` - реферальная система
2. `bot/handlers/user/bot_manage.py` - отображение зависимостей
3. `models/coowner.py` - поля разрешений
4. `bot/keyboards/user.py` - клавиатуры
5. `bot/keyboards/common.py` - главное меню
6. `bot/handlers/user/coowners.py` - хендлеры разрешений
7. `bot/texts.py` - новые тексты
8. `db/migrations/versions/20260627_add_coowner_permissions.py` - миграция БД

---

## Проверка после деплоя

### Проверить работу реферальной системы:
1. Пригласить тестового пользователя по реферальной ссылке
2. Проверить что в разделе "Рефералы" показывает правильное количество

### Проверить зависимости:
1. Открыть проект → Настройки → Зависимости
2. Убедиться что показываются все пакеты из requirements.txt

### Проверить кнопки:
1. Главное меню - должна быть только "Мои проекты" + доп. функции
2. Список проектов - должны быть все кнопки включая "Создать проект"

### Проверить разрешения совладельцев:
1. Открыть проект → Настройки → Доступ
2. Добавить совладельца
3. Нажать на совладельца - должно открыться меню настройки разрешений

---

## В случае проблем

### Откатиться на предыдущую версию:
```bash
cd ~/DeployGram-Bot
git reset --hard 64b8383
cd docker
docker compose -p mainbot restart bot
```

### Посмотреть ошибки в логах:
```bash
cd ~/DeployGram-Bot/docker
docker compose -p mainbot logs --tail=100 bot
```

### Проверить состояние контейнеров:
```bash
docker compose -p mainbot ps
```
