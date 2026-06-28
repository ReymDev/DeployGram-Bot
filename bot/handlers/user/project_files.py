from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.utils.emojis import Emoji
from bot import texts

router = Router()


class FileUploadStates(StatesGroup):
    waiting_file = State()


async def _check_file_access(callback: CallbackQuery, project_service, db_user, project_id: int, session=None, permission: str = "can_edit_files"):
    """Check if user has access to project files (owner or coowner with permission)."""
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return None
    
    # Owner always has access
    if project.user_id == db_user.id:
        return project
    
    # Check coowner permission if session provided
    if session is not None:
        from bot.utils.access import check_permission
        has_perm, _ = await check_permission(project, db_user, session, permission)
        if has_perm:
            return project
    
    await callback.answer("⛔ У вас нет прав на редактирование файлов", show_alert=True)
    return None


@router.callback_query(F.data.startswith("bot_files_"))
async def bot_files_redirect(callback: CallbackQuery, project_service, db_user, session):
    """Редирект с bot_files_ на files_main_menu_."""
    project_id = int(callback.data.split("_")[-1])
    # Перенаправляем на новый хендлер
    callback.data = f"files_main_menu_{project_id}"
    await files_main_menu(callback, project_service, db_user, session)


@router.callback_query(F.data.startswith("files_main_menu_"))
async def files_main_menu(callback: CallbackQuery, project_service, db_user, session):
    """Главное меню файлового менеджера - выбор режима."""
    project_id = int(callback.data.split("_")[-1])
    # For main menu, only need basic access
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return
    
    # Check basic access (owner or coowner)
    from bot.utils.access import check_project_access
    has_access = await check_project_access(project, db_user, session)
    if not has_access:
        await callback.answer(texts.ERROR_NO_ACCESS, show_alert=True)
        return

    from bot.keyboards.user import get_files_main_menu_keyboard
    
    text = f"""📁 <b>Файловый менеджер</b>

<b>Проект:</b> {project.name}

Выбери действие:"""

    await callback.message.edit_text(
        text,
        reply_markup=get_files_main_menu_keyboard(project_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("files_browse_"))
async def files_browse(callback: CallbackQuery, project_service, db_user, session):
    """Режим просмотра файлов."""
    project_id = int(callback.data.split("_")[-1])
    # For browsing, only need basic access - view permission not required
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return
    
    # Check basic access (owner or coowner)
    from bot.utils.access import check_project_access
    has_access = await check_project_access(project, db_user, session)
    if not has_access:
        await callback.answer(texts.ERROR_NO_ACCESS, show_alert=True)
        return

    from bot.keyboards.user import get_file_browser_keyboard
    files = await project_service.list_files(project_id, "/app")
    
    # Логируем для отладки
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"[FILES_BROWSE] Project: {project.name}, Files count: {len(files)}, Files: {files}")

    text = f"""📂 <b>Просмотр файлов</b>

<b>Путь:</b> <code>/app</code>

Нажми на файл для действий или на папку чтобы открыть:"""

    await callback.message.edit_text(
        text,
        reply_markup=get_file_browser_keyboard(project_id, files, "/app"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("files_upload_"))
async def files_upload_mode(callback: CallbackQuery, project_service, db_user, session):
    """Режим загрузки файлов."""
    project_id = int(callback.data.split("_")[-1])
    # Uploading requires edit_files permission
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return
    
    # Check edit permission
    from bot.utils.access import check_permission
    has_perm, _ = await check_permission(project, db_user, session, "can_edit_files")
    if not has_perm:
        await callback.answer("⛔ У вас нет прав на редактирование файлов", show_alert=True)
        return

    from bot.keyboards.user import get_file_upload_browser_keyboard
    files = await project_service.list_files(project_id, "/app")

    text = f"""📤 <b>Загрузка файлов</b>

<b>Путь:</b> <code>/app</code>

Выбери папку или нажми "📤 Загрузить сюда":"""

    await callback.message.edit_text(
        text,
        reply_markup=get_file_upload_browser_keyboard(project_id, files, "/app"),
        parse_mode="HTML"
    )
    await callback.answer()


def _parse_file_callback(data: str, prefix: str) -> tuple[int, str]:
    """Парсит callback с project_id и путем."""
    remaining = data.replace(prefix + "_", "", 1)
    parts = remaining.split("_", 1)
    project_id = int(parts[0])
    file_path = parts[1] if len(parts) > 1 else "/app"
    return project_id, file_path


@router.callback_query(F.data.startswith("fbrowse_nav_"))
async def file_browse_nav(callback: CallbackQuery, project_service, db_user, session):
    """Навигация по папкам в режиме просмотра."""
    project_id, path = _parse_file_callback(callback.data, "fbrowse_nav")
    # For browsing, only need basic access
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return
    
    # Check basic access (owner or coowner)
    from bot.utils.access import check_project_access
    has_access = await check_project_access(project, db_user, session)
    if not has_access:
        await callback.answer(texts.ERROR_NO_ACCESS, show_alert=True)
        return

    from bot.keyboards.user import get_file_browser_keyboard
    files = await project_service.list_files(project_id, path)

    text = f"""📂 <b>Просмотр файлов</b>

<b>Путь:</b> <code>{path}</code>

Нажми на файл для действий или на папку чтобы открыть:"""

    await callback.message.edit_text(
        text,
        reply_markup=get_file_browser_keyboard(project_id, files, path),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("fupload_nav_"))
async def file_upload_nav(callback: CallbackQuery, project_service, db_user, session):
    """Навигация по папкам в режиме загрузки."""
    project_id, path = _parse_file_callback(callback.data, "fupload_nav")
    # For upload navigation, check edit permission
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return
    
    # Check edit permission
    from bot.utils.access import check_permission
    has_perm, _ = await check_permission(project, db_user, session, "can_edit_files")
    if not has_perm:
        await callback.answer("⛔ У вас нет прав на редактирование файлов", show_alert=True)
        return

    from bot.keyboards.user import get_file_upload_browser_keyboard
    files = await project_service.list_files(project_id, path)

    text = f"""📤 <b>Загрузка файлов</b>

<b>Путь:</b> <code>{path}</code>

Выбери папку или нажми "📤 Загрузить сюда":"""

    await callback.message.edit_text(
        text,
        reply_markup=get_file_upload_browser_keyboard(project_id, files, path),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("file_action_"))
async def file_action_menu(callback: CallbackQuery, project_service, db_user, session):
    """Меню действий с файлом."""
    project_id, file_path = _parse_file_callback(callback.data, "file_action")
    # For action menu, only need basic access
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return
    
    # Check basic access (owner or coowner)
    from bot.utils.access import check_project_access
    has_access = await check_project_access(project, db_user, session)
    if not has_access:
        await callback.answer(texts.ERROR_NO_ACCESS, show_alert=True)
        return

    from bot.keyboards.user import get_file_action_keyboard
    import os
    filename = os.path.basename(file_path)
    
    text = f"""📄 <b>{filename}</b>

<b>Путь:</b> <code>{file_path}</code>

Выбери действие:"""

    await callback.message.edit_text(
        text,
        reply_markup=get_file_action_keyboard(project_id, file_path),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("file_download_"))
async def file_download(callback: CallbackQuery, project_service, db_user, session):
    """Скачать файл."""
    project_id, file_path = _parse_file_callback(callback.data, "file_download")
    # Downloading only requires basic access
    project = await project_service.get_project(project_id)
    if project is None:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return
    
    # Check basic access (owner or coowner)
    from bot.utils.access import check_project_access
    has_access = await check_project_access(project, db_user, session)
    if not has_access:
        await callback.answer(texts.ERROR_NO_ACCESS, show_alert=True)
        return

    content = await project_service.read_file(project_id, file_path)
    if not content:
        await callback.answer(texts.BOT_FILE_NOT_FOUND_TEXT, show_alert=True)
        return

    from aiogram.types import BufferedInputFile
    import os
    file_bytes = content.encode("utf-8")
    filename = os.path.basename(file_path)
    file = BufferedInputFile(file_bytes, filename=filename)

    await callback.message.answer_document(
        file,
        caption=f"📄 <code>{file_path}</code>",
        parse_mode="HTML"
    )
    await callback.answer("✅ Файл отправлен")


@router.callback_query(F.data.startswith("file_delete_"))
async def file_delete(callback: CallbackQuery, project_service, db_user, session):
    """Подтверждение удаления файла."""
    project_id, file_path = _parse_file_callback(callback.data, "file_delete")
    # Deleting requires edit_files permission
    project = await _check_file_access(callback, project_service, db_user, project_id, session, "can_edit_files")
    if project is None:
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    import os
    filename = os.path.basename(file_path)
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Да, удалить",
            callback_data=f"file_del_confirm_{project_id}_{file_path}",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data=f"file_action_{project_id}_{file_path}",
        ),
    )

    text = f"""🗑️ <b>Удалить файл?</b>

<b>Файл:</b> <code>{filename}</code>
<b>Путь:</b> <code>{file_path}</code>

⚠️ <i>Это действие нельзя отменить!</i>"""

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("file_del_confirm_"))
async def file_delete_confirm(callback: CallbackQuery, project_service, db_user, session):
    """Удалить файл."""
    project_id, file_path = _parse_file_callback(callback.data, "file_del_confirm")
    # Deleting requires edit_files permission
    project = await _check_file_access(callback, project_service, db_user, project_id, session, "can_edit_files")
    if project is None:
        return

    success = await project_service.delete_file(project_id, file_path)
    if success:
        await callback.answer("✅ Файл удалён", show_alert=True)
        
        # Возвращаемся в папку где был файл
        parent = "/".join(file_path.strip("/").split("/")[:-1]) or "/app"
        files = await project_service.list_files(project_id, parent)
        from bot.keyboards.user import get_file_browser_keyboard
        
        text = f"""📂 <b>Просмотр файлов</b>

<b>Путь:</b> <code>{parent}</code>

Нажми на файл для действий или на папку чтобы открыть:"""
        
        await callback.message.edit_text(
            text,
            reply_markup=get_file_browser_keyboard(project_id, files, parent),
            parse_mode="HTML"
        )
    else:
        await callback.answer(texts.BOT_FILE_DELETE_ERROR_TEXT, show_alert=True)


@router.callback_query(F.data.startswith("upload_here_"))
async def upload_here(callback: CallbackQuery, state: FSMContext, project_service, db_user, session):
    """Начать загрузку файла в текущую директорию."""
    project_id, path = _parse_file_callback(callback.data, "upload_here")
    # Uploading requires edit_files permission
    project = await _check_file_access(callback, project_service, db_user, project_id, session, "can_edit_files")
    if project is None:
        return

    await state.set_state(FileUploadStates.waiting_file)
    await state.update_data(project_id=project_id, upload_path=path)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data=f"files_upload_{project_id}",
        ),
    )

    text = f"""📤 <b>Загрузка файла</b>

<b>Загрузка в:</b> <code>{path}</code>

Отправь файл или несколько файлов:"""

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(FileUploadStates.waiting_file, F.document)
async def file_received(message: Message, state: FSMContext, project_service, db_user):
    """Обработка загруженного файла."""
    data = await state.get_data()
    project_id = data.get("project_id")
    upload_path = data.get("upload_path", "/app")
    
    # Скачиваем файл
    file = await message.bot.get_file(message.document.file_id)
    file_bytes = await message.bot.download_file(file.file_path)
    
    # Сохраняем файл
    filename = message.document.file_name
    full_path = f"{upload_path.rstrip('/')}/{filename}"
    
    content = file_bytes.read().decode("utf-8", errors="ignore")
    success = await project_service.write_file(project_id, full_path, content)
    
    if success:
        await message.answer(
            f"✅ <b>Файл загружен</b>\n\n<code>{full_path}</code>",
            parse_mode="HTML"
        )
    else:
        await message.answer("❌ Ошибка загрузки файла")


@router.message(FileUploadStates.waiting_file)
async def wrong_file_type(message: Message):
    """Неправильный тип сообщения."""
    await message.answer(
        "❌ Пожалуйста, отправь файл документом.\n\nДля отмены нажми кнопку ниже."
    )
