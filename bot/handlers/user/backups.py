from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.utils.emojis import Emoji, EmojiID

router = Router()


@router.callback_query(F.data.startswith("project_backups_"))
async def backups_menu(callback: CallbackQuery, project_service, db_user, session):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer("Проект не найден", show_alert=True)
        return

    from services.backup import BackupService
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
async def backup_create(callback: CallbackQuery, project_service, db_user, session):
    project_id = int(callback.data.split("_")[-1])

    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer("Нет доступа", show_alert=True)
        return

    from services.backup import BackupService
    backup_svc = BackupService(session)
    await backup_svc.create_backup(project_id, size=0)

    await callback.answer("💾 Бэкап создан!", show_alert=True)


@router.callback_query(F.data.startswith("backup_view_"))
async def backup_view(callback: CallbackQuery, project_service, db_user, session):
    parts = callback.data.split("_")
    project_id = int(parts[2])
    backup_id = int(parts[3])

    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer("Нет доступа", show_alert=True)
        return

    from services.backup import BackupService
    backup_svc = BackupService(session)
    success, msg = await backup_svc.restore_backup(backup_id)

    if success:
        await callback.answer(f"✅ {msg}", show_alert=True)
    else:
        await callback.answer(f"❌ {msg}", show_alert=True)
