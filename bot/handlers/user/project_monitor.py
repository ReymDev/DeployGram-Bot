from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.common import get_back_keyboard
from bot.utils.emojis import Emoji, EmojiID
from bot import texts

router = Router()


@router.callback_query(F.data.startswith("project_monitor_"))
async def project_monitor(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer(texts.ERROR_NOT_FOUND, show_alert=True)
        return

    monitoring = await project_service.get_monitoring(project_id)

    from bot.utils.formatters import format_status, format_uptime
    status_text = format_status(monitoring.get('status', 'unknown'))
    text = texts.project_monitor_text(
        project.name,
        status_text,
        monitoring.get('cpu', 0),
        monitoring.get('ram', 0),
        monitoring.get('disk', 0),
        monitoring.get('uptime', '—'),
        monitoring.get('restarts', 0)
    )

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔄 Обновить",
            callback_data=f"project_monitor_{project_id}",
            icon_custom_emoji_id=EmojiID.LOADING,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="📊 Графики (24ч)",
            callback_data=f"project_graphs_24_{project_id}",
            icon_custom_emoji_id=EmojiID.GRAPH_STATS,
        ),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data=f"project_view_{project_id}"),
    )

    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("project_graphs_"))
async def project_graphs(callback: CallbackQuery, project_service, db_user, session):
    parts = callback.data.split("_")
    hours = int(parts[2])
    project_id = int(parts[3])

    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer(texts.ERROR_NO_ACCESS, show_alert=True)
        return

    from services.monitoring import MonitoringService
    monitoring = MonitoringService(session)
    stats = await monitoring.get_stats_history(project_id, hours)

    if not stats:
        await callback.answer(texts.ERROR_NO_STATS_DATA, show_alert=True)
        return

    avg_cpu = sum(s.cpu_percent for s in stats) / len(stats)
    max_cpu = max(s.cpu_percent for s in stats)
    avg_ram = sum(s.ram_mb for s in stats) / len(stats)
    max_ram = max(s.ram_mb for s in stats)

    text = texts.project_graphs_text(hours, avg_cpu, max_cpu, avg_ram, max_ram, len(stats))

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    for h in [24, 168, 720]:
        label = {24: "24ч", 168: "7д", 720: "30д"}[h]
        builder.row(
            InlineKeyboardButton(
                text=f"📊 {label}",
                callback_data=f"project_graphs_{h}_{project_id}",
                icon_custom_emoji_id=EmojiID.GRAPH_STATS,
            )
        )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data=f"project_monitor_{project_id}"),
    )

    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
    except Exception:
        pass
    await callback.answer()
