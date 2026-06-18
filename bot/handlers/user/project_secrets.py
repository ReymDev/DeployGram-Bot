from __future__ import annotations

import json

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.common import get_back_keyboard
from bot.utils.emojis import Emoji

router = Router()


@router.callback_query(F.data.startswith("project_secrets_"))
async def secrets_menu(callback: CallbackQuery, project_service):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer("Проект не найден", show_alert=True)
        return

    from repositories.project import ProjectVersionRepository
    from db.engine import async_session_factory

    async with async_session_factory() as session:
        version_repo = ProjectVersionRepository(session)
        version = await version_repo.get_latest(project_id)

    secrets = {}
    if version and version.secrets:
        try:
            secrets = json.loads(version.secrets)
        except (json.JSONDecodeError, TypeError):
            pass

    from bot.keyboards.user import get_secrets_keyboard
    await callback.message.edit_text(
        f"{Emoji.LOCK} <b>Секреты: {project.name}</b>\n\n"
        f"Переменные окружения (ENV):",
        reply_markup=get_secrets_keyboard(project_id, secrets),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("secret_add_"))
async def secret_add_start(callback: CallbackQuery, state: FSMContext):
    project_id = int(callback.data.split("_")[-1])
    await state.update_data(secret_project_id=project_id)
    await callback.message.edit_text(
        f"{Emoji.PENCIL} Введите имя переменной (например BOT_TOKEN):",
        reply_markup=get_back_keyboard(f"project_secrets_{project_id}"),
    )
    await state.set_state("secret_waiting_key")
    await callback.answer()


@router.message(F.text, state="secret_waiting_key")
async def secret_key_received(message: Message, state: FSMContext):
    key = message.text.strip()
    data = await state.get_data()
    project_id = data.get("secret_project_id")

    await state.update_data(secret_key=key)
    await message.answer(
        f"🔑 {key} = ?\n\nВведите значение:",
        reply_markup=get_back_keyboard(f"project_secrets_{project_id}"),
    )
    await state.set_state("secret_waiting_value")


@router.message(F.text, state="secret_waiting_value")
async def secret_value_received(message: Message, state: FSMContext):
    value = message.text.strip()
    data = await state.get_data()
    project_id = data.get("secret_project_id")
    key = data.get("secret_key")

    from services.project import ProjectVersionRepository, ProjectService
    from db.engine import async_session_factory

    async with async_session_factory() as session:
        version_repo = ProjectVersionRepository(session)
        version = await version_repo.get_latest(project_id)

        secrets = {}
        if version and version.secrets:
            try:
                secrets = json.loads(version.secrets)
            except (json.JSONDecodeError, TypeError):
                pass

        secrets[key] = value
        project_svc = ProjectService(session)
        project = await project_svc.get_project(project_id)
        await project_svc.save_version(
            project_id,
            secrets=json.dumps(secrets),
            entry_point=project.entry_point if project else "main.py",
            python_version=project.python_version if project else "3.12",
        )

    await state.clear()
    await message.answer(
        f"{Emoji.CHECK} Секрет <b>{key}</b> сохранён.",
        reply_markup=get_back_keyboard(f"project_secrets_{project_id}"),
    )
