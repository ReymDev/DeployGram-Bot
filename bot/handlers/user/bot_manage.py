from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.user import (
    get_bot_control_keyboard,
    get_bot_list_keyboard,
    get_bot_settings_keyboard,
    get_logs_keyboard,
    get_delete_confirm_keyboard,
    get_python_change_keyboard,
    get_entry_change_keyboard,
    get_file_manager_keyboard,
    get_libs_keyboard,
    get_source_keyboard,
    get_python_version_keyboard,
    get_entry_mode_keyboard,
    get_confirm_entry_keyboard,
    get_server_select_keyboard,
)
from bot.keyboards.common import get_back_keyboard, get_control_panel_keyboard
from bot.utils.emojis import Emoji
from bot.utils.media import edit_photo_or_text
from bot.utils.formatters import format_status, format_uptime
from bot.config_photos import get_photo
from bot import texts

router = Router()


class BotRenameStates(StatesGroup):
    waiting_name = State()


class BotLibStates(StatesGroup):
    waiting_lib = State()


class BotEntryStates(StatesGroup):
    waiting_module = State()


class BotCreateStates(StatesGroup):
    waiting_github_url = State()
    waiting_zip = State()
    waiting_name = State()
    waiting_module = State()


async def _check_owner(callback: CallbackQuery, project_service, db_user, project_id: int, session=None, required_role: str = "developer"):
    """
    Check if user has access (owner or coowner).
    
    Args:
        required_role: Minimum role required. "developer" allows all coowners, "owner" requires owner only
    """
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return None
    
    # Owner always has full access
    if project.user_id == db_user.id:
        return project
    
    # Check coowner access if session provided
    if session is not None and required_role == "developer":
        from bot.utils.access import check_project_access
        has_access = await check_project_access(project, db_user, session)
        if has_access:
            return project
    
    await callback.answer(texts.ERROR_NO_ACCESS, show_alert=True)
    return None


@router.callback_query(F.data.startswith("bots_page_"))
async def bots_page(callback: CallbackQuery, db_user, project_service):
    page = int(callback.data.split("_")[-1])
    projects = await project_service.get_user_projects(db_user.id)
    from bot.keyboards.user import get_bot_list_keyboard
    await edit_photo_or_text(
        callback.message,
        texts.CONTROL_PANEL_TEXT,
        "control_panel",
        reply_markup=get_bot_list_keyboard(projects, page),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("bot_view_"))
async def bot_view(callback: CallbackQuery, project_service, db_user, session):
    project_id = int(callback.data.replace("bot_view_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id, session)
    if project is None:
        return

    monitoring = await project_service.get_monitoring(project_id)

    from repositories.server import ServerRepository
    from db.engine import async_session_factory
    server_text = ""
    async with async_session_factory() as session:
        server_repo = ServerRepository(session)
        server = await server_repo.get_by_id(project.server_id) if project.server_id else None
        if server:
            from bot.keyboards.user import get_flag
            flag = get_flag(server.country)
            server_text = f"{flag} Сервер: #{server.id}"

    status = monitoring.get("status", project.status)
    status_text = format_status(status)
    uptime_seconds = monitoring.get("uptime", 0)
    uptime = format_uptime(uptime_seconds) if uptime_seconds else "—"
    cpu = monitoring.get("cpu", 0)
    ram = monitoring.get("ram", 0)

    text = texts.bot_control_text(
        project.name,
        server_text,
        status_text,
        uptime,
        cpu,
        ram
    )

    await edit_photo_or_text(
        callback.message,
        text,
        "bot_control",
        reply_markup=get_bot_control_keyboard(project_id, status),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("bot_start_"))
async def bot_start(callback: CallbackQuery, project_service, db_user, session):
    from aiogram.exceptions import TelegramBadRequest
    import logging
    import traceback
    
    logger = logging.getLogger(__name__)
    
    project_id = int(callback.data.replace("bot_start_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id, session)
    if project is None:
        return

    success, msg = await project_service.start_project(project_id)
    project = await project_service.get_project(project_id)
    if project:
        try:
            await callback.message.edit_text(
                f"{Emoji.CHECK if success else Emoji.CROSS} {msg}",
                reply_markup=get_bot_control_keyboard(project_id, project.status),
            )
        except TelegramBadRequest as e:
            if "message is not modified" in str(e).lower():
                logger.warning(
                    f"[bot_start] Message not modified error ignored.\n"
                    f"File: {__file__}\n"
                    f"Function: bot_start\n"
                    f"Project ID: {project_id}\n"
                    f"User: {db_user.telegram_id}\n"
                    f"Error: {str(e)}"
                )
            else:
                logger.error(
                    f"[bot_start] Telegram error occurred.\n"
                    f"File: {__file__}\n"
                    f"Function: bot_start\n"
                    f"Project ID: {project_id}\n"
                    f"User: {db_user.telegram_id}\n"
                    f"Error: {str(e)}\n"
                    f"Traceback:\n{traceback.format_exc()}"
                )
        except Exception as e:
            logger.error(
                f"[bot_start] Unexpected error occurred.\n"
                f"File: {__file__}\n"
                f"Function: bot_start\n"
                f"Project ID: {project_id}\n"
                f"User: {db_user.telegram_id}\n"
                f"Error: {str(e)}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
    await callback.answer(f"{Emoji.CHECK if success else Emoji.CROSS} {msg}")


@router.callback_query(F.data.startswith("bot_stop_"))
async def bot_stop(callback: CallbackQuery, project_service, db_user, session):
    from aiogram.exceptions import TelegramBadRequest
    import logging
    import traceback
    
    logger = logging.getLogger(__name__)
    
    project_id = int(callback.data.replace("bot_stop_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id, session)
    if project is None:
        return

    success, msg = await project_service.stop_project(project_id)
    project = await project_service.get_project(project_id)
    if project:
        try:
            await callback.message.edit_text(
                f"{Emoji.CHECK if success else Emoji.CROSS} {msg}",
                reply_markup=get_bot_control_keyboard(project_id, project.status),
            )
        except TelegramBadRequest as e:
            if "message is not modified" in str(e).lower():
                logger.warning(
                    f"[bot_stop] Message not modified error ignored.\n"
                    f"File: {__file__}\n"
                    f"Function: bot_stop\n"
                    f"Project ID: {project_id}\n"
                    f"User: {db_user.telegram_id}\n"
                    f"Error: {str(e)}"
                )
            else:
                logger.error(
                    f"[bot_stop] Telegram error occurred.\n"
                    f"File: {__file__}\n"
                    f"Function: bot_stop\n"
                    f"Project ID: {project_id}\n"
                    f"User: {db_user.telegram_id}\n"
                    f"Error: {str(e)}\n"
                    f"Traceback:\n{traceback.format_exc()}"
                )
        except Exception as e:
            logger.error(
                f"[bot_stop] Unexpected error occurred.\n"
                f"File: {__file__}\n"
                f"Function: bot_stop\n"
                f"Project ID: {project_id}\n"
                f"User: {db_user.telegram_id}\n"
                f"Error: {str(e)}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
    await callback.answer(f"{Emoji.CHECK if success else Emoji.CROSS} {msg}")


@router.callback_query(F.data.startswith("bot_logs_"))
async def bot_logs(callback: CallbackQuery, project_service, db_user, session):
    project_id = int(callback.data.replace("bot_logs_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id, session)
    if project is None:
        return

    logs = await project_service.get_logs(project_id, tail=100)
    from bot.utils.formatters import truncate_text
    truncated = truncate_text(logs, 3500)

    text = (
        f"📋 Логи <b>{project.name}</b> (последние 3500 симв.)\n\n"
        f"<pre>{truncated}</pre>"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_logs_keyboard(project_id),
        )
    except Exception as e:
        from aiogram.exceptions import TelegramBadRequest
        import logging
        import traceback
        
        logger = logging.getLogger(__name__)
        
        if isinstance(e, TelegramBadRequest) and "message is not modified" in str(e).lower():
            logger.warning(
                f"[bot_logs] Message not modified error ignored.\n"
                f"File: {__file__}\n"
                f"Function: bot_logs\n"
                f"Project ID: {project_id}\n"
                f"Project name: {project.name}\n"
                f"User: {db_user.telegram_id}\n"
                f"Logs length: {len(logs)}\n"
                f"Text length: {len(text)}\n"
                f"Error: {str(e)}"
            )
        else:
            logger.error(
                f"[bot_logs] Failed to show logs.\n"
                f"File: {__file__}\n"
                f"Function: bot_logs\n"
                f"Project ID: {project_id}\n"
                f"Project name: {project.name}\n"
                f"User: {db_user.telegram_id}\n"
                f"Logs length: {len(logs)}\n"
                f"Text length: {len(text)}\n"
                f"Error: {str(e)}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            await callback.answer(f"Ошибка получения логов: {str(e)[:100]}", show_alert=True)
            return
    await callback.answer()


@router.callback_query(F.data.startswith("logs_file_"))
async def logs_file(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.replace("logs_file_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    logs = await project_service.get_logs(project_id, tail=1000)

    from aiogram.types import BufferedInputFile
    log_bytes = logs.encode("utf-8")
    file = BufferedInputFile(log_bytes, filename=f"{project.name}_logs.txt")

    await callback.message.answer_document(file, caption=f"📋 Логи {project.name}")
    await callback.answer()


@router.callback_query(F.data.startswith("bot_settings_"))
async def bot_settings(callback: CallbackQuery, project_service, db_user, session):
    project_id = int(callback.data.replace("bot_settings_", ""))
    # Settings require owner access
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return
    if project.user_id != db_user.id:
        await callback.answer("⛔ Только владелец может изменять настройки", show_alert=True)
        return

    from bot.keyboards.user import get_bot_settings_keyboard
    await edit_photo_or_text(
        callback.message,
        texts.BOT_SETTINGS_TEXT,
        "bot_settings",
        reply_markup=get_bot_settings_keyboard(project_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("bot_rename_"))
async def bot_rename(callback: CallbackQuery, state: FSMContext, project_service, db_user):
    project_id = int(callback.data.replace("bot_rename_", ""))
    # Rename requires owner access
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return
    if project.user_id != db_user.id:
        await callback.answer("⛔ Только владелец может переименовать проект", show_alert=True)
        return
    
    await state.update_data(rename_project_id=project_id)

    await callback.message.edit_text(
        texts.BOT_RENAME_TEXT,
        reply_markup=get_back_keyboard(f"bot_settings_{project_id}"),
        parse_mode="HTML"
    )
    await state.set_state(BotRenameStates.waiting_name)
    await callback.answer()


@router.message(F.text, BotRenameStates.waiting_name)
async def bot_rename_received(message: Message, state: FSMContext, project_service, db_user):
    import re
    name = message.text.strip()
    if not re.match(r"^[a-zA-Z0-9_-]{1,50}$", name):
        await message.answer(texts.ERROR_INVALID_NAME, parse_mode="HTML")
        return

    data = await state.get_data()
    project_id = data.get("rename_project_id")

    from repositories.project import ProjectRepository
    from db.engine import async_session_factory
    async with async_session_factory() as session:
        project_repo = ProjectRepository(session)
        await project_repo.update(project_id, name=name)

    await state.clear()
    await message.answer(
        texts.success_bot_renamed(name),
        reply_markup=get_back_keyboard(f"bot_view_{project_id}"),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("bot_delete_"))
async def bot_delete(callback: CallbackQuery, project_service, db_user, session):
    project_id = int(callback.data.replace("bot_delete_", ""))
    # Only owner can delete project
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return
    if project.user_id != db_user.id:
        await callback.answer("⛔ Только владелец может удалить проект", show_alert=True)
        return

    await edit_photo_or_text(
        callback.message,
        texts.BOT_DELETE_TEXT,
        "delete_bot",
        reply_markup=get_delete_confirm_keyboard(project_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("bot_del_confirm_"))
async def bot_delete_confirm(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.replace("bot_del_confirm_", ""))
    # Only owner can delete project
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return
    if project.user_id != db_user.id:
        await callback.answer("⛔ Только владелец может удалить проект", show_alert=True)
        return

    project_name = project.name
    try:
        await project_service.delete_project(project_id)
    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)
        return

    await edit_photo_or_text(
        callback.message,
        texts.bot_deleted_text(project_name),
        "bot_deleted",
        reply_markup=get_back_keyboard("control_panel"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("bot_python_"))
async def bot_python(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.replace("bot_python_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    await edit_photo_or_text(
        callback.message,
        texts.BOT_PYTHON_TEXT,
        "python_change",
        reply_markup=get_python_change_keyboard(project_id, project.python_version),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_python_"))
async def set_python(callback: CallbackQuery, project_service, db_user):
    parts = callback.data.replace("set_python_", "").split("_")
    project_id = int(parts[0])
    version = parts[1]

    if version not in ("3.10", "3.11", "3.12"):
        await callback.answer("Неверная версия Python", show_alert=True)
        return

    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    from repositories.project import ProjectRepository
    from db.engine import async_session_factory
    async with async_session_factory() as session:
        project_repo = ProjectRepository(session)
        await project_repo.update(project_id, python_version=version)

    await callback.answer(texts.success_python_changed(version), show_alert=True)
    await bot_python(callback, project_service, db_user)


@router.callback_query(F.data.startswith("bot_entry_"))
async def bot_entry(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.replace("bot_entry_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    await edit_photo_or_text(
        callback.message,
        texts.bot_entry_text(project.entry_type, project.entry_point),
        "entry_change",
        reply_markup=get_entry_change_keyboard(project_id, project.entry_type, project.entry_point),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_entry_"))
async def set_entry(callback: CallbackQuery, project_service, db_user, state: FSMContext):
    parts = callback.data.replace("set_entry_", "").split("_")
    project_id = int(parts[0])
    entry_type = parts[1]

    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    if entry_type == "module":
        await state.update_data(entry_project_id=project_id)
        await callback.message.edit_text(
            texts.BOT_ENTRY_MODULE_TEXT,
            "Режим: Модульный запуск / python -m\n\n"
            "Отправь имя модуля вручную.\n"
            "Примеры: <code>app.pkg.main</code>",
            reply_markup=get_back_keyboard(f"bot_entry_{project_id}"),
        )
        await state.set_state(BotEntryStates.waiting_module)
    else:
        await callback.answer("Выберите файл через файловый менеджер", show_alert=True)

    await callback.answer()


@router.message(F.text, BotEntryStates.waiting_module)
async def entry_module_received(message: Message, state: FSMContext):
    module = message.text.strip()
    data = await state.get_data()
    project_id = data.get("entry_project_id")

    from repositories.project import ProjectRepository
    from db.engine import async_session_factory
    async with async_session_factory() as session:
        project_repo = ProjectRepository(session)
        await project_repo.update(project_id, entry_point=module, entry_type="module")

    await state.clear()
    await message.answer(
        f"{Emoji.CHECK} Точка входа: <code>{module}</code>",
        reply_markup=get_back_keyboard(f"bot_view_{project_id}"),
    )


@router.callback_query(F.data.startswith("bot_files_"))
async def bot_files(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.replace("bot_files_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    files = await project_service.list_files(project_id, "/app")

    await edit_photo_or_text(
        callback.message,
        texts.BOT_FILES_TEXT,
        "file_manager",
        reply_markup=get_file_manager_keyboard(project_id, files, "/app"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("bot_libs_"))
async def bot_libs(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.replace("bot_libs_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    # Получаем установленные пакеты через pip list
    libs = await project_service.get_installed_packages(project_id)

    await edit_photo_or_text(
        callback.message,
        texts.BOT_LIBS_TEXT,
        "library_manager",
        reply_markup=get_libs_keyboard(project_id, libs),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lib_add_"))
async def lib_add(callback: CallbackQuery, state: FSMContext):
    project_id = int(callback.data.replace("lib_add_", ""))
    await state.update_data(lib_project_id=project_id)

    await callback.message.edit_text(
        texts.BOT_LIB_ADD_TEXT,
        reply_markup=get_back_keyboard(f"bot_libs_{project_id}"),
    )
    await state.set_state(BotLibStates.waiting_lib)
    await callback.answer()


@router.message(F.text, BotLibStates.waiting_lib)
async def lib_add_received(message: Message, state: FSMContext, project_service, db_user):
    lib = message.text.strip()
    data = await state.get_data()
    project_id = data.get("lib_project_id")

    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await message.answer(texts.ERROR_NOT_FOUND)
        await state.clear()
        return

    try:
        content = await project_service.read_file(project_id, "/app/requirements.txt")
        existing = content.strip() if content else ""
    except Exception:
        existing = ""

    if existing:
        new_content = existing + "\n" + lib
    else:
        new_content = lib

    await project_service.write_file(project_id, "/app/requirements.txt", new_content)

    await state.clear()
    await message.answer(
        texts.success_lib_added(lib),
        reply_markup=get_back_keyboard(f"bot_view_{project_id}"),
    )


@router.callback_query(F.data.startswith("lib_del_"))
async def lib_del(callback: CallbackQuery, project_service, db_user):
    parts = callback.data.replace("lib_del_", "").split("_", 1)
    project_id = int(parts[0])
    lib_name = parts[1] if len(parts) > 1 else ""

    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    try:
        content = await project_service.read_file(project_id, "/app/requirements.txt")
        if content:
            lines = content.strip().split("\n")
            new_lines = [l for l in lines if not l.strip().startswith(lib_name)]
            await project_service.write_file(project_id, "/app/requirements.txt", "\n".join(new_lines))
    except Exception:
        pass

    await callback.answer(f"✅ {lib_name} удалена", show_alert=True)
    await bot_libs(callback, project_service, db_user)


# ─── CO-OWNERS ───

@router.callback_query(F.data.startswith("bot_coowners_"))
async def bot_coowners(callback: CallbackQuery, project_service, db_user, session):
    project_id = int(callback.data.replace("bot_coowners_", ""))
    # Only owner can manage coowners
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return
    if project.user_id != db_user.id:
        await callback.answer("⛔ Только владелец может управлять совладельцами", show_alert=True)
        return

    from repositories.coowner import CoOwnerRepository
    coowner_repo = CoOwnerRepository(session)
    coowners = await coowner_repo.get_by_project_id(project_id)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()

    for co in coowners:
        builder.row(
            InlineKeyboardButton(
                text=f"👤 ID:{co.user_id} ({co.role})",
                callback_data=f"noop",
            ),
            InlineKeyboardButton(text="🗑", callback_data=f"coowner_del_{project_id}_{co.id}", style="danger"),
        )

    builder.row(
        InlineKeyboardButton(text="➕ Добавить", callback_data=f"coowner_add_{project_id}", style="primary"),
    )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data=f"bot_settings_{project_id}"),
    )

    await callback.message.edit_text(
        f"👥 <b>Совладельцы: {project.name}</b>\n\n"
        f"Роли:\n"
        f"  <b>Owner</b> — полный доступ\n"
        f"  <b>Developer</b> — запуск, остановка, логи, файлы",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


class CoOwnerStates(StatesGroup):
    waiting_id = State()


@router.callback_query(F.data.startswith("coowner_add_"))
async def coowner_add(callback: CallbackQuery, project_service, db_user, state: FSMContext):
    project_id = int(callback.data.replace("coowner_add_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    await state.update_data(coowner_project_id=project_id)

    await callback.message.edit_text(
        "👤 Отправь Telegram ID пользователя для добавления:",
        reply_markup=get_back_keyboard(f"bot_coowners_{project_id}"),
    )
    await state.set_state(CoOwnerStates.waiting_id)
    await callback.answer()


@router.message(F.text, CoOwnerStates.waiting_id)
async def coowner_id_received(message: Message, state: FSMContext, session, db_user):
    data = await state.get_data()
    project_id = data.get("coowner_project_id")

    try:
        target_telegram_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введи числовой Telegram ID")
        return

    if target_telegram_id == db_user.telegram_id:
        await message.answer("❌ Нельзя добавить самого себя")
        return

    from repositories.user import UserRepository
    user_repo = UserRepository(session)
    target_user = await user_repo.get_by_telegram_id(target_telegram_id)

    if target_user is None:
        await message.answer("❌ Пользователь не найден. Он должен хотя бы раз запустить бота.")
        return

    from repositories.coowner import CoOwnerRepository
    coowner_repo = CoOwnerRepository(session)
    existing = await coowner_repo.get_by_user_and_project(target_user.id, project_id)
    if existing:
        await message.answer("❌ Этот пользователь уже совладелец")
        return

    await coowner_repo.create(project_id=project_id, user_id=target_user.id, role="developer")

    await state.clear()
    await message.answer(
        f"✅ Пользователь <b>{target_user.username or target_telegram_id}</b> добавлен как совладелец.",
        reply_markup=get_back_keyboard(f"bot_coowners_{project_id}"),
    )


@router.callback_query(F.data.startswith("coowner_del_"))
async def coowner_del(callback: CallbackQuery, project_service, db_user, session):
    parts = callback.data.replace("coowner_del_", "").split("_")
    project_id = int(parts[0])
    coowner_id = int(parts[1])

    project = await _check_owner(callback, project_service, db_user, project_id, session)
    if project is None:
        return

    from repositories.coowner import CoOwnerRepository
    coowner_repo = CoOwnerRepository(session)
    coowner = await coowner_repo.get_by_id(coowner_id)
    if coowner is None or coowner.project_id != project_id:
        await callback.answer("Not found", show_alert=True)
        return

    await coowner_repo.delete(coowner_id)

    await callback.answer("✅ Совладелец удалён", show_alert=True)


# ─── EDITOR ───

@router.callback_query(F.data.startswith("bot_editor_"))
async def bot_editor(callback: CallbackQuery, project_service, db_user, state: FSMContext):
    project_id = int(callback.data.replace("bot_editor_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    await state.update_data(editor_project_id=project_id)

    await callback.message.edit_text(
        f"🖋 <b>Редактор: {project.name}</b>\n\n"
        f"Отправь файл для редактирования (.py, .txt, .env, .json, .yaml)\n"
        f"Или введи путь к файлу в проекте:",
        reply_markup=get_back_keyboard(f"bot_settings_{project_id}"),
    )
    await state.set_state(EditorStates.waiting_file)
    await callback.answer()


class EditorStates(StatesGroup):
    waiting_file = State()
    sending = State()


@router.message(F.document, EditorStates.waiting_file)
async def editor_file_uploaded(message: Message, state: FSMContext, project_service, db_user):
    if not message.document or not message.document.file_name:
        return

    file_name = message.document.file_name
    allowed = (".py", ".txt", ".env", ".json", ".yaml", ".yml", ".toml", ".cfg")
    if not file_name.endswith(allowed):
        await message.answer("❌ Поддерживаются только: .py, .txt, .env, .json, .yaml")
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
        f"🖋 <b>Редактирование: {file_name}</b>\n\n"
        f"<code>{text[:2000]}</code>\n\n"
        f"Отправь новый текст файла:",
    )
    await state.set_state(EditorStates.sending)


@router.message(F.text, EditorStates.waiting_file)
async def editor_text_input(message: Message, state: FSMContext):
    file_path = message.text.strip()
    await state.update_data(editor_file_name=file_path)
    await message.answer(
        f"🖋 Файл: <code>{file_path}</code>\n\nОтправь новый текст:",
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
                    f"✅ Файл <b>{file_name}</b> сохранён.",
                    reply_markup=get_back_keyboard(f"bot_view_{project_id}"),
                )
            else:
                await message.answer(
                    f"❌ Ошибка сохранения файла.",
                    reply_markup=get_back_keyboard(f"bot_view_{project_id}"),
                )
    await state.clear()


# ─── GRAPHS ───

@router.callback_query(F.data.startswith("bot_graphs_"))
async def bot_graphs(callback: CallbackQuery, project_service, db_user, session):
    project_id = int(callback.data.replace("bot_graphs_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    from services.monitoring import MonitoringService
    monitoring = MonitoringService(session)
    stats = await monitoring.get_stats_history(project_id, 24)

    if not stats:
        await callback.answer("Нет данных за этот период", show_alert=True)
        return

    avg_cpu = sum(s.cpu_percent for s in stats) / len(stats)
    max_cpu = max(s.cpu_percent for s in stats)
    avg_ram = sum(s.ram_mb for s in stats) / len(stats)
    max_ram = max(s.ram_mb for s in stats)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    for h in [24, 168, 720]:
        label = {24: "24ч", 168: "7д", 720: "30д"}[h]
        builder.row(
            InlineKeyboardButton(text=f"📊 {label}", callback_data=f"bot_graphs_{project_id}_{h}")
        )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data=f"bot_view_{project_id}"),
    )

    await callback.message.edit_text(
        f"📊 <b>Графики за 24ч</b>\n\n"
        f"📊 CPU:\n  Среднее: {avg_cpu:.1f}%\n  Максимум: {max_cpu:.1f}%\n\n"
        f"📈 RAM:\n  Среднее: {avg_ram:.1f} MB\n  Максимум: {max_ram:.1f} MB\n\n"
        f"ℹ Точек данных: {len(stats)}",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


# ─── NOTIFICATIONS ───

@router.callback_query(F.data.startswith("bot_notify_"))
async def bot_notify(callback: CallbackQuery, user_service, db_user):
    project_id = int(callback.data.replace("bot_notify_", ""))

    s = await user_service.get_settings(db_user.id)
    if s is None:
        await callback.answer("Настройки не найдены", show_alert=True)
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()

    items = [
        ("notify_container_stopped", "Контейнер остановлен", s.notify_container_stopped),
        ("notify_container_started", "Контейнер запущен", s.notify_container_started),
        ("notify_error", "Ошибка запуска", s.notify_error),
        ("notify_high_cpu", "Высокая нагрузка CPU", s.notify_high_cpu),
        ("notify_high_ram", "Высокая нагрузка RAM", s.notify_high_ram),
        ("notify_low_disk", "Мало места на диске", s.notify_low_disk),
        ("notify_backup_created", "Бэкап создан", s.notify_backup_created),
        ("notify_update_done", "Обновление завершено", s.notify_update_done),
    ]

    for data_key, label, val in items:
        icon = "✅" if val else "❌"
        builder.row(
            InlineKeyboardButton(text=f"{icon} {label}", callback_data=f"toggle_{data_key}"),
        )

    builder.row(
        InlineKeyboardButton(text="Назад", callback_data=f"bot_settings_{project_id}"),
    )

    await callback.message.edit_text(
        f"🔔 <b>Настройки уведомлений</b>",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_"))
async def toggle_notification(callback: CallbackQuery, user_service, db_user):
    setting = callback.data.replace("toggle_", "")
    valid_settings = [
        "notify_container_stopped", "notify_container_started", "notify_error",
        "notify_high_cpu", "notify_high_ram", "notify_low_disk",
        "notify_backup_created", "notify_update_done",
    ]
    if setting not in valid_settings:
        await callback.answer("Неизвестная настройка", show_alert=True)
        return

    await user_service.toggle_setting(db_user.id, setting)
    await callback.answer("Настройка изменена")

    s = await user_service.get_settings(db_user.id)
    if s:
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        builder = InlineKeyboardBuilder()

        items = [
            ("notify_container_stopped", "Контейнер остановлен", s.notify_container_stopped),
            ("notify_container_started", "Контейнер запущен", s.notify_container_started),
            ("notify_error", "Ошибка запуска", s.notify_error),
            ("notify_high_cpu", "Высокая нагрузка CPU", s.notify_high_cpu),
            ("notify_high_ram", "Высокая нагрузка RAM", s.notify_high_ram),
            ("notify_low_disk", "Мало места на диске", s.notify_low_disk),
            ("notify_backup_created", "Бэкап создан", s.notify_backup_created),
            ("notify_update_done", "Обновление завершено", s.notify_update_done),
        ]

        for data_key, label, val in items:
            icon = "✅" if val else "❌"
            builder.row(
                InlineKeyboardButton(text=f"{icon} {label}", callback_data=f"toggle_{data_key}"),
            )

        project_id = int(callback.data.split("_")[-1]) if callback.data.split("_")[-1].isdigit() else 0
        builder.row(
            InlineKeyboardButton(text="Назад", callback_data=f"bot_settings_{project_id}"),
        )

        try:
            await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
        except Exception:
            pass
