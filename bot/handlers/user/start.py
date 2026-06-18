from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from bot.config import settings
from bot.keyboards.common import get_main_menu_keyboard
from bot.utils.text import start_text
from services.referral import ReferralService

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session, db_user, user_service):
    args = message.text.split()
    referral_code = args[1] if len(args) > 1 else None

    if referral_code and referral_code.isdigit():
        referrer_id = int(referral_code)
        if referrer_id != db_user.telegram_id:
            ref_svc = ReferralService(session)
            await ref_svc.process_referral(referrer_id, db_user.telegram_id)

    await message.answer(
        start_text(db_user.username or "пользователь"),
        reply_markup=get_main_menu_keyboard(),
    )


@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery, db_user):
    from bot.keyboards.common import get_main_menu_keyboard
    await callback.message.edit_text(
        start_text(db_user.username or "пользователь"),
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()
