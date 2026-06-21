from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from bot.config import settings
from bot.keyboards.common import get_welcome_keyboard, get_control_panel_keyboard
from bot.utils.emojis import Emoji
from bot.utils.media import send_photo_or_text, edit_photo_or_text

router = Router()

WELCOME_TEXT = (
    f"{Emoji.SMILE} <b>Добро пожаловать!</b>\n\n"
    f"Привет, это <b>DeployGram</b> - дом для твоих ботов!\n\n"
    f"Здесь ты можешь бесплатно захостить свой код или запустить "
    f"готовый пресет всего за пару кликов.\n\n"
    f"Начиная работу, ты принимаешь наши <a href=\"#\">условия</a> "
    f"и <a href=\"#\">политику</a>."
)

CONTROL_PANEL_TEXT = (
    f"📋 <b>Панель управления</b>\n\n"
    f"Нажми на кнопку с названием бота, чтобы управлять им."
)


@router.message(CommandStart())
async def cmd_start(message: Message, session, db_user, user_service):
    args = message.text.split()
    referral_code = args[1] if len(args) > 1 else None

    if referral_code and referral_code.isdigit():
        referrer_id = int(referral_code)
        if referrer_id != db_user.telegram_id:
            from services.referral import ReferralService
            ref_svc = ReferralService(session)
            await ref_svc.process_referral(referrer_id, db_user.telegram_id)

    await send_photo_or_text(
        message,
        WELCOME_TEXT,
        "welcome",
        reply_markup=get_welcome_keyboard(),
    )


@router.callback_query(F.data == "control_panel")
async def control_panel(callback: CallbackQuery, db_user, project_service):
    from bot.keyboards.user import get_bot_list_keyboard
    projects = await project_service.get_user_projects(db_user.id)

    if projects:
        await edit_photo_or_text(
            callback.message,
            CONTROL_PANEL_TEXT,
            "control_panel",
            reply_markup=get_bot_list_keyboard(projects),
        )
    else:
        await edit_photo_or_text(
            callback.message,
            CONTROL_PANEL_TEXT,
            "control_panel",
            reply_markup=get_control_panel_keyboard(),
        )
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery, db_user, project_service):
    from bot.keyboards.user import get_bot_list_keyboard
    projects = await project_service.get_user_projects(db_user.id)

    if projects:
        await edit_photo_or_text(
            callback.message,
            CONTROL_PANEL_TEXT,
            "control_panel",
            reply_markup=get_bot_list_keyboard(projects),
        )
    else:
        await edit_photo_or_text(
            callback.message,
            CONTROL_PANEL_TEXT,
            "control_panel",
            reply_markup=get_control_panel_keyboard(),
        )
    await callback.answer()
