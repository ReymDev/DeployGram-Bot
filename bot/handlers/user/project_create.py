from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.user import (
    get_create_project_step1_keyboard,
    get_python_version_keyboard,
    get_entry_type_keyboard,
    get_server_select_keyboard,
    get_confirm_start_keyboard,
)
from bot.keyboards.common import get_back_keyboard
from bot.states.project import ProjectCreateStates
from bot.utils.emojis import Emoji
from services.github import GitHubService

router = Router()


@router.callback_query(F.data == "create_project")
async def create_project_start(callback: CallbackQuery, user_service, db_user, state: FSMContext):
    max_projects = await user_service.get_max_projects(db_user.tariff)

    await callback.message.edit_text(
        f"{Emoji.FILE} <b>Создание проекта</b>\n\n"
        f"Выберите источник проекта:",
        reply_markup=get_create_project_step1_keyboard(),
    )
    await state.set_state(ProjectCreateStates.waiting_source)
    await callback.answer()


@router.callback_query(F.data.startswith("create_type_"), ProjectCreateStates.waiting_source)
async def create_type_selected(callback: CallbackQuery, state: FSMContext):
    source_type = callback.data.replace("create_type_", "")
    await state.update_data(source_type=source_type)

    if source_type == "github":
        await callback.message.edit_text(
            f"{Emoji.LINK} Введите URL GitHub репозитория:\n\n"
            f"Пример: <code>https://github.com/user/repo</code>",
            reply_markup=get_back_keyboard("create_project"),
        )
        await state.set_state(ProjectCreateStates.waiting_github_url)
    else:
        await callback.message.edit_text(
            f"{Emoji.FILE} Отправьте ZIP архив проекта.",
            reply_markup=get_back_keyboard("create_project"),
        )
        await state.set_state(ProjectCreateStates.waiting_zip)
    await callback.answer()


@router.message(ProjectCreateStates.waiting_github_url)
async def github_url_received(message: Message, state: FSMContext):
    url = message.text.strip()
    parsed = GitHubService.parse_github_url(url)
    if parsed is None:
        await message.answer(
            "❌ Невалидный URL. Используйте формат:\n"
            "<code>https://github.com/user/repo</code>",
            reply_markup=get_back_keyboard("create_project"),
        )
        return

    owner, repo = parsed
    gh = GitHubService()
    info = await gh.get_repo_info(owner, repo)
    if info is None:
        await message.answer(
            "❌ Репозиторий не найден или приватный.",
            reply_markup=get_back_keyboard("create_project"),
        )
        return

    await state.update_data(source_url=url, source_owner=owner, source_repo=repo)
    await message.answer(
        f"✅ Репозиторий: <b>{info.get('full_name', url)}</b>\n"
        f"📝 {info.get('description', 'Без описания')}\n\n"
        f"Выберите версию Python:",
        reply_markup=get_python_version_keyboard(),
    )
    await state.set_state(ProjectCreateStates.waiting_python)


@router.message(ProjectCreateStates.waiting_zip)
async def zip_received(message: Message, state: FSMContext):
    if not message.document or not message.document.file_name.endswith(".zip"):
        await message.answer(
            "❌ Отправьте ZIP архив (.zip файл).",
            reply_markup=get_back_keyboard("create_project"),
        )
        return

    await state.update_data(zip_file_id=message.document.file_id)
    await message.answer(
        "✅ Архив получен.\n\nВыберите версию Python:",
        reply_markup=get_python_version_keyboard(),
    )
    await state.set_state(ProjectCreateStates.waiting_python)


@router.callback_query(F.data.startswith("create_python_"), ProjectCreateStates.waiting_python)
async def python_selected(callback: CallbackQuery, state: FSMContext):
    version = callback.data.replace("create_python_", "")
    await state.update_data(python_version=version)

    await callback.message.edit_text(
        f"🐍 Python {version}\n\nВыберите тип точки входа:",
        reply_markup=get_entry_type_keyboard(),
    )
    await state.set_state(ProjectCreateStates.waiting_entry)
    await callback.answer()


@router.callback_query(F.data == "create_entry_script", ProjectCreateStates.waiting_entry)
async def entry_script(callback: CallbackQuery, state: FSMContext):
    await state.update_data(entry_type="script")
    data = await state.get_data()
    if data.get("source_type") == "github":
        await callback.message.edit_text(
            "📄 Точка входа: <b>скрипт</b>\n\n"
            "Введите имя файла (по умолчанию main.py):",
            reply_markup=get_back_keyboard("create_project"),
        )
    else:
        await callback.message.edit_text(
            "📄 Точка входа: <b>скрипт</b>\n\n"
            "Введите имя файла (по умолчанию main.py):",
            reply_markup=get_back_keyboard("create_project"),
        )
    await state.set_state(ProjectCreateStates.waiting_entry_module)
    await callback.answer()


@router.callback_query(F.data == "create_entry_module", ProjectCreateStates.waiting_entry)
async def entry_module(callback: CallbackQuery, state: FSMContext):
    await state.update_data(entry_type="module")
    await callback.message.edit_text(
        "📦 Точка входа: <b>модуль</b>\n\n"
        "Введите путь модуля (например: mypackage.mymodule):",
        reply_markup=get_back_keyboard("create_project"),
    )
    await state.set_state(ProjectCreateStates.waiting_entry_module)
    await callback.answer()


@router.message(ProjectCreateStates.waiting_entry_module)
async def entry_received(message: Message, state: FSMContext):
    entry = message.text.strip() or "main.py"
    await state.update_data(entry_point=entry)

    data = await state.get_data()
    project_name = data.get("name", "my_project")

    await message.answer(
        f"📝 Точка входа: <code>{entry}</code>\n\n"
        f"Название проекта (1-50 символов, буквы, цифры, _ -):",
        reply_markup=get_back_keyboard("create_project"),
    )
    await state.set_state(ProjectCreateStates.waiting_name)


@router.message(ProjectCreateStates.waiting_name)
async def name_received(message: Message, state: FSMContext):
    import re
    name = message.text.strip()
    if not re.match(r"^[a-zA-Z0-9_-]{1,50}$", name):
        await message.answer(
            "❌ Невалидное имя. Используйте буквы, цифры, _ и - (1-50 символов).",
            reply_markup=get_back_keyboard("create_project"),
        )
        return

    await state.update_data(name=name)

    from repositories.server import ServerRepository
    from db.engine import async_session_factory

    async with async_session_factory() as session:
        server_repo = ServerRepository(session)
        servers = await server_repo.get_online_servers()

    if not servers:
        await message.answer(
            f"🌍 Нет доступных серверов.\n\n"
            f"Проект будет создан без конкретного сервера.",
            reply_markup=get_back_keyboard("create_project"),
        )
        await state.set_state(ProjectCreateStates.confirming)
        await show_confirmation(message, state)
    else:
        await message.answer(
            f"🌍 Выберите сервер:",
            reply_markup=get_server_select_keyboard(servers),
        )
        await state.set_state(ProjectCreateStates.waiting_server)


@router.callback_query(F.data.startswith("create_server_"), ProjectCreateStates.waiting_server)
async def server_selected(callback: CallbackQuery, state: FSMContext):
    server_id = int(callback.data.replace("create_server_", ""))
    await state.update_data(server_id=server_id)
    await show_confirmation(callback.message, state, edit=True)
    await callback.answer()


async def show_confirmation(message, state: FSMContext, edit: bool = False):
    data = await state.get_data()
    source = data.get("source_type", "zip")
    source_text = "GitHub" if source == "github" else "ZIP архив"
    version = data.get("python_version", "3.12")
    entry = data.get("entry_point", "main.py")
    entry_type = data.get("entry_type", "script")
    name = data.get("name", "my_project")

    text = (
        f"{Emoji.CHECK} <b>Подтверждение создания проекта</b>\n\n"
        f"📦 Название: <b>{name}</b>\n"
        f"🔗 Источник: {source_text}\n"
        f"🐍 Python: {version}\n"
        f"📄 Вход: <code>{entry}</code> ({entry_type})\n\n"
        f"Создать проект?"
    )

    keyboard = get_confirm_start_keyboard(0)
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Создать", callback_data="create_confirm", style="success"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="main_menu", style="danger"),
    )
    kb = builder.as_markup()

    if edit:
        await message.edit_text(text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)

    await state.set_state(ProjectCreateStates.confirming)


@router.callback_query(F.data == "create_confirm", ProjectCreateStates.confirming)
async def create_confirmed(callback: CallbackQuery, state: FSMContext, db_user, project_service, user_service, session):
    data = await state.get_data()

    max_projects = await user_service.get_max_projects(db_user.tariff)
    current_count = await project_service.count_user_projects(db_user.id)
    if current_count >= max_projects:
        await callback.answer(
            f"Достигнут лимит проектов ({max_projects})",
            show_alert=True,
        )
        return

    files_zip = None
    source_type = data.get("source_type", "zip")
    if source_type == "zip":
        zip_file_id = data.get("zip_file_id")
        if zip_file_id:
            try:
                file = await callback.bot.get_file(zip_file_id)
                files_zip = await callback.bot.download_file(file.file_path)
            except Exception as e:
                await callback.answer(f"Ошибка загрузки файла: {e}", show_alert=True)
                return

    project = await project_service.create_project(
        user_id=db_user.id,
        name=data.get("name", "my_project"),
        source_type=source_type,
        source_url=data.get("source_url"),
        python_version=data.get("python_version", "3.12"),
        entry_point=data.get("entry_point", "main.py"),
        entry_type=data.get("entry_type", "script"),
        server_id=data.get("server_id"),
        files_zip=files_zip,
    )

    await state.clear()

    from bot.keyboards.user import get_project_manage_keyboard
    await callback.message.edit_text(
        f"{Emoji.PARTY} Проект <b>{project.name}</b> создан!\n\n"
        f"Запустите проект из меню управления.",
        reply_markup=get_project_manage_keyboard(project.id, project.status),
    )
    await callback.answer()
