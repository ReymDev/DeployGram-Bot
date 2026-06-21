from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.user import get_subscription_keyboard, get_buy_subscription_keyboard
from bot.keyboards.common import get_back_keyboard
from bot.utils.media import edit_photo_or_text
from bot.texts import subscription_text, subscription_info_text

router = Router()


@router.callback_query(F.data == "subscription")
async def subscription_menu(callback: CallbackQuery, db_user):
    is_premium = db_user.tariff == "premium"
    text = subscription_text(is_premium)

    await edit_photo_or_text(
        callback.message,
        text,
        "subscription",
        reply_markup=get_subscription_keyboard(is_premium),
    )
    await callback.answer()


@router.callback_query(F.data == "subscription_info")
async def subscription_info(callback: CallbackQuery):
    text = subscription_info_text()

    await edit_photo_or_text(
        callback.message,
        text,
        "premium_info",
        reply_markup=get_back_keyboard("subscription"),
    )
    await callback.answer()


@router.callback_query(F.data == "subscription_buy")
async def subscription_buy(callback: CallbackQuery):
    text = (
        f"💳 <b>Покупка/продление подписки</b>\n\n"
        f"На какой срок ты хочешь приобрести подписку?"
    )

    await edit_photo_or_text(
        callback.message,
        text,
        "buy_subscription",
        reply_markup=get_buy_subscription_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_"))
async def buy_selected(callback: CallbackQuery, db_user):
    from models.subscription import get_premium_prices
    plan_key = callback.data.replace("buy_", "")
    prices = get_premium_prices()
    plan = prices.get(plan_key)

    if not plan:
        await callback.answer("Неизвестный план", show_alert=True)
        return

    text = (
        f"💳 <b>Покупка подписки</b>\n\n"
        f"Ты выбрал: <b>Premium {plan['label']}</b>\n"
        f"Цена: <b>{plan['price']}₽</b>\n\n"
        f"Для оплаты свяжитесь с администратором."
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard("subscription_buy"),
    )
    await callback.answer()
