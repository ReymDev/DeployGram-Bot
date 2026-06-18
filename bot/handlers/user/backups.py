from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.utils.emojis import Emoji

router = Router()


@router.callback_query(F.data.startswith("project_backups_"))
async def backups_menu(callback: CallbackQuery, project_service):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer("Проект не найден", show_alert=True)
        return

    from db.engine import async_session_factory
    from services.backup import BackupService

    async with async_session_factory() as session:
        backup_svc = BackupService(session)
        backups = await backup_svc.get_backups(project_id)

    from bot.keyboards.user import get_backups_keyboard
    await callback.message.edit_text(
        f"{Emoji.BOX} <b>Бэкапы: {project.name}</b>\n\n"
        f"Количество: {len(backups)}",
        reply_markup=get_backups_keyboard(project_id, backups),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("backup_create_"))
async def backup_create(callback: CallbackQuery, project_service):
    project_id = int(callback.data.split("_")[-1])

    from db.engine import async_session_factory
    from services.backup import BackupService

    async with async_session_factory() as session:
        backup_svc = BackupService(session)
        await backup_svc.create_backup(project_id, size=0)

    await callback.answer("💾 Бэкап создан!", show_alert=True)


@router.callback_query(F.data.startswith("backup_view_"))
async def backup_view(callback: CallbackQuery):
    await callback.answer("Функция восстановления в разработке", show_alert=True)
