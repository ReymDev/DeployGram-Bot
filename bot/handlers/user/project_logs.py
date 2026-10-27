from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

from bot.keyboards.user import get_logs_keyboard
from bot.utils.emojis import Emoji
from bot.utils.formatters import truncate_text
from bot.utils.media import edit_photo_or_text
from bot import texts

router = Router()


@router.callback_query(F.data.startswith("project_logs_"))
async def project_logs_menu(callback: CallbackQuery, project_service, db_user, session):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return
    
    # Check permission
    from bot.utils.access import check_permission
    has_perm, _ = await check_permission(project, db_user, session, "can_view_logs")
    if not has_perm:
        await callback.answer("⛔ У вас нет прав на просмотр логов", show_alert=True)
        return

    await edit_photo_or_text(
        callback.message,
        texts.project_logs_menu_text(project.name),
        "logs",
        reply_markup=get_logs_keyboard(project_id),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.callback_query(F.data.startswith("logs_view_"))
async def logs_view(callback: CallbackQuery, project_service, db_user, session):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return
    
    # Check permission
    from bot.utils.access import check_permission
    has_perm, _ = await check_permission(project, db_user, session, "can_view_logs")
    if not has_perm:
        await callback.answer("⛔ У вас нет прав на просмотр логов", show_alert=True)
        return

    logs = await project_service.get_logs(project_id, tail=100)
    truncated = truncate_text(logs, 3500)
    from html import escape
    escaped_logs = escape(truncated)

    await edit_photo_or_text(
        callback.message,
        texts.project_logs_view_text(escaped_logs),
        "logs",
        reply_markup=get_logs_keyboard(project_id),
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("logs_download_"))
async def logs_download(callback: CallbackQuery, project_service, db_user, session):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return
    
    # Check permission
    from bot.utils.access import check_permission
    has_perm, _ = await check_permission(project, db_user, session, "can_view_logs")
    if not has_perm:
        await callback.answer("⛔ У вас нет прав на просмотр логов", show_alert=True)
        return

    logs = await project_service.get_logs(project_id, tail=1000)

    from aiogram.types import BufferedInputFile
    log_bytes = logs.encode("utf-8")
    file = BufferedInputFile(log_bytes, filename=f"{project.name}_logs.txt")

    await callback.message.answer_document(
        file, 
        caption=texts.project_logs_file_caption(project.name),
        parse_mode=ParseMode.HTML
    )
    await callback.answer("✅ Файл готов")


@router.callback_query(F.data.startswith("logs_clear_"))
async def logs_clear(callback: CallbackQuery, project_service, db_user, session):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return
    
    # Only owner can clear logs
    if project.user_id != db_user.id:
        await callback.answer("⛔ Только владелец может очищать консоль", show_alert=True)
        return

    success = await project_service.clear_logs(project_id)
    if success:
        await callback.answer(texts.PROJECT_LOGS_CLEARED, show_alert=True)
    else:
        await callback.answer(texts.PROJECT_LOGS_CLEAR_ERROR, show_alert=True)
