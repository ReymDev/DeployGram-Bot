from __future__ import annotations

import re

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.user import (
    get_source_keyboard,
    get_python_version_keyboard,
    get_entry_mode_keyboard,
    get_confirm_entry_keyboard,
    get_server_select_keyboard,
)
from bot.keyboards.common import get_back_keyboard
from bot.utils.emojis import Emoji
from bot.utils.media import edit_photo_or_text
from services.github import GitHubService

router = Router()


class CreateStates(StatesGroup):
    waiting_source = State()
    waiting_github_url = State()
    waiting_zip = State()
    waiting_python = State()
    waiting_entry = State()
    waiting_entry_module = State()
    waiting_server = State()
    waiting_name = State()
    confirming = State()


STEP_TEXT = "(1/4) Откуда загружаем?"
STEP_PYTHON = "(2/4) Версия Python"
STEP_UPLOAD = "(3/4) Загрузка файлов"
STEP_ENTRY = "(4/4) Выбор точки входа"


@router.callback_query(F.data == "add_bot")
async def add_bot_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateStates.waiting_source)

    text = (
        f"📥 <b>{STEP_TEXT}</b>\n\n"
        f"Ты можешь загрузить свой код или попробовать пресеты - "
        f"готовых ботов от других пользователей."
    )

    await edit_photo_or_text(
        callback.message,
        text,
        "upload_source",
        reply_markup=get_source_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "create_source_zip", CreateStates.waiting_source)
async def source_zip(callback: CallbackQuery, state: FSMContext):
    await state.update_data(source_type="zip")

    text = (
        f"📥 <b>{STEP_UPLOAD}</b>\n\n"
        f"Отправь .zip архив с файлами, положи requirements.txt в корень, "
        f"если хочешь, чтобы я установил зависимости сразу. "
        f"Либо сможешь сделать это позже в панели."
    )

    await edit_photo_or_text(
        callback.message,
        text,
        "file_upload",
        reply_markup=get_back_keyboard("create_back"),
    )
    await state.set_state(CreateStates.waiting_zip)
    await callback.answer()


@router.message(F.document, CreateStates.waiting_zip)
async def zip_received(message: Message, state: FSMContext):
    if not message.document or not message.document.file_name.endswith(".zip"):
        await message.answer("❌ Отправьте ZIP архив (.zip файл).")
        return

    await state.update_data(zip_file_id=message.document.file_id)

    text = (
        f"🐍 <b>{STEP_PYTHON}</b>\n"
        f"<i>Для Legacy-проектов с aiogram 2.x подойдет 3.10</i>\n\n"
        f"На какой версии будет запущен твой код?"
    )

    await message.answer(
        text,
        reply_markup=get_python_version_keyboard(),
    )
    await state.set_state(CreateStates.waiting_python)


@router.callback_query(F.data == "create_source_github", CreateStates.waiting_source)
async def source_github(callback: CallbackQuery, state: FSMContext):
    await state.update_data(source_type="github")

    text = (
        f"🔗 <b>{STEP_UPLOAD}</b>\n\n"
        f"Для первого деплоя с GitHub нажми \"Подключить GitHub\".\n"
        f"Выбери доступ ко всем репо для удобства или только к нужному.\n\n"
        f"Выбери репозиторий из списка ниже:"
    )

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="➕ Подключить Github",
            url=f"https://github.com/login/oauth/authorize?client_id=YOUR_CLIENT_ID&scope=repo",
            style="primary",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🔄 Обновить",
            callback_data="github_refresh",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="create_back"),
    )

    await edit_photo_or_text(
        callback.message,
        text,
        "github_repos",
        reply_markup=builder.as_markup(),
    )
    await state.set_state(CreateStates.waiting_github_url)
    await callback.answer()


@router.message(CreateStates.waiting_github_url)
async def github_url_received(message: Message, state: FSMContext):
    url = message.text.strip()
    parsed = GitHubService.parse_github_url(url)
    if parsed is None:
        await message.answer(
            "❌ Невалидный URL. Используйте формат:\n"
            "<code>https://github.com/user/repo</code>",
        )
        return

    owner, repo = parsed
    gh = GitHubService()
    info = await gh.get_repo_info(owner, repo)
    if info is None:
        await message.answer("❌ Репозиторий не найден или приватный.")
        return

    await state.update_data(source_url=url, source_owner=owner, source_repo=repo)

    text = (
        f"🐍 <b>{STEP_PYTHON}</b>\n"
        f"<i>Для Legacy-проектов с aiogram 2.x подойдет 3.10</i>\n\n"
        f"На какой версии будет запущен твой код?"
    )

    await message.answer(
        text,
        reply_markup=get_python_version_keyboard(),
    )
    await state.set_state(CreateStates.waiting_python)


@router.callback_query(F.data.startswith("create_python_"), CreateStates.waiting_python)
async def python_selected(callback: CallbackQuery, state: FSMContext):
    version = callback.data.replace("create_python_", "")
    await state.update_data(python_version=version)

    text = (
        f"📄 <b>{STEP_ENTRY}</b>\n\n"
        f"Выбери режим запуска:\n"
        f"• <b>Скрипт</b> - для <code>python file.py</code>\n"
        f"• <b>Модуль</b> - для <code>python -m package.module</code>"
    )

    await edit_photo_or_text(
        callback.message,
        text,
        "entry_point",
        reply_markup=get_entry_mode_keyboard(),
    )
    await state.set_state(CreateStates.waiting_entry)
    await callback.answer()


@router.callback_query(F.data == "create_entry_script", CreateStates.waiting_entry)
async def entry_script(callback: CallbackQuery, state: FSMContext, project_service):
    await state.update_data(entry_type="script")

    text = (
        f"📄 <b>{STEP_ENTRY}</b>\n"
        f"<i>Режим: Скриптовый запуск / python <code>file.py</code></i>\n"
        f"<i>Фильтр: *.py</i>\n\n"
        f"Выбери файл, который ты обычно запускаешь, чтобы твой бот начал работать:"
    )

    files = []
    data = await state.get_data()
    if data.get("zip_file_id"):
        try:
            file = await callback.bot.get_file(data["zip_file_id"])
            content = await callback.bot.download_file(file.file_path)
            import zipfile, io
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                files = [n for n in zf.namelist() if n.endswith(".py")]
        except Exception:
            pass

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()

    if files:
        for f in files[:15]:
            builder.row(
                InlineKeyboardButton(
                    text=f"📄 {f}",
                    callback_data=f"create_entry_file_{f}",
                )
            )
    else:
        builder.row(
            InlineKeyboardButton(
                text="📝 Ввести вручную",
                callback_data="create_entry_manual",
            )
        )

    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="create_back"),
    )

    await edit_photo_or_text(
        callback.message,
        text,
        "entry_point_script",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("create_entry_file_"), CreateStates.waiting_entry)
async def entry_file_selected(callback: CallbackQuery, state: FSMContext):
    entry = callback.data.replace("create_entry_file_", "")
    await state.update_data(entry_point=entry)

    text = (
        f"📄 <b>{STEP_ENTRY}</b>\n\n"
        f"📄 <code>{entry}</code>\n\n"
        f"Подтверди выбор точки входа, ты сможешь изменить ее позже."
    )

    await edit_photo_or_text(
        callback.message,
        text,
        "entry_confirm",
        reply_markup=get_confirm_entry_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "create_entry_manual", CreateStates.waiting_entry)
async def entry_manual(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📄 <b>Выбор точки входа</b>\n\n"
        "Отправь имя файла вручную.\n"
        "Пример: <code>main.py</code>",
        reply_markup=get_back_keyboard("create_back"),
    )
    await state.set_state(CreateStates.waiting_entry_module)
    await callback.answer()


@router.message(F.text, CreateStates.waiting_entry_module)
async def entry_manual_received(message: Message, state: FSMContext):
    entry = message.text.strip() or "main.py"
    await state.update_data(entry_point=entry)

    text = (
        f"📄 <b>{STEP_ENTRY}</b>\n\n"
        f"📄 <code>{entry}</code>\n\n"
        f"Подтверди выбор точки входа, ты сможешь изменить ее позже."
    )

    await message.answer(
        text,
        reply_markup=get_confirm_entry_keyboard(),
    )
    await state.set_state(CreateStates.waiting_entry)


@router.callback_query(F.data == "create_entry_module", CreateStates.waiting_entry)
async def entry_module(callback: CallbackQuery, state: FSMContext):
    await state.update_data(entry_type="module")

    await callback.message.edit_text(
        "📄 <b>Выбор точки входа</b>\n\n"
        "Режим: Модульный запуск / python -m\n\n"
        "Отправь имя модуля вручную.\n"
        "Примеры: <code>app.pkg.main</code>",
        reply_markup=get_back_keyboard("create_back"),
    )
    await state.set_state(CreateStates.waiting_entry_module)
    await callback.answer()


@router.callback_query(F.data == "create_confirm", CreateStates.waiting_entry)
async def create_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    from repositories.server import ServerRepository
    from db.engine import async_session_factory

    async with async_session_factory() as session:
        server_repo = ServerRepository(session)
        servers = await server_repo.get_online_servers()

    if not servers:
        await callback.answer("Нет доступных серверов", show_alert=True)
        return

    text = (
        f"🖥 <b>Выбор сервера</b>\n\n"
        f"Выбери сервер, на котором будет развернут твой бот:"
    )

    await edit_photo_or_text(
        callback.message,
        text,
        "server_selection",
        reply_markup=get_server_select_keyboard(servers),
    )
    await state.set_state(CreateStates.waiting_server)
    await callback.answer()


@router.callback_query(F.data.startswith("create_server_"), CreateStates.waiting_server)
async def server_selected(callback: CallbackQuery, state: FSMContext):
    server_id = int(callback.data.replace("create_server_", ""))
    await state.update_data(server_id=server_id)

    await callback.message.edit_text(
        "📝 Введи название для бота (1-50 символов, буквы, цифры, _ -):",
        reply_markup=get_back_keyboard("create_back"),
    )
    await state.set_state(CreateStates.waiting_name)
    await callback.answer()


@router.message(F.text, CreateStates.waiting_name)
async def name_received(message: Message, state: FSMContext):
    name = message.text.strip()
    if not re.match(r"^[a-zA-Z0-9_-]{1,50}$", name):
        await message.answer(
            "❌ Невалидное имя. Используйте буквы, цифры, _ и - (1-50 символов).",
        )
        return

    await state.update_data(name=name)

    data = await state.get_data()

    text = (
        f"{Emoji.CHECK} <b>Подтверждение</b>\n\n"
        f"📝 Название: <b>{name}</b>\n"
        f"🐍 Python: {data.get('python_version', '3.12')}\n"
        f"📄 Вход: <code>{data.get('entry_point', 'main.py')}</code>\n\n"
        f"Создать бота?"
    )

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Создать", callback_data="create_final", style="success"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="control_panel", style="danger"),
    )

    await message.answer(text, reply_markup=builder.as_markup())
    await state.set_state(CreateStates.confirming)


@router.callback_query(F.data == "create_final", CreateStates.confirming)
async def create_final(callback: CallbackQuery, state: FSMContext, db_user, project_service, user_service, session):
    data = await state.get_data()

    max_projects = await user_service.get_max_projects(db_user.tariff)
    current_count = await project_service.count_user_projects(db_user.id)
    if current_count >= max_projects:
        await callback.answer(
            f"Достигнут лимит ботов ({max_projects})",
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
        name=data.get("name", "my_bot"),
        source_type=source_type,
        source_url=data.get("source_url"),
        python_version=data.get("python_version", "3.12"),
        entry_point=data.get("entry_point", "main.py"),
        entry_type=data.get("entry_type", "script"),
        server_id=data.get("server_id"),
        files_zip=files_zip,
    )

    await state.clear()

    text = (
        f"🤖 <b>Твой бот готов к работе!</b>\n\n"
        f"Твой бот запущен!\n\n"
        f"Вернись в меню, чтобы управлять им. Тебе доступны: просмотр "
        f"логов. Запуск и остановка, файловый менеджер и установка библиотек."
    )

    from bot.keyboards.user import get_bot_control_keyboard
    await edit_photo_or_text(
        callback.message,
        text,
        "bot_ready",
        reply_markup=get_bot_control_keyboard(project.id, project.status),
    )
    await callback.answer()


@router.callback_query(F.data == "create_back")
async def create_back(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()

    if current_state == CreateStates.waiting_python:
        await state.set_state(CreateStates.waiting_source)
        await add_bot_start(callback, state)
    elif current_state in (CreateStates.waiting_entry, CreateStates.waiting_entry_module):
        data = await state.get_data()
        if data.get("zip_file_id"):
            await state.set_state(CreateStates.waiting_zip)
            text = (
                f"📥 <b>{STEP_UPLOAD}</b>\n\n"
                f"Отправь .zip архив с файлами."
            )
            await edit_photo_or_text(callback.message, text, "file_upload")
        else:
            await state.set_state(CreateStates.waiting_github_url)
            text = (
                f"🔗 <b>{STEP_UPLOAD}</b>\n\n"
                f"Выбери репозиторий:"
            )
            await edit_photo_or_text(callback.message, text, "github_repos")
    elif current_state == CreateStates.waiting_name:
        text = (
            f"📄 <b>{STEP_ENTRY}</b>\n\n"
            f"Выбери режим запуска:"
        )
        await state.set_state(CreateStates.waiting_entry)
        await edit_photo_or_text(callback.message, text, "entry_point")
    else:
        await state.clear()
        await control_panel_fallback(callback)

    await callback.answer()


async def control_panel_fallback(callback: CallbackQuery):
    await callback.message.edit_text(
        "📋 <b>Панель управления</b>",
        reply_markup=get_back_keyboard("control_panel"),
    )
