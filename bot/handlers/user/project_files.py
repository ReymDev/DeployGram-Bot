from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.utils.emojis import Emoji

router = Router()


@router.callback_query(F.data.startswith("project_files_"))
async def files_menu(callback: CallbackQuery, project_service):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer("Проект не найден", show_alert=True)
        return

    from bot.keyboards.user import get_file_manager_keyboard
    files = ["main.py", "requirements.txt"]

    await callback.message.edit_text(
        f"{Emoji.FILE} <b>Файлы: {project.name}</b>\n\n"
        f"📁 /",
        reply_markup=get_file_manager_keyboard(project_id, files, "/"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("file_view_"))
async def file_view(callback: CallbackQuery, project_service):
    parts = callback.data.split("_", 2)
    project_id = int(parts[2])
    file_path = parts[3] if len(parts) > 3 else "main.py"

    from bot.keyboards.user import get_file_action_keyboard
    await callback.message.edit_text(
        f"{Emoji.FILE} <b>{file_path}</b>",
        reply_markup=get_file_action_keyboard(project_id, file_path),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("file_nav_"))
async def file_nav(callback: CallbackQuery, project_service):
    parts = callback.data.split("_", 2)
    project_id = int(parts[2])
    path = parts[3] if len(parts) > 3 else "/"

    from bot.keyboards.user import get_file_manager_keyboard
    files = ["main.py", "requirements.txt", "src/"]

    await callback.message.edit_text(
        f"{Emoji.FILE} <b>📁 {path}</b>",
        reply_markup=get_file_manager_keyboard(project_id, files, path),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("file_delete_"))
async def file_delete(callback: CallbackQuery, project_service):
    parts = callback.data.split("_", 2)
    project_id = int(parts[2])
    file_path = parts[3] if len(parts) > 3 else ""

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Да, удалить",
            callback_data=f"file_delete_confirm_{project_id}_{file_path}",
            style="danger",
        ),
        InlineKeyboardButton(
            text="❌ Нет",
            callback_data=f"project_files_{project_id}",
        ),
    )

    await callback.message.edit_text(
        f"{Emoji.TRASH} Удалить <b>{file_path}</b>?",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()
