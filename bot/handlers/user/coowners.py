from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.utils.emojis import Emoji

router = Router()


@router.callback_query(F.data.startswith("project_coowners_"))
async def coowners_menu(callback: CallbackQuery, project_service):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer("Проект не найден", show_alert=True)
        return

    from db.engine import async_session_factory
    from repositories.coowner import CoOwnerRepository

    async with async_session_factory() as session:
        coowner_repo = CoOwnerRepository(session)
        coowners = await coowner_repo.get_by_project_id(project_id)

    from bot.keyboards.user import get_coowners_keyboard
    await callback.message.edit_text(
        f"{Emoji.PEOPLE} <b>Совладельцы: {project.name}</b>\n\n"
        f"Роли:\n"
        f"  <b>Owner</b> — полный доступ\n"
        f"  <b>Developer</b> — запуск, остановка, логи, файлы",
        reply_markup=get_coowners_keyboard(project_id, coowners),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("coowner_add_"))
async def coowner_add(callback: CallbackQuery):
    await callback.answer(
        "Отправьте Telegram ID пользователя для добавления",
        show_alert=True,
    )
