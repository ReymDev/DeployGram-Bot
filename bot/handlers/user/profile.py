from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.config import settings
from bot.keyboards.user import get_settings_keyboard
from bot.keyboards.common import get_back_keyboard
from bot.utils.emojis import Emoji
from bot import texts

router = Router()


@router.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery, db_user, user_service, session):
    from services.referral import ReferralService
    from services.project import ProjectService
    ref_svc = ReferralService(session)
    referral_link = await ref_svc.get_referral_link(db_user.telegram_id)
    max_projects = await user_service.get_max_projects(db_user.tariff)
    project_svc = ProjectService(session)
    projects = await project_svc.get_user_projects(db_user.id)
    projects_count = len(projects)

    # Используем новую функцию из texts.py
    text = texts.profile_text(
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
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "settings")
async def settings_page(callback: CallbackQuery, user_service, db_user):
    s = await user_service.get_settings(db_user.id)
    if s is None:
        await callback.answer(texts.SETTINGS_NOT_FOUND, show_alert=True)
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
        texts.notification_settings_text(),
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_"))
async def toggle_notification(callback: CallbackQuery, user_service, db_user):
    setting = callback.data.replace("toggle_", "")
    valid_settings = [
        "notify_container_stopped", "notify_container_started", "notify_error",
        "notify_high_cpu", "notify_high_ram", "notify_low_disk",
        "notify_backup_created", "notify_update_done",
    ]
    if setting not in valid_settings:
        await callback.answer(texts.SETTINGS_UNKNOWN, show_alert=True)
        return

    await user_service.toggle_setting(db_user.id, setting)
    await callback.answer(texts.SETTINGS_CHANGED)

    s = await user_service.get_settings(db_user.id)
    if s:
        from bot.keyboards.user import get_settings_keyboard
        keyboard = get_settings_keyboard(
            s.notify_container_stopped, s.notify_container_started,
            s.notify_error, s.notify_high_cpu, s.notify_high_ram,
            s.notify_low_disk, s.notify_backup_created, s.notify_update_done,
        )
        await callback.message.edit_reply_markup(reply_markup=keyboard)
