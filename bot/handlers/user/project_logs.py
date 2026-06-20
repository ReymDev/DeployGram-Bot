from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

from bot.keyboards.user import get_logs_keyboard
from bot.utils.emojis import Emoji
from bot.utils.formatters import truncate_text

router = Router()


@router.callback_query(F.data.startswith("project_logs_"))
async def project_logs_menu(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer("Проект не найден", show_alert=True)
        return

    await callback.message.edit_text(
        f"{Emoji.FILE} <b>Логи: {project.name}</b>",
        reply_markup=get_logs_keyboard(project_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("logs_view_"))
async def logs_view(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer("Нет доступа", show_alert=True)
        return

    logs = await project_service.get_logs(project_id, tail=100)
    truncated = truncate_text(logs, 3500)

    await callback.message.edit_text(
        f"<b>📋 Последние логи:</b>\n\n<code>{truncated}</code>",
        reply_markup=get_logs_keyboard(project_id),
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("logs_download_"))
async def logs_download(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer("Нет доступа", show_alert=True)
        return

    logs = await project_service.get_logs(project_id, tail=1000)

    from aiogram.types import BufferedInputFile
    log_bytes = logs.encode("utf-8")
    file = BufferedInputFile(log_bytes, filename=f"{project.name}_logs.txt")

    await callback.message.answer_document(file, caption=f"📋 Логи проекта {project.name}")
    await callback.answer()


@router.callback_query(F.data.startswith("logs_clear_"))
async def logs_clear(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer("Нет доступа", show_alert=True)
        return

    success = await project_service.clear_logs(project_id)
    if success:
        await callback.answer("Логи очищены", show_alert=True)
    else:
        await callback.answer("Ошибка очистки логов", show_alert=True)
