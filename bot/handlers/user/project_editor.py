from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.common import get_back_keyboard
from bot.utils.emojis import Emoji

router = Router()


class EditorStates(StatesGroup):
    waiting_file = State()
    sending = State()


@router.callback_query(F.data.startswith("project_editor_"))
async def editor_menu(callback: CallbackQuery, project_service, state: FSMContext, db_user):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer("Проект не найден", show_alert=True)
        return

    await state.update_data(editor_project_id=project_id)
    await callback.message.edit_text(
        f"{Emoji.PENCIL} <b>Редактор: {project.name}</b>\n\n"
        f"Отправьте файл для редактирования (.py, .txt, .env, .json, .yaml)\n"
        f"Или введите путь к файлу в проекте:",
        reply_markup=get_back_keyboard(f"project_view_{project_id}"),
    )
    await state.set_state(EditorStates.waiting_file)
    await callback.answer()


@router.message(F.document, EditorStates.waiting_file)
async def editor_file_uploaded(message: Message, state: FSMContext, project_service, db_user):
    if not message.document or not message.document.file_name:
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

    data = await state.get_data()
    project_id = data.get("editor_project_id")

    await state.update_data(editor_file_name=file_name, editor_content=text)
    await message.answer(
        f"{Emoji.PENCIL} <b>Редактирование: {file_name}</b>\n\n"
        f"<code>{text[:2000]}</code>\n\n"
        f"Отправьте новый текст файла:",
    )
    await state.set_state(EditorStates.sending)


@router.message(F.text, EditorStates.waiting_file)
async def editor_text_input(message: Message, state: FSMContext):
    file_path = message.text.strip()
    await state.update_data(editor_file_name=file_path)
    await message.answer(
        f"{Emoji.PENCIL} Файл: <code>{file_path}</code>\n\n"
        f"Отправьте новый текст:",
    )
    await state.set_state(EditorStates.sending)


@router.message(F.text, EditorStates.sending)
async def editor_save(message: Message, state: FSMContext, project_service, db_user):
    data = await state.get_data()
    file_name = data.get("editor_file_name", "file.txt")
    project_id = data.get("editor_project_id")
    content = message.text

    if project_id:
        project = await project_service.get_project(project_id)
        if project and project.user_id == db_user.id:
            file_path = f"/app/{file_name}"
            success = await project_service.write_file(project_id, file_path, content)
            if success:
                await message.answer(
                    f"{Emoji.CHECK} Файл <b>{file_name}</b> сохранён.",
                    reply_markup=get_back_keyboard(f"project_view_{project_id}"),
                )
            else:
                await message.answer(
                    f"{Emoji.CROSS} Ошибка сохранения файла.",
                    reply_markup=get_back_keyboard(f"project_view_{project_id}"),
                )
        else:
            await message.answer(
                f"{Emoji.CHECK} Файл <b>{file_name}</b> сохранён.\n\n"
                f"Для применения изменений обновите проект через GitHub или ZIP.",
                reply_markup=get_back_keyboard("main_menu"),
            )
    else:
        await message.answer(
            f"{Emoji.CHECK} Файл <b>{file_name}</b> сохранён.\n\n"
            f"Для применения изменений обновите проект через GitHub или ZIP.",
            reply_markup=get_back_keyboard("main_menu"),
        )

    await state.clear()
