from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.utils.emojis import Emoji, EmojiID
from bot.keyboards.common import get_back_keyboard
from bot.utils.media import edit_photo_or_text
from bot import texts

router = Router()


class CoOwnerStates(StatesGroup):
    waiting_id = State()


@router.callback_query(F.data.startswith("project_coowners_"))
async def coowners_menu(callback: CallbackQuery, project_service, db_user, session):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return

    from repositories.coowner import CoOwnerRepository
    coowner_repo = CoOwnerRepository(session)
    coowners = await coowner_repo.get_by_project_id(project_id)

    from bot.keyboards.user import get_coowners_keyboard
    await edit_photo_or_text(
        callback.message,
        texts.bot_coowners_text(project.name),
        "bot_control",
        reply_markup=get_coowners_keyboard(project_id, coowners),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("coowner_add_"))
async def coowner_add(callback: CallbackQuery, state: FSMContext, db_user):
    project_id = int(callback.data.split("_")[-1])
    await state.update_data(coowner_project_id=project_id)
    await edit_photo_or_text(
        callback.message,
        texts.COOWNER_ENTER_ID,
        "bot_control",
        parse_mode="HTML"
    )
    await state.set_state(CoOwnerStates.waiting_id)
    await callback.answer()


@router.callback_query(F.data.startswith("coowner_remove_"))
async def coowner_remove(callback: CallbackQuery, project_service, db_user, session):
    parts = callback.data.split("_")
    project_id = int(parts[2])
    coowner_id = int(parts[3])

    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer(texts.ERROR_NO_ACCESS, show_alert=True)
        return

    from repositories.coowner import CoOwnerRepository
    coowner_repo = CoOwnerRepository(session)
    await coowner_repo.delete(coowner_id)

    await callback.answer(texts.COOWNER_REMOVED, show_alert=True)

    coowners = await coowner_repo.get_by_project_id(project_id)
    from bot.keyboards.user import get_coowners_keyboard
    await edit_photo_or_text(
        callback.message,
        texts.bot_coowners_text(project.name),
        "bot_control",
        reply_markup=get_coowners_keyboard(project_id, coowners),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("coowner_edit_"))
async def coowner_edit(callback: CallbackQuery, project_service, db_user, session):
    """Редактирование разрешений совладельца."""
    parts = callback.data.split("_")
    project_id = int(parts[2])
    coowner_id = int(parts[3])

    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer(texts.ERROR_NO_ACCESS, show_alert=True)
        return

    from repositories.coowner import CoOwnerRepository
    coowner_repo = CoOwnerRepository(session)
    coowner = await coowner_repo.get_by_id(coowner_id)
    
    if coowner is None or coowner.project_id != project_id:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return

    from bot.keyboards.user import get_coowner_permissions_keyboard
    await edit_photo_or_text(
        callback.message,
        texts.coowner_permissions_text(coowner.user_id),
        "bot_control",
        reply_markup=get_coowner_permissions_keyboard(project_id, coowner_id, coowner),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("coowner_perm_"))
async def coowner_toggle_permission(callback: CallbackQuery, project_service, db_user, session):
    """Переключение разрешения совладельца."""
    parts = callback.data.split("_")
    project_id = int(parts[2])
    coowner_id = int(parts[3])
    permission = "_".join(parts[4:])  # can_start_stop, can_view_logs, etc.

    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer(texts.ERROR_NO_ACCESS, show_alert=True)
        return

    from repositories.coowner import CoOwnerRepository
    coowner_repo = CoOwnerRepository(session)
    coowner = await coowner_repo.get_by_id(coowner_id)
    
    if coowner is None or coowner.project_id != project_id:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return

    # Переключаем разрешение
    current_value = getattr(coowner, permission, False)
    await coowner_repo.update(coowner_id, **{permission: not current_value})
    
    # Обновляем объект
    coowner = await coowner_repo.get_by_id(coowner_id)
    
    await callback.answer(texts.SETTINGS_CHANGED)

    # Обновляем клавиатуру
    from bot.keyboards.user import get_coowner_permissions_keyboard
    await callback.message.edit_reply_markup(
        reply_markup=get_coowner_permissions_keyboard(project_id, coowner_id, coowner)
    )


@router.message(F.text, CoOwnerStates.waiting_id)
async def coowner_id_received(message: Message, state: FSMContext, session, db_user):
    data = await state.get_data()
    project_id = data.get("coowner_project_id")

    try:
        target_telegram_id = int(message.text.strip())
    except ValueError:
        await message.answer(texts.COOWNER_INVALID_ID, parse_mode="HTML")
        return

    if target_telegram_id == db_user.telegram_id:
        await message.answer(texts.COOWNER_SELF_ADD, parse_mode="HTML")
        return

    from repositories.user import UserRepository
    user_repo = UserRepository(session)
    target_user = await user_repo.get_by_telegram_id(target_telegram_id)

    if target_user is None:
        await message.answer(texts.COOWNER_USER_NOT_FOUND, parse_mode="HTML")
        return

    from repositories.coowner import CoOwnerRepository
    coowner_repo = CoOwnerRepository(session)
    existing = await coowner_repo.get_by_user_and_project(target_user.id, project_id)
    if existing:
        await message.answer(texts.COOWNER_ALREADY_EXISTS, parse_mode="HTML")
        return

    await coowner_repo.create(
        project_id=project_id,
        user_id=target_user.id,
        role="developer",
    )

    await state.clear()
    await message.answer(
        texts.coowner_added_text(target_user.username or str(target_telegram_id)),
        reply_markup=get_back_keyboard(f"project_coowners_{project_id}"),
        parse_mode="HTML"
    )
