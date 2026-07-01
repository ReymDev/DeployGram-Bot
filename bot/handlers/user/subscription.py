from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.user import get_subscription_keyboard, get_buy_subscription_keyboard
from bot.keyboards.common import get_back_keyboard
from bot.utils.media import edit_photo_or_text
from bot import texts

router = Router()


@router.callback_query(F.data == "subscription")
async def subscription_menu(callback: CallbackQuery, db_user, project_service):
    is_premium = db_user.tariff == "premium"
    
    # Получаем количество проектов пользователя
    projects = await project_service.get_user_projects(db_user.id)
    projects_count = len(projects)
    max_projects = 5 if is_premium else 1
    
    text = texts.subscription_text(is_premium, projects_count, max_projects)

    await edit_photo_or_text(
        callback.message,
        text,
        "subscription",
        reply_markup=get_subscription_keyboard(is_premium),
    )
    await callback.answer()


@router.callback_query(F.data == "subscription_info")
async def subscription_info(callback: CallbackQuery):
    text = texts.subscription_info_text()

    await edit_photo_or_text(
        callback.message,
        text,
        "premium_info",
        reply_markup=get_back_keyboard("subscription"),
    )
    await callback.answer()


@router.callback_query(F.data == "subscription_buy")
async def subscription_buy(callback: CallbackQuery):
    text = texts.SUBSCRIPTION_BUY_TEXT

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
        await callback.answer(texts.SUBSCRIPTION_PLAN_UNKNOWN, show_alert=True)
        return

    text = texts.subscription_buy_plan_text(plan['label'], plan['price'])

    await edit_photo_or_text(
        callback.message,
        text,
        "buy_subscription",
        reply_markup=get_back_keyboard("subscription_buy"),
        parse_mode="HTML"
    )
    await callback.answer()
