from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.utils.emojis import Emoji, EmojiID

router = Router()


@router.callback_query(F.data == "locations")
async def locations_menu(callback: CallbackQuery, session):
    from repositories.server import ServerRepository

    server_repo = ServerRepository(session)
    servers = await server_repo.get_online_servers()

    if not servers:
        await callback.message.edit_text(
            f"{Emoji.HOME} <b>Серверы</b>\n\nНет доступных серверов.",
        )
        await callback.answer()
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()

    for s in servers:
        builder.row(
            InlineKeyboardButton(
                text=f"🌍 {s.name} ({s.country}) — {s.free_slots} слотов",
                callback_data=f"location_view_{s.id}",
                icon_custom_emoji_id=EmojiID.EARTH,
            )
        )
    builder.row(
        InlineKeyboardButton(text="🔄 Обновить", callback_data="locations"),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Меню", callback_data="main_menu"),
    )

    await callback.message.edit_text(
        f"{Emoji.HOME} <b>Доступные серверы</b>",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("location_view_"))
async def location_view(callback: CallbackQuery, session):
    server_id = int(callback.data.split("_")[-1])
    from repositories.server import ServerRepository

    server_repo = ServerRepository(session)
    server = await server_repo.get_by_id(server_id)

    if server is None:
        await callback.answer("Сервер не найден", show_alert=True)
        return

    from bot.utils.text import server_card
    text = server_card(
        name=server.name,
        country=server.country,
        free_slots=server.free_slots,
        total_slots=server.total_slots,
        rating=server.rating,
        ping=server.ping,
        load_cpu=server.load_cpu,
        load_ram=server.load_ram,
    )

    from bot.keyboards.common import get_back_keyboard
    await callback.message.edit_text(text, reply_markup=get_back_keyboard("locations"))
    await callback.answer()
