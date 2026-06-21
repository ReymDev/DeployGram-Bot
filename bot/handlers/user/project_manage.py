from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.user import get_project_manage_keyboard, get_project_list_keyboard
from bot.utils.text import project_card
from bot.utils.emojis import Emoji

router = Router()


async def _check_owner(callback: CallbackQuery, project_service, db_user, project_id: int):
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer("Проект не найден", show_alert=True)
        return None
    if project.user_id != db_user.id:
        await callback.answer("Нет доступа к этому проекту", show_alert=True)
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
    text = project_card(
        name=project.name,
        status=monitoring.get("status", project.status),
        python_version=project.python_version,
        entry_point=project.entry_point,
        cpu=monitoring.get("cpu", 0),
        ram=monitoring.get("ram", 0),
        uptime=format_uptime(0),
        restarts=monitoring.get("restarts", 0),
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_project_manage_keyboard(project_id, project.status),
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
        await callback.message.edit_text(
            f"{Emoji.CHECK if success else Emoji.CROSS} {msg}",
            reply_markup=get_project_manage_keyboard(project_id, project.status),
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
        await callback.message.edit_text(
            f"{Emoji.CHECK if success else Emoji.CROSS} {msg}",
            reply_markup=get_project_manage_keyboard(project_id, project.status),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("project_restart_"))
async def project_restart(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.split("_")[-1])
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    success, msg = await project_service.restart_project(project_id)
    project = await project_service.get_project(project_id)
    if project:
        await callback.message.edit_text(
            f"{Emoji.CHECK if success else Emoji.CROSS} {msg}",
            reply_markup=get_project_manage_keyboard(project_id, project.status),
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
            f"{Emoji.TRASH} <b>Удаление проекта</b>\n\n"
            f"Вы уверены что хотите удалить <b>{project.name}</b>?\n"
            f"Это действие необратимо.",
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
        await callback.answer("Проект не найден", show_alert=True)
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
                f"{Emoji.CHECK} Проект удалён.",
                reply_markup=get_project_list_keyboard(projects),
            )
        except Exception:
            pass
    else:
        await callback.answer("Ошибка удаления", show_alert=True)
    await callback.answer()
