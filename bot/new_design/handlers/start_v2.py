"""
🏠 ГЛАВНЫЙ ЭКРАН - НОВАЯ ВЕРСИЯ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Современный главный экран с адаптивным контентом
"""

from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.new_design import texts_v2 as texts
from bot.new_design import keyboards_v2 as kb

router = Router()


@router.message(CommandStart())
async def cmd_start_new(
    message: Message,
    db_user,
    project_service,
    state: FSMContext
):
    """
    Команда /start - Адаптивный главный экран.
    
    Для новых пользователей: призыв к созданию первого проекта
    Для опытных: быстрый доступ к проектам
    """
    # Очищаем состояние
    await state.clear()
    
    # Получаем проекты пользователя
    projects = await project_service.get_user_projects(db_user.id)
    has_projects = len(projects) > 0
    
    # Генерируем персонализированное приветствие
    username = message.from_user.first_name or "друг"
    text = texts.home_screen(username, len(projects))
    
    # Отправляем с адаптивной клавиатурой
    await message.answer(
        text,
        reply_markup=kb.home_menu(has_projects=has_projects),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "home")
async def callback_home(
    callback: CallbackQuery,
    db_user,
    project_service
):
    """
    Возврат на главный экран.
    """
    projects = await project_service.get_user_projects(db_user.id)
    has_projects = len(projects) > 0
    
    username = callback.from_user.first_name or "друг"
    text = texts.home_screen(username, len(projects))
    
    try:
        await callback.message.edit_text(
            text,
            reply_markup=kb.home_menu(has_projects=has_projects),
            parse_mode="HTML"
        )
    except Exception:
        # Если сообщение не изменилось, просто отвечаем
        await callback.answer()
    
    await callback.answer()


@router.callback_query(F.data == "my_projects")
async def callback_my_projects(
    callback: CallbackQuery,
    db_user,
    project_service
):
    """
    Список проектов пользователя.
    """
    projects = await project_service.get_user_projects(db_user.id)
    
    if not projects:
        # Пустой список - предлагаем создать
        await callback.message.edit_text(
            texts.EMPTY_PROJECTS,
            reply_markup=kb.create_project_upload_method(),
            parse_mode="HTML"
        )
    else:
        # Показываем список с карточками
        text = texts.MY_PROJECTS_TITLE
        await callback.message.edit_text(
            text,
            reply_markup=kb.projects_list(projects, page=0),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("projects:page:"))
async def callback_projects_page(
    callback: CallbackQuery,
    db_user,
    project_service
):
    """
    Пагинация списка проектов.
    """
    page = int(callback.data.split(":")[-1])
    projects = await project_service.get_user_projects(db_user.id)
    
    text = texts.MY_PROJECTS_TITLE
    
    try:
        await callback.message.edit_text(
            text,
            reply_markup=kb.projects_list(projects, page=page),
            parse_mode="HTML"
        )
    except Exception:
        await callback.answer()
    
    await callback.answer()


@router.callback_query(F.data.startswith("proj:"))
async def callback_project_view(
    callback: CallbackQuery,
    db_user,
    project_service,
    session
):
    """
    Просмотр конкретного проекта.
    
    Format: proj:{project_id} или proj:{project_id}:{action}
    """
    parts = callback.data.split(":")
    project_id = int(parts[1])
    action = parts[2] if len(parts) > 2 else None
    
    # Получаем проект
    project = await project_service.get_project(project_id)
    
    if not project:
        await callback.answer(texts.ERROR_PROJECT_NOT_FOUND, show_alert=True)
        return
    
    # Проверяем доступ
    is_owner = project.user_id == db_user.id
    
    if not is_owner:
        # Проверяем, является ли пользователь совладельцем
        from bot.utils.access import check_project_access
        has_access = await check_project_access(project, db_user, session)
        if not has_access:
            await callback.answer(texts.ERROR_NO_ACCESS, show_alert=True)
            return
    
    # Обрабатываем действие если есть
    if action:
        await _handle_project_action(
            callback, project_id, action, project_service, db_user
        )
        return
    
    # Показываем панель управления
    monitoring = await project_service.get_monitoring(project_id)
    
    text = texts.project_control_panel(
        name=project.name,
        status=monitoring.get("status", project.status),
        stats=monitoring
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=kb.project_control(project_id, project.status, is_owner),
        parse_mode="HTML"
    )
    
    await callback.answer()


async def _handle_project_action(
    callback: CallbackQuery,
    project_id: int,
    action: str,
    project_service,
    db_user
):
    """
    Обработка действий над проектом.
    """
    if action == "start":
        success, msg = await project_service.start_project(project_id)
        icon = "✅" if success else "⚠️"
        
        if success:
            full_msg = texts.success_project_started(
                await _get_project_name(project_service, project_id)
            )
        else:
            full_msg = f"{icon} {msg}"
        
        await callback.answer(f"{icon} {msg}", show_alert=True)
        
        # Обновляем панель
        await callback_project_view(callback, db_user, project_service, None)
    
    elif action == "stop":
        success, msg = await project_service.stop_project(project_id)
        icon = "✅" if success else "⚠️"
        
        if success:
            full_msg = texts.success_project_stopped(
                await _get_project_name(project_service, project_id)
            )
        else:
            full_msg = f"{icon} {msg}"
        
        await callback.answer(f"{icon} {msg}", show_alert=True)
        
        # Обновляем панель
        await callback_project_view(callback, db_user, project_service, None)
    
    elif action == "restart":
        success, msg = await project_service.restart_project(project_id)
        icon = "✅" if success else "⚠️"
        await callback.answer(f"{icon} {msg}", show_alert=True)
        
        # Обновляем панель
        await callback_project_view(callback, db_user, project_service, None)
    
    elif action == "logs":
        await _show_project_logs(callback, project_id, project_service)
    
    elif action == "stats":
        await _show_project_stats(callback, project_id, project_service)
    
    elif action == "files":
        await _show_project_files(callback, project_id, project_service)
    
    elif action == "settings":
        await _show_project_settings(callback, project_id)
    
    elif action == "sharing":
        await _show_project_sharing(callback, project_id, db_user, project_service)
    
    elif action == "delete":
        await _confirm_project_delete(callback, project_id, project_service)


async def _show_project_logs(
    callback: CallbackQuery,
    project_id: int,
    project_service
):
    """
    Показать логи проекта.
    """
    logs = await project_service.get_logs(project_id, tail=100)
    
    # Форматируем логи
    from html import escape
    logs_escaped = escape(logs[:3500])  # Ограничение Telegram
    
    text = f"""{texts.PROJECT_LOGS_HEADER}

<code>{logs_escaped}</code>"""
    
    await callback.message.edit_text(
        text,
        reply_markup=kb.logs_actions(project_id),
        parse_mode="HTML"
    )
    await callback.answer()


async def _show_project_stats(
    callback: CallbackQuery,
    project_id: int,
    project_service
):
    """
    Показать статистику проекта.
    """
    monitoring = await project_service.get_monitoring(project_id)
    project = await project_service.get_project(project_id)
    
    # Создаём визуализацию статистики
    text = texts.project_card(
        name=project.name,
        status=monitoring.get("status", "stopped"),
        uptime=texts.format_uptime(0),  # TODO: реальное время
        memory=monitoring.get("ram", 0),
        cpu=monitoring.get("cpu", 0)
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=kb.stats_timerange(project_id, "24h"),
        parse_mode="HTML"
    )
    await callback.answer()


async def _show_project_files(
    callback: CallbackQuery,
    project_id: int,
    project_service
):
    """
    Показать файловый менеджер.
    """
    files = await project_service.list_files(project_id, "/app")
    
    text = texts.file_manager_header("/app", len(files))
    
    await callback.message.edit_text(
        text,
        reply_markup=kb.file_browser(project_id, files, "/app"),
        parse_mode="HTML"
    )
    await callback.answer()


async def _show_project_settings(
    callback: CallbackQuery,
    project_id: int
):
    """
    Показать настройки проекта.
    """
    text = texts.PROJECT_SETTINGS_MENU
    
    await callback.message.edit_text(
        text,
        reply_markup=kb.project_settings_menu(project_id),
        parse_mode="HTML"
    )
    await callback.answer()


async def _show_project_sharing(
    callback: CallbackQuery,
    project_id: int,
    db_user,
    project_service
):
    """
    Показать управление совладельцами.
    """
    from repositories.coowner import CoOwnerRepository
    from db.engine import async_session_factory
    
    project = await project_service.get_project(project_id)
    
    async with async_session_factory() as session:
        coowner_repo = CoOwnerRepository(session)
        coowners = await coowner_repo.get_by_project_id(project_id)
    
    text = texts.sharing_menu(project.name, len(coowners))
    
    await callback.message.edit_text(
        text,
        reply_markup=kb.sharing_menu(project_id, coowners),
        parse_mode="HTML"
    )
    await callback.answer()


async def _confirm_project_delete(
    callback: CallbackQuery,
    project_id: int,
    project_service
):
    """
    Подтверждение удаления проекта.
    """
    project = await project_service.get_project(project_id)
    
    text = f"""⚠️ <b>Удаление проекта</b>

Ты уверен что хочешь удалить <b>{project.name}</b>?

Все данные будут потеряны навсегда.
Это действие нельзя отменить."""
    
    await callback.message.edit_text(
        text,
        reply_markup=kb.confirm_action(
            action_callback=f"proj:{project_id}:delete:confirm",
            cancel_callback=f"proj:{project_id}"
        ),
        parse_mode="HTML"
    )
    await callback.answer()


async def _get_project_name(project_service, project_id: int) -> str:
    """Получить имя проекта."""
    project = await project_service.get_project(project_id)
    return project.name if project else "Проект"


@router.callback_query(F.data == "delete_message")
async def callback_delete_message(callback: CallbackQuery):
    """Удалить сообщение."""
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message):
    """
    Команда /help - Показать помощь.
    """
    await message.answer(
        texts.HELP_MENU,
        reply_markup=kb.help_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "help_menu")
async def callback_help_menu(callback: CallbackQuery):
    """
    Меню помощи.
    """
    await callback.message.edit_text(
        texts.HELP_MENU,
        reply_markup=kb.help_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "help:quick_start")
async def callback_help_quick_start(callback: CallbackQuery):
    """
    Быстрый старт.
    """
    await callback.message.edit_text(
        texts.QUICK_START_GUIDE,
        reply_markup=kb.back_button("help_menu"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def callback_noop(callback: CallbackQuery):
    """
    No-operation callback (для неактивных кнопок).
    """
    await callback.answer()
