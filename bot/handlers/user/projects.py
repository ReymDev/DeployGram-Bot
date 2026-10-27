from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.user import get_bot_list_keyboard
from bot.utils.text import start_text
from bot.utils.media import edit_photo_or_text

router = Router()


@router.callback_query(F.data == "my_projects")
async def my_projects(callback: CallbackQuery, db_user, project_service):
    projects_with_flags = await project_service.get_all_user_projects(db_user.id)

    if not projects_with_flags:
        await edit_photo_or_text(
            callback.message,
            "📦 У вас пока нет приложений.\n\nНажмите «Развернуть сервис» чтобы начать.",
            "control_panel",
            reply_markup=get_bot_list_keyboard([]),
        )
    else:
        await edit_photo_or_text(
            callback.message,
            f"📦 <b>Ваши приложения</b> ({len(projects_with_flags)})",
            "control_panel",
            reply_markup=get_bot_list_keyboard(projects_with_flags),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("projects_page_"))
async def projects_page(callback: CallbackQuery, db_user, project_service):
    page = int(callback.data.split("_")[-1])
    projects_with_flags = await project_service.get_all_user_projects(db_user.id)
    await edit_photo_or_text(
        callback.message,
        f"📦 <b>Ваши приложения</b> ({len(projects_with_flags)})",
        "control_panel",
        reply_markup=get_bot_list_keyboard(projects_with_flags, page),
    )
    await callback.answer()
