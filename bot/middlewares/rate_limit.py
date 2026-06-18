from __future__ import annotations

from typing import Any, Awaitable, Callable
import time

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 0.5) -> None:
        self.limit = limit
        self.last_call: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id = 0
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id:
            now = time.time()
            last = self.last_call.get(user_id, 0)
            if now - last < self.limit:
                if isinstance(event, CallbackQuery):
                    await event.answer("⏳ Слишком часто!", show_alert=False)
                return None
            self.last_call[user_id] = now

        return await handler(event, data)
