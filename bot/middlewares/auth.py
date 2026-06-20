from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, Message, CallbackQuery

from services.user import UserService
from services.project import ProjectService


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        session = data.get("session")
        if session is None:
            return await handler(event, **data)

        user_service = UserService(session)
        project_service = ProjectService(session)

        telegram_user = None
        if isinstance(event, Message) and event.from_user:
            telegram_user = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            telegram_user = event.from_user

        if telegram_user:
            user = await user_service.get_or_create_user(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                full_name=telegram_user.full_name,
            )
            data["db_user"] = user
            data["user_service"] = user_service

        data["project_service"] = project_service

        return await handler(event, **data)
