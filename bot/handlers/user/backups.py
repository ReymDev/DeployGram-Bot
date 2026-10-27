from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.utils.emojis import Emoji
from bot.utils.media import edit_photo_or_text
from bot.keyboards.common import get_back_keyboard
from bot import texts

router = Router()


@router.callback_query(F.data == "backups_list")
async def backups_list(callback: CallbackQuery, db_user, project_service):
    projects = await project_service.get_user_projects(db_user.id)

    if not projects:
        text = texts.BACKUPS_LIST_EMPTY_TEXT
        await edit_photo_or_text(
            callback.message,
            text,
            "backups",
            reply_markup=get_back_keyboard("main_menu"),
        )
    else:
        text = texts.BACKUPS_LIST_TEXT

        from bot.keyboards.user import get_backups_list_keyboard
        await edit_photo_or_text(
            callback.message,
            text,
            "backups",
            reply_markup=get_backups_list_keyboard(projects),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("backups_bot_"))
async def backups_bot(callback: CallbackQuery, db_user, project_service, session):
    project_id = int(callback.data.replace("backups_bot_", ""))
    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return

    from services.backup import BackupService
    backup_svc = BackupService(session)
    backups = await backup_svc.get_backups(project_id)

    text = texts.backups_bot_text(project.name, len(backups))

    from bot.keyboards.user import get_backups_keyboard
    await edit_photo_or_text(
        callback.message,
        text,
        "create_backup",
        reply_markup=get_backups_keyboard(project_id, backups),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("backup_create_"))
async def backup_create(callback: CallbackQuery, project_service, db_user, session):
    project_id = int(callback.data.replace("backup_create_", ""))

    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer(texts.ERROR_NO_ACCESS, show_alert=True)
        return

    from services.backup import BackupService
    backup_svc = BackupService(session)
    backup = await backup_svc.create_backup(project_id, size=0)
    if backup is None:
        await callback.answer(texts.BACKUP_CREATE_ERROR, show_alert=True)
        return

    from bot.utils.text import plain_text
    await callback.answer(plain_text(texts.SUCCESS_BACKUP_CREATED), show_alert=True)


@router.callback_query(F.data.startswith("backup_view_"))
async def backup_view(callback: CallbackQuery, project_service, db_user, session):
    parts = callback.data.split("_")
    project_id = int(parts[2])
    backup_id = int(parts[3])

    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer(texts.ERROR_NO_ACCESS, show_alert=True)
        return

    from services.backup import BackupService
    from repositories.backup import BackupRepository
    backup_svc = BackupService(session)
    backup_repo = BackupRepository(session)
    backup = await backup_repo.get_by_id(backup_id)
    if backup is None or backup.project_id != project_id:
        await callback.answer("Снимок не найден", show_alert=True)
        return

    success, msg = await backup_svc.restore_backup(backup_id)

    if success:
        await callback.answer(f"✅ {msg}", show_alert=True)
    else:
        await callback.answer(f"❌ {msg}", show_alert=True)
