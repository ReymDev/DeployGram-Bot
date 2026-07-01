from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.utils.emojis import Emoji
from bot.utils.media import edit_photo_or_text

router = Router()


@router.callback_query(F.data == "referrals")
async def referrals_menu(callback: CallbackQuery, db_user, session):
    from services.referral import ReferralService
    ref_svc = ReferralService(session)
    link = await ref_svc.get_referral_link(db_user.telegram_id)
    count = await ref_svc.get_referrals_count(db_user.id)

    text = (
        f"{Emoji.LINK} <b>Реферальная система</b>\n\n"
        f"🔗 Ваша ссылка:\n<code>{link}</code>\n\n"
        f"👥 Приглашено: <b>{count}</b>\n\n"
        f"Поделитесь ссылкой с друзьями!"
    )

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="◁ Меню", callback_data="main_menu"),
    )

    await edit_photo_or_text(
        callback.message,
        text,
        "control_panel",
        reply_markup=builder.as_markup()
    )
    await callback.answer()
