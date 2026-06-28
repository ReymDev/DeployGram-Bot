from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from bot.config import settings
from bot.keyboards.common import get_welcome_keyboard, get_control_panel_keyboard
from bot.utils.emojis import Emoji
from bot.utils.media import send_photo_or_text, edit_photo_or_text
from bot import texts

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session, db_user, user_service, project_service):
    args = message.text.split()
    referral_code = args[1] if len(args) > 1 else None

    if referral_code and referral_code.isdigit():
        referrer_id = int(referral_code)
        if referrer_id != db_user.telegram_id:
            from services.referral import ReferralService
            ref_svc = ReferralService(session)
            await ref_svc.process_referral(referrer_id, db_user.telegram_id)

    # Получаем количество проектов для персонализации приветствия
    projects = await project_service.get_user_projects(db_user.id)
    
    await send_photo_or_text(
        message,
        texts.welcome_text(
            message.from_user.first_name or "друг",
            len(projects)
        ),
        "welcome",
        reply_markup=get_welcome_keyboard(),
    )


@router.callback_query(F.data == "control_panel")
async def control_panel(callback: CallbackQuery, db_user, project_service):
    from bot.keyboards.user import get_bot_list_keyboard
    projects_with_flags = await project_service.get_all_user_projects(db_user.id)

    if projects_with_flags:
        await edit_photo_or_text(
            callback.message,
            texts.CONTROL_PANEL_TEXT,
            "control_panel",
            reply_markup=get_bot_list_keyboard(projects_with_flags),
        )
    else:
        # Если проектов нет - показываем дружелюбное сообщение
        await edit_photo_or_text(
            callback.message,
            texts.EMPTY_PROJECTS,
            "control_panel",
            reply_markup=get_control_panel_keyboard(),
        )
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery, db_user, project_service):
    # Получаем количество проектов для персонализации приветствия
    projects = await project_service.get_user_projects(db_user.id)
    
    await edit_photo_or_text(
        callback.message,
        texts.welcome_text(
            callback.from_user.first_name or "друг",
            len(projects)
        ),
        "welcome",
        reply_markup=get_welcome_keyboard(),
    )
    await callback.answer()
