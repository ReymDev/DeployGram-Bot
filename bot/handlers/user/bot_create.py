from __future__ import annotations

import io
import os
import re
import tempfile
import zipfile
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.user import (
    get_source_keyboard,
    get_python_version_keyboard,
)
from bot.keyboards.common import get_back_keyboard
from bot.utils.emojis import Emoji
from bot.utils.media import edit_photo_or_text
from services.github import GitHubService
from bot import texts

router = Router()


class CreateStates(StatesGroup):
    waiting_source = State()
    waiting_github_url = State()
    waiting_zip = State()
    waiting_python = State()
    waiting_entry = State()
    waiting_name = State()
    waiting_server = State()
    confirming = State()


STEP_TEXT = "(1/4) Откуда загружаем?"
STEP_PYTHON = "(2/4) Версия Python"
STEP_ENTRY = "(2/4) Точка входа"
STEP_NAME = "(3/4) Название"
STEP_SERVER = "(4/4) Сервер"


def _extract_zip_to_temp(files_zip: bytes) -> str:
    tmpdir = tempfile.mkdtemp(prefix="dg_")
    with zipfile.ZipFile(io.BytesIO(files_zip)) as zf:
        zf.extractall(tmpdir)
    return tmpdir


def _list_dir(path: str) -> list[dict]:
    items = []
    if not os.path.exists(path):
        return items
    for name in sorted(os.listdir(path)):
        full = os.path.join(path, name)
        items.append({
            "name": name,
            "is_dir": os.path.isdir(full),
            "path": full,
        })
    return items


def _get_entry_keyboard(tmpdir: str, current_path: str, project_id: int = 0) -> "InlineKeyboardMarkup":
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton

    builder = InlineKeyboardBuilder()
    full_current = os.path.join(tmpdir, current_path.lstrip("/"))

    if current_path != "/":
        parent = "/".join(current_path.strip("/").split("/")[:-1]) or "/"
        builder.row(
            InlineKeyboardButton(text="⬆ ..", callback_data=f"create_nav_{parent}"),
        )

    items = _list_dir(full_current)
    dirs = [i for i in items if i["is_dir"]]
    files = [i for i in items if not i["is_dir"]]

    for d in dirs:
        rel = os.path.relpath(d["path"], tmpdir).replace("\\", "/")
        builder.row(
            InlineKeyboardButton(text=f"📁 {d['name']}", callback_data=f"create_nav_{rel}"),
        )

    py_files = [f for f in files if f["name"].endswith(".py")]
    for f in py_files[:15]:
        rel = os.path.relpath(f["path"], tmpdir).replace("\\", "/")
        builder.row(
            InlineKeyboardButton(text=f"📄 {f['name']}", callback_data=f"create_select_{rel}"),
        )

    if not py_files and not dirs:
        builder.row(
            InlineKeyboardButton(text="📝 Ввести вручную", callback_data="create_manual_entry"),
        )

    builder.row(
        InlineKeyboardButton(text="Назад", style="danger", callback_data="create_back"),
    )
    return builder.as_markup()


@router.callback_query(F.data == "add_bot")
async def add_bot_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateStates.waiting_source)

    text = texts.ADD_BOT_SOURCE_TEXT

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

    text = texts.ADD_BOT_ZIP_TEXT

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
        await message.answer(texts.BOT_CREATE_INVALID_ZIP)
        return

    file = await message.bot.get_file(message.document.file_id)
    content = await message.bot.download_file(file.file_path)
    files_zip = content.read()

    tmpdir = _extract_zip_to_temp(files_zip)

    await state.update_data(
        zip_file_id=message.document.file_id,
        tmpdir=tmpdir,
    )

    text = texts.ADD_BOT_PYTHON_TEXT

    await message.answer(text, reply_markup=get_python_version_keyboard())
    await state.set_state(CreateStates.waiting_python)


@router.callback_query(F.data == "create_source_github", CreateStates.waiting_source)
async def source_github(callback: CallbackQuery, state: FSMContext):
    await state.update_data(source_type="github")

    text = texts.ADD_BOT_GITHUB_TEXT

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="➕ Подключить Github",
            url="https://github.com/login/oauth/authorize?client_id=YOUR_CLIENT_ID&scope=repo",
            style="primary",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Обновить", callback_data="github_refresh"),
    )
    builder.row(
        InlineKeyboardButton(text="Назад", style="danger", callback_data="create_back"),
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
        await message.answer(texts.BOT_CREATE_INVALID_URL)
        return

    owner, repo = parsed
    gh = GitHubService()
    info = await gh.get_repo_info(owner, repo)
    if info is None:
        await message.answer(texts.BOT_CREATE_REPO_NOT_FOUND)
        return

    await state.update_data(source_url=url, source_owner=owner, source_repo=repo)

    text = texts.ADD_BOT_PYTHON_TEXT

    await message.answer(text, reply_markup=get_python_version_keyboard())
    await state.set_state(CreateStates.waiting_python)


@router.callback_query(F.data.startswith("create_python_"), CreateStates.waiting_python)
async def python_selected(callback: CallbackQuery, state: FSMContext):
    version = callback.data.replace("create_python_", "")
    await state.update_data(python_version=version)

    data = await state.get_data()
    tmpdir = data.get("tmpdir")

    if tmpdir and os.path.exists(tmpdir):
        text = texts.add_bot_entry_script_text()
        kb = _get_entry_keyboard(tmpdir, "/")
        await edit_photo_or_text(callback.message, text, "entry_point_script", reply_markup=kb)
        await state.set_state(CreateStates.waiting_entry)
    else:
        text = texts.ADD_BOT_ENTRY_TEXT
        from bot.keyboards.user import get_entry_mode_keyboard
        await edit_photo_or_text(callback.message, text, "entry_point", reply_markup=get_entry_mode_keyboard())
        await state.set_state(CreateStates.waiting_entry)

    await callback.answer()


@router.callback_query(F.data.startswith("create_nav_"), CreateStates.waiting_entry)
async def create_nav(callback: CallbackQuery, state: FSMContext):
    path = callback.data.replace("create_nav_", "")
    data = await state.get_data()
    tmpdir = data.get("tmpdir")

    if not tmpdir or not os.path.exists(tmpdir):
        await callback.answer(texts.BOT_CREATE_ARCHIVE_NOT_FOUND, show_alert=True)
        return

    text = texts.add_bot_entry_script_text()
    kb = _get_entry_keyboard(tmpdir, f"/{path.lstrip('/')}")
    try:
        await callback.message.edit_text(text, reply_markup=kb)
    except Exception:
        await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("create_select_"), CreateStates.waiting_entry)
async def create_select_file(callback: CallbackQuery, state: FSMContext):
    entry = callback.data.replace("create_select_", "")
    await state.update_data(entry_point=entry, entry_type="script")

    text = texts.bot_create_entry_confirm_text(entry)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬆ ..", callback_data="create_nav_/"),
    )
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="create_confirmed_entry", style="success"),
    )

    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "create_manual_entry", CreateStates.waiting_entry)
async def create_manual_entry(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        texts.BOT_CREATE_ENTRY_MANUAL_TEXT,
        reply_markup=get_back_keyboard("create_back"),
    )
    await callback.answer()


@router.message(F.text, CreateStates.waiting_entry)
async def create_entry_manual(message: Message, state: FSMContext):
    entry = message.text.strip() or "main.py"
    await state.update_data(entry_point=entry, entry_type="script")

    text = texts.bot_create_entry_confirm_text(entry)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="create_confirmed_entry", style="success"),
    )

    await message.answer(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "create_entry_script", CreateStates.waiting_entry)
async def entry_script(callback: CallbackQuery, state: FSMContext):
    await state.update_data(entry_type="script")
    await state.set_state(CreateStates.waiting_entry)

    data = await state.get_data()
    tmpdir = data.get("tmpdir")

    if tmpdir and os.path.exists(tmpdir):
        text = texts.add_bot_entry_script_text()
        kb = _get_entry_keyboard(tmpdir, "/")
        await callback.message.edit_text(text, reply_markup=kb)
    else:
        await callback.message.edit_text(
            texts.BOT_CREATE_ENTRY_MANUAL_TEXT,
            reply_markup=get_back_keyboard("create_back"),
        )
    await callback.answer()


@router.callback_query(F.data == "create_entry_module", CreateStates.waiting_entry)
async def entry_module(callback: CallbackQuery, state: FSMContext):
    await state.update_data(entry_type="module")

    await callback.message.edit_text(
        texts.BOT_CREATE_ENTRY_MODULE_TEXT,
        reply_markup=get_back_keyboard("create_back"),
    )
    await callback.answer()


@router.callback_query(F.data == "create_confirmed_entry", CreateStates.waiting_entry)
async def create_confirmed_entry(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    entry = data.get("entry_point", "main.py")

    from repositories.server import ServerRepository
    from db.engine import async_session_factory

    async with async_session_factory() as session:
        server_repo = ServerRepository(session)
        servers = await server_repo.get_online_servers()

    if not servers:
        await callback.answer(texts.BOT_CREATE_NO_SERVERS, show_alert=True)
        return

    text = (
        f"🖥 <b>{STEP_SERVER}</b>\n\n"
        f"Выбери сервер, на котором будет развернут твой бот:"
    )

    from bot.keyboards.user import get_server_select_keyboard
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
        texts.BOT_CREATE_NAME_TEXT,
        reply_markup=get_back_keyboard("create_back"),
    )
    await state.set_state(CreateStates.waiting_name)
    await callback.answer()


@router.message(F.text, CreateStates.waiting_name)
async def name_received(message: Message, state: FSMContext):
    name = message.text.strip()
    if not re.match(r"^[a-zA-Z0-9_-]{1,50}$", name):
        await message.answer(texts.BOT_CREATE_INVALID_NAME)
        return

    await state.update_data(name=name)
    data = await state.get_data()

    text = texts.bot_create_confirm_text(name, data.get('python_version', '3.12'), data.get('entry_point', 'main.py'))

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
        await callback.answer(texts.BOT_CREATE_LIMIT_REACHED(max_projects), show_alert=True)
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
                await callback.answer(texts.BOT_CREATE_DOWNLOAD_ERROR(e), show_alert=True)
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

    tmpdir = data.get("tmpdir")
    if tmpdir and os.path.exists(tmpdir):
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)

    await state.clear()

    text = texts.BOT_CREATE_SUCCESS_TEXT

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
        data = await state.get_data()
        if data.get("source_type") == "zip":
            await state.set_state(CreateStates.waiting_zip)
            await edit_photo_or_text(
                callback.message,
                "📥 Отправь .zip архив с файлами.",
                "file_upload",
            )
        else:
            await state.set_state(CreateStates.waiting_github_url)
            await edit_photo_or_text(
                callback.message,
                "🔗 Введи URL репозитория:",
                "github_repos",
            )
    elif current_state == CreateStates.waiting_entry:
        await state.set_state(CreateStates.waiting_python)
        text = (
            f"🐍 <b>{STEP_PYTHON}</b>\n"
            f"<i>Для Legacy-проектов с aiogram 2.x подойдет 3.10</i>\n\n"
            f"На какой версии будет запущен твой код?"
        )
        await edit_photo_or_text(callback.message, text, "python_version")
    elif current_state == CreateStates.waiting_name:
        data = await state.get_data()
        if data.get("tmpdir") and os.path.exists(data.get("tmpdir", "")):
            await state.set_state(CreateStates.waiting_entry)
            text = f"📄 <b>{STEP_ENTRY}</b>\n\nВыбери файл:"
            kb = _get_entry_keyboard(data["tmpdir"], "/")
            await edit_photo_or_text(callback.message, text, "entry_point_script", reply_markup=kb)
        else:
            await state.set_state(CreateStates.waiting_entry)
            from bot.keyboards.user import get_entry_mode_keyboard
            await edit_photo_or_text(
                callback.message,
                f"📄 <b>{STEP_ENTRY}</b>\n\nВыбери режим:",
                "entry_point",
                reply_markup=get_entry_mode_keyboard(),
            )
    elif current_state == CreateStates.waiting_server:
        await state.set_state(CreateStates.waiting_name)
        await callback.message.edit_text(
            "📝 Введи название бота:",
            reply_markup=get_back_keyboard("create_back"),
        )
    else:
        await state.clear()
        await edit_photo_or_text(
            callback.message,
            "📋 <b>Панель управления</b>",
            "control_panel",
            reply_markup=get_back_keyboard("control_panel"),
        )

    await callback.answer()
