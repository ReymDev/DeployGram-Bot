"""
Middleware для ограничения частоты критических операций.
Предотвращает злоупотребление ресурсами Docker и VPS.
"""
from __future__ import annotations

import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery


class OperationRateLimitMiddleware(BaseMiddleware):
    """
    Rate limiting для критических операций:
    - Создание проектов: макс 5 в час
    - Запуск/остановка: макс 20 в час
    - Перезапуск: макс 10 в час
    """
    
    def __init__(self) -> None:
        # Хранилище: {user_id: {operation: [(timestamp, count)]}}
        self.operations: dict[int, dict[str, list[tuple[float, int]]]] = {}
        
        # Лимиты: operation -> (max_count, time_window_seconds)
        self.limits = {
            "create_project": (5, 3600),      # 5 проектов в час
            "start_project": (20, 3600),      # 20 запусков в час
            "stop_project": (20, 3600),       # 20 остановок в час
            "restart_project": (10, 3600),    # 10 перезапусков в час
            "delete_project": (10, 3600),     # 10 удалений в час
            "upload_file": (50, 3600),        # 50 загрузок в час
        }
    
    def _get_operation_from_callback(self, data: str) -> str | None:
        """Определить тип операции по callback_data."""
        if data.startswith("create_confirm"):
            return "create_project"
        elif data.startswith("bot_start_") or data.startswith("project_start_"):
            return "start_project"
        elif data.startswith("bot_stop_") or data.startswith("project_stop_"):
            return "stop_project"
        elif data.startswith("bot_del_confirm_") or data.startswith("project_del_confirm_"):
            return "delete_project"
        return None
    
    def _check_limit(self, user_id: int, operation: str) -> tuple[bool, int]:
        """
        Проверить лимит операции для пользователя.
        
        Returns:
            (allowed, seconds_until_reset)
        """
        if operation not in self.limits:
            return True, 0
        
        max_count, window = self.limits[operation]
        now = time.time()

        if len(self.operations) > 5000:
            self.operations = {
                uid: ops
                for uid, ops in self.operations.items()
                if any(ts >= now - max(w for _, w in self.limits.values()) for ts, _ in ops.get(operation, []))
            }

        # Инициализируем хранилище для пользователя
        if user_id not in self.operations:
            self.operations[user_id] = {}
        
        if operation not in self.operations[user_id]:
            self.operations[user_id][operation] = []
        
        # Очистка старых записей
        self.operations[user_id][operation] = [
            (ts, count) for ts, count in self.operations[user_id][operation]
            if now - ts < window
        ]
        
        # Подсчет операций в текущем окне
        total_count = sum(count for _, count in self.operations[user_id][operation])
        
        if total_count >= max_count:
            # Вычисляем время до сброса
            oldest_ts = min(ts for ts, _ in self.operations[user_id][operation])
            seconds_until_reset = int(window - (now - oldest_ts))
            return False, seconds_until_reset
        
        # Добавляем текущую операцию
        self.operations[user_id][operation].append((now, 1))
        return True, 0
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
        **kwargs,
    ) -> Any:
        # Применяем только к callback query
        if not isinstance(event, CallbackQuery):
            return await handler(event, data)
        
        if not event.from_user or not event.data:
            return await handler(event, data)
        
        user_id = event.from_user.id
        operation = self._get_operation_from_callback(event.data)
        
        # Если операция не критическая, пропускаем
        if operation is None:
            return await handler(event, data)
        
        # Проверяем лимит
        allowed, seconds = self._check_limit(user_id, operation)
        
        if not allowed:
            minutes = seconds // 60
            seconds_left = seconds % 60
            time_str = f"{minutes}м {seconds_left}с" if minutes > 0 else f"{seconds_left}с"
            
            await event.answer(
                f"⏳ Слишком много операций. Попробуйте через {time_str}",
                show_alert=True,
            )
            return None
        
        return await handler(event, data)
