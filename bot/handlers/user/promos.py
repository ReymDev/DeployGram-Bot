from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.common import get_back_keyboard
from bot.utils.emojis import Emoji

router = Router()


class PromoStates(StatesGroup):
    waiting_code = State()


@router.callback_query(F.data == "promo_activate")
async def promo_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        f"{Emoji.GIFT} <b>Активация промокода</b>\n\n"
        f"Введите код:",
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
        if promo and promo.reward_type == "tariff":
            from services.user import UserService
            user_svc = UserService(session)
            await user_svc.set_tariff(db_user.id, "premium")

        await message.answer(
            f"{Emoji.PARTY} {msg}",
            reply_markup=get_back_keyboard("main_menu"),
        )
    else:
        await message.answer(
            f"{Emoji.CROSS} {msg}",
            reply_markup=get_back_keyboard("main_menu"),
        )
