from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.common import get_back_keyboard
from bot.utils.emojis import Emoji

router = Router()


class ProjectSettingsStates(StatesGroup):
    waiting_python = State()
    waiting_entry = State()


@router.callback_query(F.data.startswith("project_settings_"))
async def project_settings(callback: CallbackQuery, project_service, db_user, state: FSMContext):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer("Проект не найден", show_alert=True)
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=f"🐍 Python: {project.python_version}",
            callback_data=f"ps_python_{project_id}",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=f"📄 Entry: {project.entry_point}",
            callback_data=f"ps_entry_{project_id}",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data=f"project_view_{project_id}"),
    )

    await callback.message.edit_text(
        f"{Emoji.SETTINGS} <b>Настройки: {project.name}</b>\n\n"
        f"Python: {project.python_version}\n"
        f"Entry: <code>{project.entry_point}</code>\n"
        f"Тип: {project.entry_type}",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ps_python_"))
async def ps_python_select(callback: CallbackQuery, state: FSMContext):
    project_id = int(callback.data.split("_")[-1])
    await state.update_data(ps_project_id=project_id)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    for ver in ("3.10", "3.11", "3.12"):
        builder.row(
            InlineKeyboardButton(
                text=f"Python {ver}",
                callback_data=f"ps_python_set_{project_id}_{ver}",
            )
        )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data=f"project_settings_{project_id}"),
    )

    await callback.message.edit_text(
        f"{Emoji.SETTINGS} Выберите версию Python:",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ps_python_set_"))
async def ps_python_set(callback: CallbackQuery, project_service, db_user):
    parts = callback.data.split("_")
    project_id = int(parts[3])
    version = parts[4]

    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer("Нет доступа", show_alert=True)
        return

    from repositories.project import ProjectRepository
    from db.engine import async_session_factory
    async with async_session_factory() as session:
        project_repo = ProjectRepository(session)
        await project_repo.update(project_id, python_version=version)

    await callback.answer(f"✅ Python изменён на {version}", show_alert=True)
    await callback.message.edit_text(
        f"{Emoji.CHECK} Python изменён на <b>{version}</b>",
        reply_markup=get_back_keyboard(f"project_settings_{project_id}"),
    )


@router.callback_query(F.data.startswith("ps_entry_"))
async def ps_entry_edit(callback: CallbackQuery, state: FSMContext):
    project_id = int(callback.data.split("_")[-1])
    await state.update_data(ps_project_id=project_id)

    await callback.message.edit_text(
        f"{Emoji.PENCIL} Введите новую точку входа (например: main.py или mypackage.module):",
        reply_markup=get_back_keyboard(f"project_settings_{project_id}"),
    )
    await state.set_state(ProjectSettingsStates.waiting_entry)


@router.callback_query(F.data.startswith("project_settings"), ~F.data.startswith("project_settings_"))
async def project_settings_no_id(callback: CallbackQuery):
    await callback.answer("Используйте настройки из карточки проекта", show_alert=True)


@router.message(F.text, ProjectSettingsStates.waiting_entry)
async def ps_entry_received(message: Message, state: FSMContext, project_service, db_user):
    data = await state.get_data()
    project_id = data.get("ps_project_id")
    entry = message.text.strip()

    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await message.answer("❌ Проект не найден")
        await state.clear()
        return

    from repositories.project import ProjectRepository
    from db.engine import async_session_factory
    async with async_session_factory() as session:
        project_repo = ProjectRepository(session)
        await project_repo.update(project_id, entry_point=entry)

    await state.clear()
    await message.answer(
        f"{Emoji.CHECK} Точка входа изменена на <code>{entry}</code>",
        reply_markup=get_back_keyboard(f"project_settings_{project_id}"),
    )
