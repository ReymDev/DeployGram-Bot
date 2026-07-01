from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.user import get_project_manage_keyboard, get_project_list_keyboard
from bot import texts

router = Router()


async def _check_owner(callback: CallbackQuery, project_service, db_user, project_id: int):
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return None
    if project.user_id != db_user.id:
        await callback.answer(texts.ERROR_NO_ACCESS, show_alert=True)
        return None
    return project


@router.callback_query(F.data.startswith("project_view_"))
async def project_view(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.split("_")[-1])
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    monitoring = await project_service.get_monitoring(project_id)
    from bot.utils.formatters import format_uptime
    
    text = texts.project_card_text(
        name=project.name,
        status=monitoring.get("status", project.status),
        python_version=project.python_version,
        entry_point=project.entry_point,
        cpu=monitoring.get("cpu", 0),
        ram=monitoring.get("ram", 0),
        uptime=format_uptime(monitoring.get("uptime_seconds", 0)),
        restarts=monitoring.get("restarts", 0),
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_project_manage_keyboard(project_id, project.status),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("project_start_"))
async def project_start(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.split("_")[-1])
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    success, msg = await project_service.start_project(project_id)
    project = await project_service.get_project(project_id)
    
    if project:
        if success:
            text = texts.PROJECT_START_SUCCESS
        else:
            text = f"{texts.PROJECT_START_ERROR}\n\n<i>{msg}</i>"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_project_manage_keyboard(project_id, project.status),
            parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(F.data.startswith("project_stop_"))
async def project_stop(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.split("_")[-1])
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    success, msg = await project_service.stop_project(project_id)
    project = await project_service.get_project(project_id)
    
    if project:
        if success:
            text = texts.PROJECT_STOP_SUCCESS
        else:
            text = f"{texts.PROJECT_STOP_ERROR}\n\n<i>{msg}</i>"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_project_manage_keyboard(project_id, project.status),
            parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(F.data.startswith("project_delete_"))
async def project_delete(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.replace("project_delete_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Да, удалить",
            callback_data=f"project_del_confirm_{project_id}",
            style="danger",
        ),
        InlineKeyboardButton(
            text="❌ Нет",
            callback_data=f"project_view_{project_id}",
        ),
    )

    try:
        await callback.message.edit_text(
            texts.project_delete_confirm_text(project.name),
            reply_markup=builder.as_markup(),
        )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("project_del_confirm_"))
async def project_delete_confirm(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.replace("project_del_confirm_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return

    try:
        success = await project_service.delete_project(project_id)
    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)
        return

    if success:
        projects = await project_service.get_user_projects(db_user.id)
        try:
            await callback.message.edit_text(
                texts.PROJECT_DELETED_TEXT,
                reply_markup=get_project_list_keyboard(projects),
            )
        except Exception:
            pass
    else:
        await callback.answer(texts.PROJECT_DELETE_ERROR, show_alert=True)
    await callback.answer()
