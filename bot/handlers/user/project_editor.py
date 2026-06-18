from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.user import get_back_keyboard
from bot.utils.emojis import Emoji

router = Router()


@router.callback_query(F.data.startswith("project_editor_"))
async def editor_menu(callback: CallbackQuery, project_service, state: FSMContext):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer("Проект не найден", show_alert=True)
        return

    await state.update_data(editor_project_id=project_id)
    await callback.message.edit_text(
        f"{Emoji.PENCIL} <b>Редактор: {project.name}</b>\n\n"
        f"Отправьте файл для редактирования (.py, .txt, .env, .json, .yaml)\n"
        f"Или введите путь к файлу в проекте:",
        reply_markup=get_back_keyboard(f"project_view_{project_id}"),
    )
    await state.set_state("editor_waiting_file")
    await callback.answer()


@router.message(F.document, lambda m: m.document and m.document.file_name)
async def editor_file_uploaded(message: Message, state: FSMContext, project_service):
    from aiogram.fsm.state import State, StatesGroup
    current_state = await state.get_state()
    if current_state != "editor_waiting_file":
        return

    file_name = message.document.file_name
    allowed = (".py", ".txt", ".env", ".json", ".yaml", ".yml", ".toml", ".cfg")
    if not file_name.endswith(allowed):
        await message.answer(
            "❌ Поддерживаются только: .py, .txt, .env, .json, .yaml",
            reply_markup=get_back_keyboard("main_menu"),
        )
        return

    try:
        content = await message.bot.download(message.document)
        text = content.read().decode("utf-8", errors="replace")
    except Exception:
        await message.answer("❌ Ошибка чтения файла")
        return

    await state.update_data(editor_file_name=file_name, editor_content=text)
    await message.answer(
        f"🖋 <b>Редактирование: {file_name}</b>\n\n"
        f"<code>{text[:2000]}</code>\n\n"
        f"Отправьте новый текст файла:",
    )
    await state.set_state("editor_sending")


@router.message(F.text, state=None)
async def editor_text_input(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state != "editor_waiting_file":
        return

    file_path = message.text.strip()
    await state.update_data(editor_file_name=file_path)
    await message.answer(
        f"🖋 Файл: <code>{file_path}</code>\n\n"
        f"Отправьте новый текст:",
    )
    await state.set_state("editor_sending")


@router.message(F.text, state=None)
async def editor_save(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state != "editor_sending":
        return

    data = await state.get_data()
    file_name = data.get("editor_file_name", "file.txt")
    project_id = data.get("editor_project_id")

    await state.clear()
    await message.answer(
        f"{Emoji.CHECK} Файл <b>{file_name}</b> сохранён.\n\n"
        f"Для применения изменений обновите проект через GitHub или ZIP.",
        reply_markup=get_back_keyboard(f"project_view_{project_id}" if project_id else "main_menu"),
    )
