from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
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
from bot.utils.media import edit_photo_or_text
from services.github import GitHubService

router = Router()


@router.callback_query(F.data == "create_project")
async def create_project_start(callback: CallbackQuery, user_service, db_user, project_service, state: FSMContext):
    from bot import texts
    
    # Проверка лимита проектов
    max_projects = await user_service.get_max_projects(db_user.tariff)
    current_count = await project_service.count_user_projects(db_user.id)
    
    if current_count >= max_projects:
        await callback.answer(
            f"⚠️ Достигнут лимит проектов ({max_projects})\n\n"
            f"Обнови подписку для больших возможностей!",
            show_alert=True,
        )
        return

    await state.clear()
    await edit_photo_or_text(
        callback.message,
        texts.ADD_BOT_SOURCE_TEXT,
        "upload_source",
        reply_markup=get_create_project_step1_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ProjectCreateStates.waiting_source)
    await callback.answer()


@router.callback_query(F.data.startswith("create_type_"), ProjectCreateStates.waiting_source)
async def create_type_selected(callback: CallbackQuery, state: FSMContext):
    from bot import texts
    source_type = callback.data.replace("create_type_", "")
    await state.update_data(source_type=source_type)

    if source_type == "github":
        await edit_photo_or_text(
            callback.message,
            texts.ADD_BOT_GITHUB_TEXT,
            "github_repos",
            reply_markup=get_back_keyboard("create_project"),
            parse_mode="HTML"
        )
        await state.set_state(ProjectCreateStates.waiting_github_url)
    else:
        await edit_photo_or_text(
            callback.message,
            texts.ADD_BOT_ZIP_TEXT,
            "file_upload",
            reply_markup=get_back_keyboard("create_project"),
            parse_mode="HTML"
        )
        await state.set_state(ProjectCreateStates.waiting_zip)
    await callback.answer()


@router.message(ProjectCreateStates.waiting_github_url)
async def github_url_received(message: Message, state: FSMContext):
    from bot import texts
    url = message.text.strip()
    parsed = GitHubService.parse_github_url(url)
    if parsed is None:
        await message.answer(
            "❌ <b>Невалидный URL</b>\n\n"
            "Используй формат:\n"
            "<code>https://github.com/user/repo</code>",
            reply_markup=get_back_keyboard("create_project"),
            parse_mode="HTML"
        )
        return

    owner, repo = parsed
    gh = GitHubService()
    info = await gh.get_repo_info(owner, repo)
    if info is None:
        await message.answer(
            "❌ <b>Репозиторий не найден</b>\n\n"
            "Проверь что репозиторий публичный или у нас есть доступ.",
            reply_markup=get_back_keyboard("create_project"),
            parse_mode="HTML"
        )
        return

    await state.update_data(source_url=url, source_owner=owner, source_repo=repo)
    
    from html import escape

    description = escape(str(info.get("description") or "Без описания"))
    full_name = escape(str(info.get("full_name") or url))
    await message.answer(
        f"✅ <b>Репозиторий найден</b>\n\n"
        f"📦 <b>{full_name}</b>\n"
        f"<blockquote>📝 {description}</blockquote>\n\n"
        f"{texts.add_bot_python_text()}",
        reply_markup=get_python_version_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ProjectCreateStates.waiting_python)


@router.message(ProjectCreateStates.waiting_zip)
async def zip_received(message: Message, state: FSMContext):
    from bot import texts
    if not message.document or not (message.document.file_name or "").lower().endswith(".zip"):
        await message.answer(
            "❌ <b>Неверный формат</b>\n\n"
            "Отправь ZIP архив (.zip файл).",
            reply_markup=get_back_keyboard("create_project"),
            parse_mode="HTML"
        )
        return

    # Check file size (max 100MB)
    MAX_ZIP_SIZE = 100 * 1024 * 1024  # 100 MB
    if message.document.file_size and message.document.file_size > MAX_ZIP_SIZE:
        await message.answer(
            f"❌ <b>Файл слишком большой</b>\n\n"
            f"Максимум: {MAX_ZIP_SIZE // (1024*1024)} МБ\n"
            f"Твой файл: {message.document.file_size // (1024*1024)} МБ",
            reply_markup=get_back_keyboard("create_project"),
            parse_mode="HTML"
        )
        return

    await state.update_data(zip_file_id=message.document.file_id)
    await message.answer(
        f"✅ <b>Архив получен</b>\n\n"
        f"{texts.add_bot_python_text(message.document.file_name)}",
        reply_markup=get_python_version_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ProjectCreateStates.waiting_python)


@router.callback_query(F.data.startswith("create_python_"), ProjectCreateStates.waiting_python)
async def python_selected(callback: CallbackQuery, state: FSMContext):
    from bot import texts
    version = callback.data.replace("create_python_", "")
    await state.update_data(python_version=version)

    await edit_photo_or_text(
        callback.message,
        f"✅ <b>Python {version}</b>\n\n"
        f"{texts.ADD_BOT_ENTRY_TEXT}",
        "entry_point",
        reply_markup=get_entry_type_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ProjectCreateStates.waiting_entry)
    await callback.answer()


@router.callback_query(F.data == "create_entry_script", ProjectCreateStates.waiting_entry)
async def entry_script(callback: CallbackQuery, state: FSMContext):
    from bot import texts
    await state.update_data(entry_type="script")
    
    await edit_photo_or_text(
        callback.message,
        texts.add_bot_entry_script_text(),
        "entry_point_script",
        reply_markup=get_back_keyboard("create_project"),
        parse_mode="HTML"
    )
    await state.set_state(ProjectCreateStates.waiting_entry_module)
    await callback.answer()


@router.callback_query(F.data == "create_entry_module", ProjectCreateStates.waiting_entry)
async def entry_module(callback: CallbackQuery, state: FSMContext):
    from bot import texts
    await state.update_data(entry_type="module")
    
    await edit_photo_or_text(
        callback.message,
        texts.ADD_BOT_ENTRY_MODULE_TEXT,
        "entry_point_module",
        reply_markup=get_back_keyboard("create_project"),
        parse_mode="HTML"
    )
    await state.set_state(ProjectCreateStates.waiting_entry_module)
    await callback.answer()


@router.message(ProjectCreateStates.waiting_entry_module)
async def entry_received(message: Message, state: FSMContext):
    from bot import texts
    entry = message.text.strip() or "main.py"
    
    data = await state.get_data()
    entry_type = data.get("entry_type", "script")
    
    # Validate entry point for security
    if entry_type == "module":
        # Block dangerous built-in modules
        dangerous_modules = [
            "os", "subprocess", "sys", "socket", "requests",
            "urllib", "http", "smtplib", "ftplib", "telnetlib",
            "__import__", "eval", "exec", "compile"
        ]
        module_parts = entry.split(".")
        if any(part in dangerous_modules for part in module_parts):
            await message.answer(
                "❌ <b>Небезопасный модуль</b>\n\n"
                "Использование системных модулей запрещено из соображений безопасности.\n\n"
                "Используй пользовательские модули из своего проекта.",
                reply_markup=get_back_keyboard("create_project"),
                parse_mode="HTML"
            )
            return
        
        # Validate module name format
        import re
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', entry):
            await message.answer(
                "❌ <b>Невалидное имя модуля</b>\n\n"
                "Используй формат: <code>mypackage.mymodule</code>",
                reply_markup=get_back_keyboard("create_project"),
                parse_mode="HTML"
            )
            return
    else:
        # Validate script path
        if ".." in entry or entry.startswith("/"):
            await message.answer(
                "❌ <b>Невалидный путь</b>\n\n"
                "Используй относительный путь без <code>../</code>",
                reply_markup=get_back_keyboard("create_project"),
                parse_mode="HTML"
            )
            return
    
    await state.update_data(entry_point=entry)

    from html import escape
    await message.answer(
        f"✅ <b>Точка входа:</b> <code>{escape(entry)}</code>\n\n"
        f"{texts.ADD_BOT_NAME_TEXT}",
        reply_markup=get_back_keyboard("create_project"),
        parse_mode="HTML"
    )
    await state.set_state(ProjectCreateStates.waiting_name)


@router.message(ProjectCreateStates.waiting_name)
async def name_received(message: Message, state: FSMContext):
    import re
    name = message.text.strip()
    if not re.match(r"^[a-zA-Z0-9_-]{1,50}$", name):
        await message.answer(
            "❌ <b>Невалидное имя</b>\n\n"
            "Используй буквы, цифры, _ и - (1-50 символов).",
            reply_markup=get_back_keyboard("create_project"),
            parse_mode="HTML"
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
            f"🌍 <b>Нет доступных серверов</b>\n\n"
            f"Проект будет создан без конкретного сервера.",
            reply_markup=get_back_keyboard("create_project"),
            parse_mode="HTML"
        )
        await state.set_state(ProjectCreateStates.confirming)
        await show_confirmation(message, state)
    else:
        await message.answer(
            f"🌍 <b>Выбери сервер:</b>",
            reply_markup=get_server_select_keyboard(servers),
            parse_mode="HTML"
        )
        await state.set_state(ProjectCreateStates.waiting_server)


@router.callback_query(F.data == "create_back", StateFilter(ProjectCreateStates))
async def create_back_active(callback: CallbackQuery, state: FSMContext):
    from bot import texts
    await state.clear()
    await state.set_state(ProjectCreateStates.waiting_source)
    await edit_photo_or_text(
        callback.message,
        texts.ADD_BOT_SOURCE_TEXT,
        "upload_source",
        reply_markup=get_create_project_step1_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "server_pool_info")
async def server_pool_info(callback: CallbackQuery):
    await callback.answer(
        "🖥 Это общий пул серверов: проект будет размещён на свободной площадке автоматически.",
        show_alert=True,
    )


@router.callback_query(F.data.startswith("create_server_"), ProjectCreateStates.waiting_server)
async def server_selected(callback: CallbackQuery, state: FSMContext):
    server_id = int(callback.data.replace("create_server_", ""))
    await state.update_data(server_id=server_id)
    await show_confirmation(callback.message, state, edit=True)
    await callback.answer()


async def show_confirmation(message, state: FSMContext, edit: bool = False):
    from bot import texts
    data = await state.get_data()
    source = data.get("source_type", "zip")
    source_text = "🔗 GitHub" if source == "github" else "📦 ZIP архив"
    version = data.get("python_version", "3.12")
    entry = data.get("entry_point", "main.py")
    entry_type = data.get("entry_type", "script")
    name = data.get("name", "my_project")

    text = texts.add_bot_confirm_text(name, version, entry)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(style="success", text="✅ Создать проект", callback_data="create_confirm"),
        InlineKeyboardButton(text="❌ Отмена", style="primary", callback_data="main_menu"),
    )
    kb = builder.as_markup()

    if edit:
        await edit_photo_or_text(
            message, text, "entry_confirm", reply_markup=kb, parse_mode="HTML"
        )
    else:
        await message.answer(text, reply_markup=kb, parse_mode="HTML")

    await state.set_state(ProjectCreateStates.confirming)


@router.callback_query(F.data == "create_confirm", ProjectCreateStates.confirming)
async def create_confirmed(callback: CallbackQuery, state: FSMContext, db_user, project_service, user_service, session):
    import logging
    from bot import texts
    logger = logging.getLogger(__name__)
    
    data = await state.get_data()

    max_projects = await user_service.get_max_projects(db_user.tariff)
    current_count = await project_service.count_user_projects(db_user.id)
    if current_count >= max_projects:
        await callback.answer(
            f"⚠️ Достигнут лимит проектов ({max_projects})\n\nОбнови подписку для больших возможностей!",
            show_alert=True,
        )
        return

    files_zip = None
    source_type = data.get("source_type", "zip")
    if source_type == "zip":
        zip_file_id = data.get("zip_file_id")
        if zip_file_id:
            try:
                logger.info("Downloading ZIP file: %s", zip_file_id)
                file = await callback.bot.get_file(zip_file_id)
                files_zip = await callback.bot.download_file(file.file_path)
                if hasattr(files_zip, "seek"):
                    files_zip.seek(0)
                size = len(files_zip.getvalue()) if hasattr(files_zip, "getvalue") else 0
                logger.info("ZIP file downloaded successfully, size: %d bytes", size)
            except Exception as e:
                logger.error("Failed to download ZIP file: %s", e)
                await callback.answer(f"❌ Ошибка загрузки файла: {e}", show_alert=True)
                return
        else:
            await callback.answer("❌ ZIP-архив не найден, начните создание заново", show_alert=True)
            return
    elif source_type == "github":
        owner = data.get("source_owner")
        repo = data.get("source_repo")
        if not owner or not repo:
            await callback.answer("❌ Ссылка на GitHub потеряна, начните создание заново", show_alert=True)
            return
        try:
            from services.github import GitHubService
            files_zip = await GitHubService().download_zip(owner, repo)
        except Exception as e:
            logger.error("Failed to download GitHub archive: %s", e)
            files_zip = None
        if not files_zip:
            await callback.answer(
                "❌ Не удалось скачать репозиторий GitHub (ветка main/master, размер до 100 МБ)",
                show_alert=True,
            )
            return

    logger.info("Creating project: name=%s, source_type=%s, server_id=%s, has_files=%s",
                data.get("name"), source_type, data.get("server_id"), files_zip is not None)

    try:
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
    except ValueError as e:
        await callback.answer(f"❌ {e}", show_alert=True)
        return
    
    logger.info("Project created successfully: id=%d, name=%s", project.id, project.name)

    await state.clear()

    from bot.keyboards.user import get_project_manage_keyboard
    await edit_photo_or_text(
        callback.message,
        f"🎉 <b>Проект создан!</b>\n\n"
        f"<b>{project.name}</b> готов к запуску.\n\n"
        f"Нажми <b>\"Запустить\"</b> чтобы развернуть его в облаке.",
        "bot_ready",
        reply_markup=get_project_manage_keyboard(project.id, project.status),
        parse_mode="HTML"
    )
    await callback.answer()
