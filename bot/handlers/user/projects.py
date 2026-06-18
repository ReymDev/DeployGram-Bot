from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.user import get_project_list_keyboard
from bot.utils.text import start_text

router = Router()


@router.callback_query(F.data == "my_projects")
async def my_projects(callback: CallbackQuery, db_user, project_service):
    projects = await project_service.get_user_projects(db_user.id)

    if not projects:
        await callback.message.edit_text(
            "📦 У вас пока нет проектов.\n\nНажмите «Создать проект» чтобы начать.",
            reply_markup=get_project_list_keyboard([]),
        )
    else:
        await callback.message.edit_text(
            f"📦 <b>Ваши проекты</b> ({len(projects)})",
            reply_markup=get_project_list_keyboard(projects),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("projects_page_"))
async def projects_page(callback: CallbackQuery, db_user, project_service):
    page = int(callback.data.split("_")[-1])
    projects = await project_service.get_user_projects(db_user.id)
    await callback.message.edit_text(
        f"📦 <b>Ваши проекты</b> ({len(projects)})",
        reply_markup=get_project_list_keyboard(projects, page),
    )
    await callback.answer()
