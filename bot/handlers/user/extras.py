from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.common import get_back_keyboard
from bot.utils.media import edit_photo_or_text

router = Router()


# ─── PROMO ACTIVATE ───

class PromoStates(StatesGroup):
    waiting_code = State()


@router.callback_query(F.data == "promo_activate")
async def promo_menu(callback: CallbackQuery, state: FSMContext):
    await edit_photo_or_text(
        callback.message,
        "<b>🎁 Активация промокода</b>\n\n<blockquote>Отправь код сообщением — мы активируем награду автоматически.</blockquote>",
        "control_panel",
        reply_markup=get_back_keyboard("main_menu"),
    )
    await state.set_state(PromoStates.waiting_code)
    await callback.answer()


@router.message(F.text, PromoStates.waiting_code)
async def promo_code_received(message: Message, state: FSMContext, db_user, session):
    code = message.text.strip()
    from services.promo import PromoService

    promo_svc = PromoService(session)
    success, msg, promo = await promo_svc.activate_promo(code)

    await state.clear()
    if success:
        if promo:
            from services.user import UserService
            user_svc = UserService(session)
            if promo.reward_type == "tariff":
                await user_svc.set_tariff(db_user.id, "premium")
            elif promo.reward_type == "balance":
                try:
                    amount = float(promo.reward_value)
                    await user_svc.update_balance(db_user.id, amount)
                except (ValueError, TypeError):
                    pass

        from html import escape
        await message.answer(
            f"🎉 {escape(str(msg))}",
            reply_markup=get_back_keyboard("main_menu"),
        )
    else:
        from html import escape
        await message.answer(
            f"❌ {escape(str(msg))}",
            reply_markup=get_back_keyboard("main_menu"),
        )


# ─── REFERRALS ───

@router.callback_query(F.data == "referrals")
async def referrals_menu(callback: CallbackQuery, db_user, session):
    from services.referral import ReferralService
    ref_svc = ReferralService(session)
    link = await ref_svc.get_referral_link(db_user.telegram_id)
    count = await ref_svc.get_referrals_count(db_user.id)

    text = (
        f"🔗 <b>Реферальная система</b>\n\n"
        f"🔗 Твоя ссылка:\n<code>{link}</code>\n\n"
        f"👥 Приглашено: <b>{count}</b>\n\n"
        f"Поделись ссылкой с друзьями!"
    )

    await edit_photo_or_text(
        callback.message,
        text,
        "control_panel",
        reply_markup=get_back_keyboard("main_menu"),
    )
    await callback.answer()
