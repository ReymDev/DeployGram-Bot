from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.common import get_back_keyboard
from bot.utils.emojis import Emoji

router = Router()


@router.callback_query(F.data == "promo_activate")
async def promo_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        f"{Emoji.GIFT} <b>Активация промокода</b>\n\n"
        f"Введите код:",
        reply_markup=get_back_keyboard("main_menu"),
    )
    await state.set_state("promo_waiting_code")
    await callback.answer()


@router.message(F.text, state=None)
async def promo_code_received(message: Message, state: FSMContext):
    from aiogram.fsm.state import State, StatesGroup
    current_state = await state.get_state()
    if current_state != "promo_waiting_code":
        return

    code = message.text.strip()
    from db.engine import async_session_factory
    from services.promo import PromoService

    async with async_session_factory() as session:
        promo_svc = PromoService(session)
        success, msg, promo = await promo_svc.activate_promo(code)

    await state.clear()
    if success:
        from bot.config import settings
        if promo and promo.reward_type == "tariff":
            from db.engine import async_session_factory
            from services.user import UserService
            async with async_session_factory() as session:
                user_svc = UserService(session)
                await user_svc.set_tariff(message.from_user.id, "premium")

        await message.answer(
            f"{Emoji.PARTY} {msg}",
            reply_markup=get_back_keyboard("main_menu"),
        )
    else:
        await message.answer(
            f"{Emoji.CROSS} {msg}",
            reply_markup=get_back_keyboard("main_menu"),
        )
