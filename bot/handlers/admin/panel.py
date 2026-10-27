from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from html import escape

from bot.config import settings
from bot.keyboards.admin import (
    get_admin_keyboard,
    get_admin_users_keyboard,
    get_admin_user_detail_keyboard,
    get_admin_servers_keyboard,
    get_admin_promos_keyboard,
    get_admin_settings_keyboard,
)
from bot.keyboards.common import get_back_keyboard
from bot.utils.emojis import Emoji, EmojiID
from bot.states.project import BroadcastStates, AdminUserStates, AdminServerStates, AdminPromoStates
from services.user import UserService
from bot import texts

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS


@router.message(Command("admin"))
async def cmd_admin(message: Message, session, state: FSMContext):
    await state.clear()
    if not is_admin(message.from_user.id):
        await message.answer(texts.ADMIN_NO_ACCESS)
        return

    from services.user import UserService
    from services.project import ProjectService

    user_svc = UserService(session)
    users_count = await user_svc.count_users()

    from repositories.project import ProjectRepository
    project_repo = ProjectRepository(session)
    projects_count = await project_repo.count()

    from repositories.server import ServerRepository
    server_repo = ServerRepository(session)
    servers_count = await server_repo.count()

    await message.answer(
        texts.admin_panel_text(users_count, projects_count, servers_count),
        reply_markup=get_admin_keyboard(users_count, projects_count, servers_count),
    )


def admin_panel_text(users, projects, servers):
    return texts.admin_panel_text(users, projects, servers)


@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery, session, state: FSMContext):
    await state.clear()
    if not is_admin(callback.from_user.id):
        await callback.answer(texts.ADMIN_NO_ACCESS, show_alert=True)
        return

    from services.user import UserService
    from repositories.project import ProjectRepository
    from repositories.server import ServerRepository

    user_svc = UserService(session)
    project_repo = ProjectRepository(session)
    server_repo = ServerRepository(session)

    users_count = await user_svc.count_users()
    projects_count = await project_repo.count()
    servers_count = await server_repo.count()

    await callback.message.edit_text(
        texts.admin_panel_text(users_count, projects_count, servers_count),
        reply_markup=get_admin_keyboard(users_count, projects_count, servers_count),
    )
    await callback.answer()


# ─── USERS ───

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery, session):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return

    user_svc = UserService(session)
    users = await user_svc.get_all_users()

    await callback.message.edit_text(
        f"{Emoji.PEOPLE} <b>Люди</b> ({len(users)})",
        reply_markup=get_admin_users_keyboard(users),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_users_page_"))
async def admin_users_page(callback: CallbackQuery, session):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return
    page = int(callback.data.split("_")[-1])
    user_svc = UserService(session)
    users = await user_svc.get_all_users()

    await callback.message.edit_text(
        f"{Emoji.PEOPLE} <b>Люди</b> ({len(users)})",
        reply_markup=get_admin_users_keyboard(users, page),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_user_view_"))
async def admin_user_view(callback: CallbackQuery, session):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return
    user_id = int(callback.data.split("_")[-1])
    user_svc = UserService(session)
    user = await user_svc.get_user_by_id(user_id)

    if user is None:
        await callback.answer(texts.ADMIN_USER_NOT_FOUND, show_alert=True)
        return

    text = texts.admin_user_view_text(
        user.telegram_id,
        user.username,
        user.full_name,
        user.tariff,
        user.balance,
        user.is_banned,
        len(user.projects),
        user.registered_at.strftime('%d.%m.%Y %H:%M')
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_admin_user_detail_keyboard(user_id, user.is_banned),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_user_ban_"))
async def admin_user_ban(callback: CallbackQuery, session):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return
    user_id = int(callback.data.split("_")[-1])
    user_svc = UserService(session)
    await user_svc.ban_user(user_id)
    await callback.answer(texts.ADMIN_USER_BANNED, show_alert=True)

    user = await user_svc.get_user_by_id(user_id)
    if user:
        from bot.keyboards.admin import get_admin_user_detail_keyboard
        await callback.message.edit_text(
            texts.admin_user_status_text(user.username or str(user.telegram_id), "🚫 Забанен"),
            reply_markup=get_admin_user_detail_keyboard(user_id, True),
        )


@router.callback_query(F.data.startswith("admin_user_unban_"))
async def admin_user_unban(callback: CallbackQuery, session):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return
    user_id = int(callback.data.split("_")[-1])
    user_svc = UserService(session)
    await user_svc.unban_user(user_id)
    await callback.answer(texts.ADMIN_USER_UNBANNED, show_alert=True)

    user = await user_svc.get_user_by_id(user_id)
    if user:
        from bot.keyboards.admin import get_admin_user_detail_keyboard
        await callback.message.edit_text(
            texts.admin_user_status_text(user.username or str(user.telegram_id), "✅ Активен"),
            reply_markup=get_admin_user_detail_keyboard(user_id, False),
        )


@router.callback_query(F.data.startswith("admin_user_tariff_"))
async def admin_user_tariff(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return
    user_id = int(callback.data.split("_")[-1])
    await state.update_data(admin_tariff_user_id=user_id)
    await callback.message.edit_text(
        texts.ADMIN_TARIFF_SELECT_TEXT,
        reply_markup=get_admin_user_tariff_keyboard(user_id),
    )
    await callback.answer()


def get_admin_user_tariff_keyboard(user_id: int):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🆓 Free", callback_data=f"admin_set_tariff_{user_id}_free", style="default"),
        InlineKeyboardButton(text="💎 Premium", callback_data=f"admin_set_tariff_{user_id}_premium", style="success"),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", style="primary", callback_data=f"admin_user_view_{user_id}"),
    )
    return builder.as_markup()


@router.callback_query(F.data.startswith("admin_set_tariff_"))
async def admin_set_tariff(callback: CallbackQuery, session):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return
    parts = callback.data.split("_")
    user_id = int(parts[3])
    tariff = parts[4]
    if tariff not in ("free", "premium"):
        await callback.answer(texts.SETTINGS_UNKNOWN, show_alert=True)
        return

    user_svc = UserService(session)
    await user_svc.set_tariff(user_id, tariff)
    await callback.answer(texts.ADMIN_TARIFF_CHANGED(tariff), show_alert=True)

    user = await user_svc.get_user_by_id(user_id)
    if user:
        from bot.keyboards.admin import get_admin_user_detail_keyboard
        await callback.message.edit_text(
            texts.admin_user_tariff_text(user.username or str(user.telegram_id), tariff),
            reply_markup=get_admin_user_detail_keyboard(user_id, user.is_banned),
        )


# ─── SERVERS ───

@router.callback_query(F.data == "admin_locations")
async def admin_locations(callback: CallbackQuery, session):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return

    from repositories.server import ServerRepository
    server_repo = ServerRepository(session)
    servers = await server_repo.get_all()

    await callback.message.edit_text(
        f"{Emoji.HOME} <b>Узлы</b> ({len(servers)})",
        reply_markup=get_admin_servers_keyboard(servers),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_server_add")
async def admin_server_add(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer(texts.ADMIN_NO_ACCESS, show_alert=True)
        return
    await callback.message.edit_text(
        texts.ADMIN_SERVER_ENTER_NAME,
    )
    await state.set_state(AdminServerStates.waiting_name)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_user_balance_"))
async def admin_user_balance(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return
    user_id = int(callback.data.replace("admin_user_balance_", ""))
    await state.update_data(admin_balance_user_id=user_id)
    await callback.message.edit_text(
        texts.ADMIN_BALANCE_INPUT_TEXT,
    )
    await state.set_state(AdminUserStates.waiting_balance)
    await callback.answer()


@router.message(F.text, AdminUserStates.waiting_balance)
async def admin_balance_input(message: Message, state: FSMContext, session):
    if not is_admin(message.from_user.id):
        return

    import math

    try:
        amount = float(message.text.strip())
    except ValueError:
        await message.answer(texts.ADMIN_BALANCE_INPUT_ERROR)
        return
    if not math.isfinite(amount) or abs(amount) > 1_000_000:
        await message.answer(texts.ADMIN_BALANCE_INPUT_ERROR)
        return

    data = await state.get_data()
    user_id = data.get("admin_balance_user_id")
    if not user_id:
        await message.answer(texts.ADMIN_USER_NOT_FOUND)
        await state.clear()
        return

    user_svc = UserService(session)
    await user_svc.update_balance(user_id, amount)

    user = await user_svc.get_user_by_id(user_id)
    await state.clear()
    await message.answer(
        texts.admin_balance_result_text(amount, user.balance) if user else texts.ADMIN_USER_NOT_FOUND,
        reply_markup=get_back_keyboard("admin_panel"),
    )


@router.callback_query(F.data == "admin_subscriptions")
async def admin_subscriptions(callback: CallbackQuery, session):
    if not is_admin(callback.from_user.id):
        await callback.answer(texts.ADMIN_NO_ACCESS, show_alert=True)
        return

    user_svc = UserService(session)
    users = await user_svc.get_all_users()

    premium_count = sum(1 for u in users if u.tariff == "premium")
    free_count = sum(1 for u in users if u.tariff == "free")

    text = texts.admin_subscriptions_text(free_count, premium_count, len(users))

    await callback.message.edit_text(text, reply_markup=get_back_keyboard("admin_panel"))
    await callback.answer()


@router.callback_query(F.data == "admin_referrals")
async def admin_referrals(callback: CallbackQuery, session):
    if not is_admin(callback.from_user.id):
        await callback.answer(texts.ADMIN_NO_ACCESS, show_alert=True)
        return

    from repositories.referral import ReferralRepository
    ref_repo = ReferralRepository(session)
    referrals = await ref_repo.get_all()

    text = texts.admin_referrals_text(len(referrals))

    await callback.message.edit_text(text, reply_markup=get_back_keyboard("admin_panel"))
    await callback.answer()


@router.callback_query(F.data == "admin_servers")
async def admin_servers(callback: CallbackQuery, session):
    await admin_locations(callback, session)


@router.callback_query(F.data.startswith("admin_server_view_"))
async def admin_server_view(callback: CallbackQuery, session):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return

    server_id = int(callback.data.split("_")[-1])
    from repositories.server import ServerRepository
    server_repo = ServerRepository(session)
    server = await server_repo.get_by_id(server_id)

    if server is None:
        await callback.answer(texts.ADMIN_SERVER_NOT_FOUND, show_alert=True)
        return

    text = texts.admin_server_view_text(
        server.name,
        server.country,
        server.ip,
        server.port,
        bool(server.api_key),
        server.free_slots,
        server.total_slots,
        server.rating,
        server.ping,
        server.load_cpu,
        server.load_ram,
        server.status
    )

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🗑 Удалить сервер",
            callback_data=f"admin_sdel_{server_id}",
            style="danger",
            icon_custom_emoji_id=EmojiID.TRASH,
        ),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", style="primary", callback_data="admin_locations"),
    )

    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("admin_sdel_"))
async def admin_server_delete(callback: CallbackQuery, session):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return

    server_id = int(callback.data.split("_")[-1])
    from repositories.server import ServerRepository
    server_repo = ServerRepository(session)
    server = await server_repo.get_by_id(server_id)

    if server is None:
        await callback.answer(texts.ADMIN_SERVER_NOT_FOUND, show_alert=True)
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Да, удалить",
            callback_data=f"admin_sdelyes_{server_id}",
            style="danger",
        ),
        InlineKeyboardButton(
            style="primary",
            text="❌ Нет",
            callback_data=f"admin_server_view_{server_id}",
        ),
    )

    try:
        await callback.message.edit_text(
            texts.admin_server_delete_confirm_text(server.name),
            reply_markup=builder.as_markup(),
        )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("admin_sdelyes_"))
async def admin_server_delete_confirm(callback: CallbackQuery, session):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return

    server_id = int(callback.data.split("_")[-1])
    from repositories.server import ServerRepository
    server_repo = ServerRepository(session)
    await server_repo.delete(server_id)

    await callback.answer(texts.ADMIN_SERVER_DELETED, show_alert=True)

    servers = await server_repo.get_all()
    try:
        await callback.message.edit_text(
            texts.admin_servers_text(len(servers)),
            reply_markup=get_admin_servers_keyboard(servers),
        )
    except Exception:
        pass


# ─── STATS ───

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery, session):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return

    from services.user import UserService
    from repositories.project import ProjectRepository
    from repositories.server import ServerRepository

    user_svc = UserService(session)
    project_repo = ProjectRepository(session)
    server_repo = ServerRepository(session)

    users_count = await user_svc.count_users()
    projects_count = await project_repo.count()
    servers = await server_repo.get_all()
    running = await project_repo.get_running_projects()

    text = texts.admin_stats_text(
        users_count,
        projects_count,
        len(running),
        len(servers),
        len([s for s in servers if s.status == "online"]),
    )

    from bot.keyboards.admin import get_admin_keyboard
    await callback.message.edit_text(
        text,
        reply_markup=get_admin_keyboard(users_count, projects_count, len(servers)),
    )
    await callback.answer()


# ─── PROMOS ───

@router.callback_query(F.data == "admin_promos")
async def admin_promos(callback: CallbackQuery, session):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return

    from services.promo import PromoService
    promo_svc = PromoService(session)
    promos = await promo_svc.get_promos()

    await callback.message.edit_text(
        f"{Emoji.GIFT} <b>Ключи</b> ({len(promos)})",
        reply_markup=get_admin_promos_keyboard(promos),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_promo_view_"))
async def admin_promo_view(callback: CallbackQuery, session):
    if not is_admin(callback.from_user.id):
        await callback.answer(texts.ADMIN_NO_ACCESS, show_alert=True)
        return

    try:
        promo_id = int(callback.data.split("_")[-1])
    except ValueError:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return

    from repositories.promo import PromoRepository
    promo = await PromoRepository(session).get_by_id(promo_id)
    if promo is None:
        await callback.answer("Ключ не найден", show_alert=True)
        return

    expires = promo.expires_at.strftime("%d.%m.%Y %H:%M") if promo.expires_at else "бессрочно"
    text = (
        f"🎁 <b>Ключ</b>\n\n"
        f"<blockquote><b>Код:</b> <code>{escape(str(promo.code))}</code>\n"
        f"<b>Награда:</b> {escape(str(promo.reward_type))} = {escape(str(promo.reward_value))}\n"
        f"<b>Активации:</b> {promo.activated_count}/{promo.max_activations}\n"
        f"<b>Действует до:</b> {escape(str(expires))}</blockquote>"
    )
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard("admin_promos"),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "admin_promo_create")
async def admin_promo_create(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return
    await callback.message.edit_text(
        texts.ADMIN_PROMO_ENTER_CODE,
    )
    await state.set_state(AdminPromoStates.waiting_code)
    await callback.answer()


# ─── REFERRALS ───

@router.callback_query(F.data == "admin_referrals")
async def admin_referrals(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return
    await callback.answer(texts.ADMIN_REFERRAL_WIP, show_alert=True)


# ─── BROADCAST ───

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return
    await callback.message.edit_text(
        texts.ADMIN_BROADCAST_ENTER_MESSAGE,
        reply_markup=get_back_keyboard("admin_panel"),
    )
    await state.set_state(BroadcastStates.waiting_for_message)
    await callback.answer()


# ─── SETTINGS ───

@router.callback_query(F.data == "admin_settings")
async def admin_settings(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(texts.ADMIN_NO_ACCESS, show_alert=True)
        return
    from bot.config import settings as cfg
    await callback.message.edit_text(
        f"{Emoji.SETTINGS} <b>Параметры</b>",
        reply_markup=get_admin_settings_keyboard(cfg.AUTO_SLEEP_MINUTES),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_sleep_"))
async def admin_set_sleep(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(texts.ADMIN_NO_ACCESS, show_alert=True)
        return
    try:
        minutes = int(callback.data.replace("admin_sleep_", ""))
    except ValueError:
        await callback.answer(texts.SETTINGS_UNKNOWN, show_alert=True)
        return
    if minutes not in (0, 30, 60, 360, 1440):
        await callback.answer(texts.SETTINGS_UNKNOWN, show_alert=True)
        return

    from bot.config import settings as cfg
    cfg.AUTO_SLEEP_MINUTES = minutes

    await callback.answer(texts.ADMIN_SLEEP_CHANGED(minutes), show_alert=True)

    from bot.keyboards.admin import get_admin_settings_keyboard
    await callback.message.edit_reply_markup(reply_markup=get_admin_settings_keyboard(minutes))


# ─── BROADCAST HANDLER ───

@router.message(F.text, BroadcastStates.waiting_for_message)
async def broadcast_receive(message: Message, state: FSMContext, session, bot):
    if not is_admin(message.from_user.id):
        return

    from services.user import UserService
    user_svc = UserService(session)
    users = await user_svc.get_all_users()

    sent = 0
    failed = 0
    for user in users:
        try:
            await bot.send_message(user.telegram_id, message.text)
            sent += 1
        except Exception:
            failed += 1

    await state.clear()
    await message.answer(
        texts.admin_broadcast_done_text(sent, failed),
        reply_markup=get_back_keyboard("admin_panel"),
    )


# ─── SERVER ADD HANDLERS ───

@router.message(F.text, AdminServerStates.waiting_name)
async def server_name_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.update_data(server_name=message.text.strip())
    await message.answer(texts.ADMIN_SERVER_ENTER_COUNTRY)
    await state.set_state(AdminServerStates.waiting_country)


@router.message(F.text, AdminServerStates.waiting_country)
async def server_country_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.update_data(server_country=message.text.strip())
    await message.answer(texts.ADMIN_SERVER_ENTER_IP)
    await state.set_state(AdminServerStates.waiting_ip)


@router.message(F.text, AdminServerStates.waiting_ip)
async def server_ip_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.update_data(server_ip=message.text.strip())
    await message.answer(texts.ADMIN_SERVER_ENTER_API_KEY)
    await state.set_state(AdminServerStates.waiting_api_key)


@router.message(F.text, AdminServerStates.waiting_api_key)
async def server_api_key_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    api_key = message.text.strip()
    if api_key == "-":
        api_key = ""
    await state.update_data(server_api_key=api_key)
    await message.answer(texts.ADMIN_SERVER_ENTER_SLOTS)
    await state.set_state(AdminServerStates.waiting_slots)


@router.message(F.text, AdminServerStates.waiting_slots)
async def server_slots_received(message: Message, state: FSMContext, session):
    if not is_admin(message.from_user.id):
        return

    try:
        slots = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите число:")
        return

    data = await state.get_data()
    server_name = data["server_name"]
    server_ip = data["server_ip"]
    api_key = data.get("server_api_key", "")

    log_lines = []
    log_lines.append(f"🔌 <b>Подключение к {escape(str(server_name))} ({escape(str(server_ip))}:8080)</b>\n")

    status_msg = await message.answer(
        texts.ADMIN_SERVER_CHECKING + "\n\n"
        f"📋 Консоль подключения:\n"
        + "\n".join(log_lines),
    )

    from services.vps_agent import VPSClient
    client = VPSClient(
        base_url=f"http://{server_ip}:8080",
        api_key=api_key,
    )

    log_lines.append("1️⃣ Проверка health endpoint...")

    try:
        health = await client.health()
        if health.get("status") != "ok":
            log_lines.append(f"   {Emoji.CROSS} Ответ агента: {health}")
            try:
                await status_msg.edit_text(
                    f"📋 <b>Консоль подключения:</b>\n\n"
                    + "\n".join(log_lines)
                    + f"\n\n{Emoji.CROSS} <b>Агент ответил, но статус не OK</b>",
                    reply_markup=get_back_keyboard("admin_panel"),
                )
            except Exception:
                pass
            return
        log_lines.append(f"   {Emoji.CHECK} Health: OK")
    except Exception as e:
        error_text = str(e)
        log_lines.append(f"   {Emoji.CROSS} Ошибка: <code>{error_text[:200]}</code>")
        try:
            await status_msg.edit_text(
                f"📋 <b>Консоль подключения:</b>\n\n"
                + "\n".join(log_lines)
                + f"\n\n{Emoji.CROSS} <b>Не удалось подключиться к агенту</b>\n\n"
                f"Убедитесь что:\n"
                f"1. Агент запущен на сервере\n"
                f"2. Порт 8080 открыт в firewall\n"
                f"3. IP адрес верный",
                reply_markup=get_back_keyboard("admin_panel"),
            )
        except Exception:
            pass
        return

    try:
        await status_msg.edit_text(
            f"📋 <b>Консоль подключения:</b>\n\n"
            + "\n".join(log_lines)
            + f"\n\n{Emoji.LOADING} Проверка Docker...",
        )
    except Exception:
        pass

    log_lines.append("2️⃣ Проверка Docker...")

    try:
        stats = await client.get_server_stats()
        if stats.get("error"):
            raise RuntimeError(str(stats["error"]))
        containers_running = stats.get("containers_running", 0)
        containers_total = stats.get("containers_total", 0)
        log_lines.append(f"   {Emoji.CHECK} Docker: OK (контейнеров: {containers_running}/{containers_total})")
    except Exception as e:
        log_lines.append(f"   {Emoji.CROSS} Docker недоступен: <code>{str(e)[:150]}</code>")
        try:
            await status_msg.edit_text(
                f"📋 <b>Консоль подключения:</b>\n\n"
                + "\n".join(log_lines)
                + f"\n\n{Emoji.CROSS} <b>Docker недоступен на сервере</b>",
                reply_markup=get_back_keyboard("admin_panel"),
            )
        except Exception:
            pass
        return

    try:
        await status_msg.edit_text(
            f"📋 <b>Консоль подключения:</b>\n\n"
            + "\n".join(log_lines)
            + f"\n\n{Emoji.LOADING} Тестовый запуск контейнера...",
        )
    except Exception:
        pass

    log_lines.append("3️⃣ Тестовый запуск контейнера...")

    try:
        test_result = await client.create_container({
            "project_id": 0,
            "project_name": "test_connection",
            "python_version": "3.12",
            "entry_point": "main.py",
            "entry_type": "script",
            "tariff": "free",
            "env_vars": {},
        })

        if "error" in test_result:
            log_lines.append(f"   {Emoji.CROSS} Ошибка создания: <code>{test_result['error'][:150]}</code>")
            try:
                await status_msg.edit_text(
                    f"📋 <b>Консоль подключения:</b>\n\n"
                    + "\n".join(log_lines)
                    + f"\n\n{Emoji.CROSS} <b>Не удалось создать тестовый контейнер</b>\n\n"
                    f"Возможные причины:\n"
                    f"1. Docker не установлен\n"
                    f"2. Нет прав для запуска контейнеров\n"
                    f"3. Недостаточно ресурсов (RAM/Disk)\n"
                    f"4. Проблемы с сетью (нужен доступ к Docker Hub)",
                    reply_markup=get_back_keyboard("admin_panel"),
                )
            except Exception:
                pass
            return

        test_container_id = test_result.get("container_id", "")
        log_lines.append(f"   {Emoji.CHECK} Контейнер создан: <code>{test_container_id[:12]}...</code>")

        start_result = await client.start_container(test_container_id)
        if start_result.get("success"):
            log_lines.append(f"   {Emoji.CHECK} Контейнер запущен")
        else:
            log_lines.append(f"   {Emoji.CROSS} Не удалось поднять контейнер")

        await client.remove_container(test_container_id)
        log_lines.append(f"   {Emoji.CHECK} Тестовый контейнер удалён")

    except Exception as e:
        log_lines.append(f"   {Emoji.CROSS} Ошибка: <code>{str(e)[:150]}</code>")
        try:
            await status_msg.edit_text(
                f"📋 <b>Консоль подключения:</b>\n\n"
                + "\n".join(log_lines)
                + f"\n\n{Emoji.CROSS} <b>Ошибка при тестировании контейнера</b>",
                reply_markup=get_back_keyboard("admin_panel"),
            )
        except Exception:
            pass
        return

    try:
        await status_msg.edit_text(
            f"📋 <b>Консоль подключения:</b>\n\n"
            + "\n".join(log_lines)
            + f"\n\n{Emoji.LOADING} Сохранение сервера...",
        )
    except Exception:
        pass

    from repositories.server import ServerRepository
    server_repo = ServerRepository(session)
    await server_repo.create(
        name=server_name,
        country=data["server_country"],
        ip=server_ip,
        api_key=api_key,
        total_slots=slots,
        free_slots=slots,
        status="online",
    )

    log_lines.append("4️⃣ Сервер сохранён в базу данных")
    log_lines.append(f"   {Emoji.CHECK} Готово")

    await state.clear()
    try:
        await status_msg.edit_text(
            f"📋 <b>Консоль подключения:</b>\n\n"
            + "\n".join(log_lines)
            + f"\n\n{Emoji.CHECK} <b>Сервер {escape(str(server_name))} успешно добавлен!</b>\n\n"
            f"🌍 Страна: {escape(str(data['server_country']))}\n"
            f"📡 IP: {escape(str(server_ip))}:8080\n"
            f"💻 Слоты: {slots}\n"
            f"🔑 API Key: {'Есть' if api_key else 'Нет'}",
            reply_markup=get_back_keyboard("admin_panel"),
        )
    except Exception:
        await message.answer(
            f"📋 <b>Консоль подключения:</b>\n\n"
            + "\n".join(log_lines)
            + f"\n\n{Emoji.CHECK} <b>Сервер {escape(str(server_name))} успешно добавлен!</b>\n\n"
            f"🌍 Страна: {escape(str(data['server_country']))}\n"
            f"📡 IP: {escape(str(server_ip))}:8080\n"
            f"💻 Слоты: {slots}\n"
            f"🔑 API Key: {'Есть' if api_key else 'Нет'}",
            reply_markup=get_back_keyboard("admin_panel"),
        )


# ─── PROMO CREATE HANDLERS ───

@router.message(F.text, AdminPromoStates.waiting_code)
async def promo_code_input(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.update_data(promo_code=message.text.strip())
    await message.answer(texts.ADMIN_PROMO_ENTER_TYPE)
    await state.set_state(AdminPromoStates.waiting_reward_type)


@router.message(F.text, AdminPromoStates.waiting_reward_type)
async def promo_reward_type_input(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    reward_type = message.text.strip().lower()
    if reward_type not in ("tariff", "projects", "balance"):
        await message.answer(texts.ADMIN_PROMO_TYPE_ERROR)
        return

    await state.update_data(promo_reward_type=reward_type)
    await message.answer(texts.ADMIN_PROMO_ENTER_VALUE)
    await state.set_state(AdminPromoStates.waiting_reward_value)


@router.message(F.text, AdminPromoStates.waiting_reward_value)
async def promo_reward_value_input(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.update_data(promo_reward_value=message.text.strip())
    await message.answer(texts.ADMIN_PROMO_ENTER_MAX)
    await state.set_state(AdminPromoStates.waiting_max_activations)


@router.message(F.text, AdminPromoStates.waiting_max_activations)
async def promo_max_input(message: Message, state: FSMContext, session):
    if not is_admin(message.from_user.id):
        return

    try:
        max_act = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите число:")
        return
    if max_act < 1 or max_act > 1_000_000:
        await message.answer("❌ Количество активаций: от 1 до 1 000 000")
        return

    data = await state.get_data()
    from services.promo import PromoService
    promo_svc = PromoService(session)
    await promo_svc.create_promo(
        code=data["promo_code"],
        reward_type=data["promo_reward_type"],
        reward_value=data["promo_reward_value"],
        max_activations=max_act,
    )

    await state.clear()
    await message.answer(
        f"{Emoji.CHECK} Ключ <b>{escape(str(data['promo_code']))}</b> создан.",
        reply_markup=get_back_keyboard("admin_panel"),
    )
