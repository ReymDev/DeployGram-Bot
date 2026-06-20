from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

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
from bot.utils.emojis import Emoji
from bot.states.project import BroadcastStates, AdminUserStates, AdminServerStates, AdminPromoStates
from services.user import UserService

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS


@router.message(Command("admin"))
async def cmd_admin(message: Message, session):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа")
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
        admin_panel_text(users_count, projects_count, servers_count),
        reply_markup=get_admin_keyboard(users_count, projects_count, servers_count),
    )


def admin_panel_text(users, projects, servers):
    return (
        f"{Emoji.SETTINGS} <b>Админ-панель</b>\n\n"
        f"👤 Пользователей: {users}\n"
        f"📦 Проектов: {projects}\n"
        f"🌍 Серверов: {servers}"
    )


@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery, session):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
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
        admin_panel_text(users_count, projects_count, servers_count),
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
        f"{Emoji.PEOPLE} <b>Пользователи</b> ({len(users)})",
        reply_markup=get_admin_users_keyboard(users),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_users_page_"))
async def admin_users_page(callback: CallbackQuery, session):
    page = int(callback.data.split("_")[-1])
    user_svc = UserService(session)
    users = await user_svc.get_all_users()

    await callback.message.edit_text(
        f"{Emoji.PEOPLE} <b>Пользователи</b> ({len(users)})",
        reply_markup=get_admin_users_keyboard(users, page),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_user_view_"))
async def admin_user_view(callback: CallbackQuery, session):
    user_id = int(callback.data.split("_")[-1])
    user_svc = UserService(session)
    user = await user_svc.get_user_by_id(user_id)

    if user is None:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    text = (
        f"{Emoji.PROFILE} <b>Пользователь</b>\n\n"
        f"ID: <code>{user.telegram_id}</code>\n"
        f"Username: @{user.username or '—'}\n"
        f"Имя: {user.full_name or '—'}\n"
        f"Тариф: <b>{user.tariff}</b>\n"
        f"Баланс: <b>{user.balance:.2f}</b>\n"
        f"Статус: {'🚫 Забанен' if user.is_banned else '✅ Активен'}\n"
        f"Проектов: {len(user.projects)}\n"
        f"Регистрация: {user.registered_at.strftime('%d.%m.%Y %H:%M')}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_admin_user_detail_keyboard(user_id, user.is_banned),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_user_ban_"))
async def admin_user_ban(callback: CallbackQuery, session):
    user_id = int(callback.data.split("_")[-1])
    user_svc = UserService(session)
    await user_svc.ban_user(user_id)
    await callback.answer("🚫 Пользователь забанен", show_alert=True)

    user = await user_svc.get_user_by_id(user_id)
    if user:
        from bot.keyboards.admin import get_admin_user_detail_keyboard
        await callback.message.edit_text(
            f"{Emoji.PROFILE} <b>{user.username or user.telegram_id}</b> — 🚫 Забанен",
            reply_markup=get_admin_user_detail_keyboard(user_id, True),
        )


@router.callback_query(F.data.startswith("admin_user_unban_"))
async def admin_user_unban(callback: CallbackQuery, session):
    user_id = int(callback.data.split("_")[-1])
    user_svc = UserService(session)
    await user_svc.unban_user(user_id)
    await callback.answer("✅ Пользователь разбанен", show_alert=True)

    user = await user_svc.get_user_by_id(user_id)
    if user:
        from bot.keyboards.admin import get_admin_user_detail_keyboard
        await callback.message.edit_text(
            f"{Emoji.PROFILE} <b>{user.username or user.telegram_id}</b> — ✅ Активен",
            reply_markup=get_admin_user_detail_keyboard(user_id, False),
        )


@router.callback_query(F.data.startswith("admin_user_tariff_"))
async def admin_user_tariff(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[-1])
    await state.update_data(admin_tariff_user_id=user_id)
    await callback.message.edit_text(
        f"{Emoji.SETTINGS} Выберите тариф для пользователя:",
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
        InlineKeyboardButton(text="◁ Назад", callback_data=f"admin_user_view_{user_id}"),
    )
    return builder.as_markup()


@router.callback_query(F.data.startswith("admin_set_tariff_"))
async def admin_set_tariff(callback: CallbackQuery, session):
    parts = callback.data.split("_")
    user_id = int(parts[3])
    tariff = parts[4]

    user_svc = UserService(session)
    await user_svc.set_tariff(user_id, tariff)
    await callback.answer(f"✅ Тариф изменён на {tariff}", show_alert=True)

    user = await user_svc.get_user_by_id(user_id)
    if user:
        from bot.keyboards.admin import get_admin_user_detail_keyboard
        await callback.message.edit_text(
            f"{Emoji.PROFILE} <b>{user.username or user.telegram_id}</b> — Тариф: {tariff}",
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
        f"{Emoji.HOME} <b>Серверы</b> ({len(servers)})",
        reply_markup=get_admin_servers_keyboard(servers),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_server_add")
async def admin_server_add(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        f"{Emoji.HOME} Введите название сервера:",
    )
    await state.set_state(AdminServerStates.waiting_name)
    await callback.answer()


@router.callback_query(F.data == "admin_subscriptions")
async def admin_subscriptions(callback: CallbackQuery):
    await callback.answer("Управление подписками в разработке", show_alert=True)


@router.callback_query(F.data == "admin_servers")
async def admin_servers(callback: CallbackQuery, session):
    await admin_locations(callback, session)


@router.callback_query(F.data.startswith("admin_server_view_"))
async def admin_server_view(callback: CallbackQuery):
    await callback.answer("Информация о сервере в разработке", show_alert=True)


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

    text = (
        f"{Emoji.GRAPH_STATS} <b>Статистика</b>\n\n"
        f"👤 Пользователей: {users_count}\n"
        f"📦 Всего проектов: {projects_count}\n"
        f"🟢 Активных: {len(running)}\n"
        f"🌍 Серверов: {len(servers)}\n"
        f"🟢 Онлайн: {len([s for s in servers if s.status == 'online'])}"
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
        f"{Emoji.GIFT} <b>Промокоды</b> ({len(promos)})",
        reply_markup=get_admin_promos_keyboard(promos),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_promo_create")
async def admin_promo_create(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        f"{Emoji.GIFT} Введите код промокода:",
    )
    await state.set_state(AdminPromoStates.waiting_code)
    await callback.answer()


# ─── REFERRALS ───

@router.callback_query(F.data == "admin_referrals")
async def admin_referrals(callback: CallbackQuery):
    await callback.answer("Настройка реферальной системы в разработке", show_alert=True)


# ─── BROADCAST ───

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        f"{Emoji.SPEAKER} Отправьте сообщение для рассылки:",
        reply_markup=get_back_keyboard("admin_panel"),
    )
    await state.set_state(BroadcastStates.waiting_for_message)
    await callback.answer()


# ─── SETTINGS ───

@router.callback_query(F.data == "admin_settings")
async def admin_settings(callback: CallbackQuery):
    from bot.config import settings as cfg
    await callback.message.edit_text(
        f"{Emoji.SETTINGS} <b>Настройки</b>",
        reply_markup=get_admin_settings_keyboard(cfg.AUTO_SLEEP_MINUTES),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_sleep_"))
async def admin_set_sleep(callback: CallbackQuery):
    minutes = int(callback.data.split("_")[-1])
    await callback.answer(f"✅ Автосон: {minutes} минут", show_alert=True)


# ─── BROADCAST HANDLER ───

@router.message(F.text, BroadcastStates.waiting_for_message)
async def broadcast_receive(message: Message, state: FSMContext, session):
    if not is_admin(message.from_user.id):
        return

    from services.user import UserService
    user_svc = UserService(session)
    users = await user_svc.get_all_users()

    sent = 0
    failed = 0
    for user in users:
        try:
            from aiogram import Bot
            from bot.config import settings
            bot = Bot(token=settings.BOT_TOKEN)
            await bot.send_message(user.telegram_id, message.text)
            sent += 1
        except Exception:
            failed += 1

    await state.clear()
    await message.answer(
        f"{Emoji.CHECK} Рассылка завершена.\n\n"
        f"✅ Отправлено: {sent}\n"
        f"❌ Ошибок: {failed}",
        reply_markup=get_back_keyboard("admin_panel"),
    )


# ─── SERVER ADD HANDLERS ───

@router.message(F.text, AdminServerStates.waiting_name)
async def server_name_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.update_data(server_name=message.text.strip())
    await message.answer(f"{Emoji.HOME} Введите страну сервера:")
    await state.set_state(AdminServerStates.waiting_country)


@router.message(F.text, AdminServerStates.waiting_country)
async def server_country_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.update_data(server_country=message.text.strip())
    await message.answer(f"{Emoji.HOME} Введите IP адрес сервера:")
    await state.set_state(AdminServerStates.waiting_ip)


@router.message(F.text, AdminServerStates.waiting_ip)
async def server_ip_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.update_data(server_ip=message.text.strip())
    await message.answer(f"{Emoji.HOME} Введите количество слотов:")
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
    from repositories.server import ServerRepository
    server_repo = ServerRepository(session)
    await server_repo.create(
        name=data["server_name"],
        country=data["server_country"],
        ip=data["server_ip"],
        total_slots=slots,
        free_slots=slots,
        status="online",
    )

    await state.clear()
    await message.answer(
        f"{Emoji.CHECK} Сервер <b>{data['server_name']}</b> добавлен.",
        reply_markup=get_back_keyboard("admin_panel"),
    )


# ─── PROMO CREATE HANDLERS ───

@router.message(F.text, AdminPromoStates.waiting_code)
async def promo_code_input(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.update_data(promo_code=message.text.strip())
    await message.answer(f"{Emoji.GIFT} Введите тип награды (tariff/projects/balance):")
    await state.set_state(AdminPromoStates.waiting_reward_type)


@router.message(F.text, AdminPromoStates.waiting_reward_type)
async def promo_reward_type_input(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    reward_type = message.text.strip().lower()
    if reward_type not in ("tariff", "projects", "balance"):
        await message.answer("❌ Допустимые типы: tariff, projects, balance")
        return

    await state.update_data(promo_reward_type=reward_type)
    await message.answer(f"{Emoji.GIFT} Введите значение награды:")
    await state.set_state(AdminPromoStates.waiting_reward_value)


@router.message(F.text, AdminPromoStates.waiting_reward_value)
async def promo_reward_value_input(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.update_data(promo_reward_value=message.text.strip())
    await message.answer(f"{Emoji.GIFT} Введите макс. количество активаций:")
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
        f"{Emoji.CHECK} Промокод <b>{data['promo_code']}</b> создан.",
        reply_markup=get_back_keyboard("admin_panel"),
    )
