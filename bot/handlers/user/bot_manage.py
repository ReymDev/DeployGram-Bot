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


async def _check_owner(callback: CallbackQuery, project_service, db_user, project_id: int):
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer("Бот не найден", show_alert=True)
        return None
    if project.user_id != db_user.id:
        await callback.answer("Нет доступа", show_alert=True)
        return None
    return project


@router.callback_query(F.data.startswith("bots_page_"))
async def bots_page(callback: CallbackQuery, db_user, project_service):
    page = int(callback.data.split("_")[-1])
    projects = await project_service.get_user_projects(db_user.id)
    from bot.keyboards.user import get_bot_list_keyboard
    await edit_photo_or_text(
        callback.message,
        "📋 <b>Панель управления</b>\n\nНажми на кнопку с названием бота, чтобы управлять им.",
        "control_panel",
        reply_markup=get_bot_list_keyboard(projects, page),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("bot_view_"))
async def bot_view(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.replace("bot_view_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
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
    uptime = monitoring.get("uptime", "—")
    cpu = monitoring.get("cpu", 0)
    ram = monitoring.get("ram", 0)

    text = (
        f"📋 <b>Панель управления</b>\n\n"
        f"<b>{project.name}</b>\n"
        f"{server_text}\n\n"
        f"{status_text} · Аптайм: {uptime}\n"
        f"CPU: {cpu:.2f}% · RAM: {ram:.2f}%"
    )

    await edit_photo_or_text(
        callback.message,
        text,
        "bot_control",
        reply_markup=get_bot_control_keyboard(project_id, status),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("bot_start_"))
async def bot_start(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.replace("bot_start_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    success, msg = await project_service.start_project(project_id)
    project = await project_service.get_project(project_id)
    if project:
        await callback.message.edit_text(
            f"{Emoji.CHECK if success else Emoji.CROSS} {msg}",
            reply_markup=get_bot_control_keyboard(project_id, project.status),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("bot_stop_"))
async def bot_stop(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.replace("bot_stop_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    success, msg = await project_service.stop_project(project_id)
    project = await project_service.get_project(project_id)
    if project:
        await callback.message.edit_text(
            f"{Emoji.CHECK if success else Emoji.CROSS} {msg}",
            reply_markup=get_bot_control_keyboard(project_id, project.status),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("bot_logs_"))
async def bot_logs(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.replace("bot_logs_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    logs = await project_service.get_logs(project_id, tail=100)
    from bot.utils.formatters import truncate_text
    truncated = truncate_text(logs, 3500)

    text = (
        f"📋 Логи <b>{project.name}</b> (последние 3500 симв.)\n\n"
        f"<code>{truncated}</code>"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_logs_keyboard(project_id),
    )
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
async def bot_settings(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.replace("bot_settings_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    text = (
        f"⚙ <b>Настройки бота</b>\n\n"
        f"Выбери, что хочешь сделать с ботом:"
    )

    await edit_photo_or_text(
        callback.message,
        text,
        "bot_settings",
        reply_markup=get_bot_settings_keyboard(project_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("bot_rename_"))
async def bot_rename(callback: CallbackQuery, state: FSMContext):
    project_id = int(callback.data.replace("bot_rename_", ""))
    await state.update_data(rename_project_id=project_id)

    await edit_photo_or_text(
        callback.message,
        "✏ <b>Смена названия</b>\n\nВведи новое название для бота:",
        "rename_bot",
        reply_markup=get_back_keyboard(f"bot_settings_{project_id}"),
    )
    await state.set_state(BotRenameStates.waiting_name)
    await callback.answer()


@router.message(F.text, BotRenameStates.waiting_name)
async def bot_rename_received(message: Message, state: FSMContext, project_service, db_user):
    import re
    name = message.text.strip()
    if not re.match(r"^[a-zA-Z0-9_-]{1,50}$", name):
        await message.answer("❌ Имя: буквы, цифры, _ и - (1-50 символов)")
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
        f"{Emoji.CHECK} Бот переименован в <b>{name}</b>",
        reply_markup=get_back_keyboard(f"bot_view_{project_id}"),
    )


@router.callback_query(F.data.startswith("bot_delete_"))
async def bot_delete(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.replace("bot_delete_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    text = (
        f"🗑 <b>Удаление бота</b>\n\n"
        f"Подтверди удаление бота, восстановить доступ к нему будет "
        f"невозможно - только загрузить заново."
    )

    await edit_photo_or_text(
        callback.message,
        text,
        "delete_bot",
        reply_markup=get_delete_confirm_keyboard(project_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("bot_del_confirm_"))
async def bot_delete_confirm(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.replace("bot_del_confirm_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    project_name = project.name
    try:
        await project_service.delete_project(project_id)
    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)
        return

    text = (
        f"🗑 <b>Удаление бота</b>\n\n"
        f"Бот <b>{project_name}</b> удален."
    )

    await edit_photo_or_text(
        callback.message,
        text,
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

    text = (
        f"🐍 <b>Смена версии Python</b>\n\n"
        f"Бот перезапустится после смены версии."
    )

    await edit_photo_or_text(
        callback.message,
        text,
        "python_change",
        reply_markup=get_python_change_keyboard(project_id, project.python_version),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_python_"))
async def set_python(callback: CallbackQuery, project_service, db_user):
    parts = callback.data.replace("set_python_", "").split("_")
    project_id = int(parts[0])
    version = parts[1]

    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    from repositories.project import ProjectRepository
    from db.engine import async_session_factory
    async with async_session_factory() as session:
        project_repo = ProjectRepository(session)
        await project_repo.update(project_id, python_version=version)

    await callback.answer(f"✅ Python изменён на {version}", show_alert=True)
    await bot_python(callback, project_service, db_user)


@router.callback_query(F.data.startswith("bot_entry_"))
async def bot_entry(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.replace("bot_entry_", ""))
    project = await _check_owner(callback, project_service, db_user, project_id)
    if project is None:
        return

    text = (
        f"📄 <b>Смена точки входа</b>\n\n"
        f"Выбери режим запуска:\n"
        f"• <b>Скрипт</b> - для <code>python file.py</code>\n"
        f"• <b>Модуль</b> - для <code>python -m package.module</code>\n\n"
        f"Текущий режим: <b>{project.entry_type}</b>\n"
        f"Текущее значение: <b>{project.entry_point}</b>"
    )

    await edit_photo_or_text(
        callback.message,
        text,
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
            "📄 <b>Выбор точки входа</b>\n\n"
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

    text = (
        f"📁 <b>Файловый менеджер</b>\n\n"
        f"Чтобы загрузить новый файл - отправь его, он попадет "
        f"в открытую директорию заменой. Если файлов несколько, "
        f"пришли их архивом, он будет распакован."
    )

    await edit_photo_or_text(
        callback.message,
        text,
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

    libs = []
    try:
        content = await project_service.read_file(project_id, "/app/requirements.txt")
        if content:
            libs = [line.strip().split("==")[0].split(">=")[0].split("<=")[0]
                    for line in content.strip().split("\n") if line.strip() and not line.startswith("#")]
    except Exception:
        pass

    text = (
        f"📦 <b>Менеджер библиотек</b>\n\n"
        f"Тут находятся все твои библиотеки, можешь установить новые "
        f"или удалить текущие."
    )

    await edit_photo_or_text(
        callback.message,
        text,
        "library_manager",
        reply_markup=get_libs_keyboard(project_id, libs),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lib_add_"))
async def lib_add(callback: CallbackQuery, state: FSMContext):
    project_id = int(callback.data.replace("lib_add_", ""))
    await state.update_data(lib_project_id=project_id)

    await callback.message.edit_text(
        "📦 <b>Установка библиотеки</b>\n\n"
        "Отправь название библиотеки.\n"
        "Примеры: <code>aiogram</code>, <code>requests>=2.0</code>",
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
        await message.answer("❌ Проект не найден")
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
        f"{Emoji.CHECK} Библиотека <b>{lib}</b> добавлена.\n"
        f"Перезапустите бота для применения.",
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
