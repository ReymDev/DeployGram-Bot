from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.utils.emojis import Emoji
from bot.utils.media import edit_photo_or_text

router = Router()


@router.callback_query(F.data == "backups_list")
async def backups_list(callback: CallbackQuery, db_user, project_service):
    projects = await project_service.get_user_projects(db_user.id)

    if not projects:
        text = (
            f"☁ <b>Список бэкапов</b>\n\n"
            f"У тебя пока нет ботов."
        )
        await edit_photo_or_text(
            callback.message,
            text,
            "backups",
            reply_markup=get_back_keyboard("control_panel"),
        )
    else:
        text = (
            f"☁ <b>Список бэкапов</b>\n\n"
            f"🟢 - Бэкап создан\n"
            f"🟡 - Бэкап создается\n"
            f"🔴 - Возникла ошибка при создании бэкапа\n\n"
            f"Выбери существующий бэкап или создай новый:"
        )

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
        await callback.answer("Бот не найден", show_alert=True)
        return

    from services.backup import BackupService
    backup_svc = BackupService(session)
    backups = await backup_svc.get_backups(project_id)

    text = (
        f"☁ <b>Бэкапы: {project.name}</b>\n\n"
        f"Количество: {len(backups)}"
    )

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
        await callback.answer("Нет доступа", show_alert=True)
        return

    from services.backup import BackupService
    backup_svc = BackupService(session)
    await backup_svc.create_backup(project_id, size=0)

    await callback.answer("☁ Бэкап создан!", show_alert=True)


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
