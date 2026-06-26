from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.utils.emojis import Emoji
from bot import texts

router = Router()


async def _check_file_access(callback: CallbackQuery, project_service, db_user, project_id: int, session=None):
    """Check if user has access to project files (owner or coowner)."""
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return None
    
    # Owner always has access
    if project.user_id == db_user.id:
        return project
    
    # Check coowner access if session provided
    if session is not None:
        from bot.utils.access import check_project_access
        has_access = await check_project_access(project, db_user, session)
        if has_access:
            return project
    
    await callback.answer(texts.ERROR_NO_ACCESS, show_alert=True)
    return None


@router.callback_query(F.data.startswith("project_files_"))
async def files_menu(callback: CallbackQuery, project_service, db_user, session):
    project_id = int(callback.data.split("_")[-1])
    project = await _check_file_access(callback, project_service, db_user, project_id, session)
    if project is None:
        return

    from bot.keyboards.user import get_file_manager_keyboard
    files = await project_service.list_files(project_id, "/app")

    # Используем новый стиль текста
    text = texts.bot_files_text(project.name, "/app")

    await callback.message.edit_text(
        text,
        reply_markup=get_file_manager_keyboard(project_id, files, "/app"),
        parse_mode="HTML"
    )
    await callback.answer()


def _parse_file_callback(data: str, prefix: str) -> tuple[int, str]:
    remaining = data.replace(prefix + "_", "", 1)
    parts = remaining.split("_", 1)
    project_id = int(parts[0])
    file_path = parts[1] if len(parts) > 1 else "main.py"
    return project_id, file_path


@router.callback_query(F.data.startswith("file_view_"))
async def file_view(callback: CallbackQuery, project_service, db_user, session):
    project_id, file_path = _parse_file_callback(callback.data, "file_view")
    project = await _check_file_access(callback, project_service, db_user, project_id, session)
    if project is None:
        return

    from bot.keyboards.user import get_file_action_keyboard
    await callback.message.edit_text(
        f"{Emoji.FILE} <b>{file_path}</b>",
        reply_markup=get_file_action_keyboard(project_id, file_path),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("file_nav_"))
async def file_nav(callback: CallbackQuery, project_service, db_user, session):
    project_id, path = _parse_file_callback(callback.data, "file_nav")
    project = await _check_file_access(callback, project_service, db_user, project_id, session)
    if project is None:
        return

    from bot.keyboards.user import get_file_manager_keyboard
    files = await project_service.list_files(project_id, path)

    # Используем новый стиль текста
    text = texts.bot_files_text(project.name, path)

    await callback.message.edit_text(
        text,
        reply_markup=get_file_manager_keyboard(project_id, files, path),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("file_delete_"))
async def file_delete(callback: CallbackQuery, project_service, db_user, session):
    project_id, file_path = _parse_file_callback(callback.data, "file_delete")
    project = await _check_file_access(callback, project_service, db_user, project_id, session)
    if project is None:
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Да, удалить",
            callback_data=f"file_delete_confirm_{project_id}_{file_path}",
        ),
        InlineKeyboardButton(
            text="❌ Нет",
            callback_data=f"project_files_{project_id}",
        ),
    )

    # Используем новый стиль текста
    text = texts.bot_file_delete_confirm(file_path)

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("file_delete_confirm_"))
async def file_delete_confirm(callback: CallbackQuery, project_service, db_user, session):
    project_id, file_path = _parse_file_callback(callback.data, "file_delete_confirm")
    project = await _check_file_access(callback, project_service, db_user, project_id, session)
    if project is None:
        return

    success = await project_service.delete_file(project_id, file_path)
    if success:
        await callback.answer(texts.BOT_FILE_DELETED_TEXT, show_alert=True)
        parent = "/".join(file_path.strip("/").split("/")[:-1]) or "/app"
        files = await project_service.list_files(project_id, parent)
        from bot.keyboards.user import get_file_manager_keyboard
        
        # Используем новый стиль текста
        text = texts.bot_files_text(project.name, parent)
        
        await callback.message.edit_text(
            text,
            reply_markup=get_file_manager_keyboard(project_id, files, parent),
            parse_mode="HTML"
        )
    else:
        await callback.answer(texts.BOT_FILE_DELETE_ERROR_TEXT, show_alert=True)


@router.callback_query(F.data.startswith("file_download_"))
async def file_download(callback: CallbackQuery, project_service, db_user, session):
    project_id, file_path = _parse_file_callback(callback.data, "file_download")
    project = await _check_file_access(callback, project_service, db_user, project_id, session)
    if project is None:
        return

    content = await project_service.read_file(project_id, file_path)
    if not content:
        await callback.answer(texts.BOT_FILE_NOT_FOUND_TEXT, show_alert=True)
        return

    from aiogram.types import BufferedInputFile
    import os
    file_bytes = content.encode("utf-8")
    filename = os.path.basename(file_path)
    file = BufferedInputFile(file_bytes, filename=filename)

    await callback.message.answer_document(
        file,
        caption=f"📄 <code>{file_path}</code>",
        parse_mode="HTML"
    )
    await callback.answer("✅ Файл загружен")
