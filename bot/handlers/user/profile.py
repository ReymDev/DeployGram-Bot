from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.config import settings
from bot.keyboards.user import get_settings_keyboard, get_back_keyboard
from bot.utils.text import profile_text
from bot.utils.emojis import Emoji

router = Router()


@router.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery, db_user, user_service, session):
    from services.referral import ReferralService
    ref_svc = ReferralService(session)
    referral_link = await ref_svc.get_referral_link(db_user.telegram_id)
    max_projects = await user_service.get_max_projects(db_user.tariff)
    projects = await user_service.get_user_by_id(db_user.id)
    projects_count = len(projects.projects) if projects else 0

    text = profile_text(
        username=db_user.username or str(db_user.telegram_id),
        tariff=db_user.tariff,
        projects_count=projects_count,
        max_projects=max_projects,
        balance=db_user.balance,
        referral_link=referral_link,
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard("main_menu"),
    )
    await callback.answer()


@router.callback_query(F.data == "settings")
async def settings_page(callback: CallbackQuery, user_service):
    s = await user_service.get_settings(callback.from_user.id)
    if s is None:
        await callback.answer("Настройки не найдены", show_alert=True)
        return

    keyboard = get_settings_keyboard(
        s.notify_container_stopped,
        s.notify_container_started,
        s.notify_error,
        s.notify_high_cpu,
        s.notify_high_ram,
        s.notify_low_disk,
        s.notify_backup_created,
        s.notify_update_done,
    )

    await callback.message.edit_text(
        f"{Emoji.NOTIF} <b>Настройки уведомлений</b>",
        reply_markup=keyboard,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_"))
async def toggle_notification(callback: CallbackQuery, user_service):
    setting = callback.data.replace("toggle_", "")
    valid_settings = [
        "notify_container_stopped", "notify_container_started", "notify_error",
        "notify_high_cpu", "notify_high_ram", "notify_low_disk",
        "notify_backup_created", "notify_update_done",
    ]
    if setting not in valid_settings:
        await callback.answer("Неизвестная настройка", show_alert=True)
        return

    await user_service.toggle_setting(callback.from_user.id, setting)
    await callback.answer("Настройка изменена")

    s = await user_service.get_settings(callback.from_user.id)
    if s:
        from bot.keyboards.user import get_settings_keyboard
        keyboard = get_settings_keyboard(
            s.notify_container_stopped, s.notify_container_started,
            s.notify_error, s.notify_high_cpu, s.notify_high_ram,
            s.notify_low_disk, s.notify_backup_created, s.notify_update_done,
        )
        await callback.message.edit_reply_markup(reply_markup=keyboard)
