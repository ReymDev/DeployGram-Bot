from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.common import get_back_keyboard
from bot.utils.emojis import Emoji, EmojiID

router = Router()


@router.callback_query(F.data.startswith("project_monitor_"))
async def project_monitor(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer("Проект не найден", show_alert=True)
        return

    monitoring = await project_service.get_monitoring(project_id)

    from bot.utils.formatters import format_status, format_uptime
    text = (
        f"{Emoji.GRAPH_STATS} <b>Мониторинг: {project.name}</b>\n\n"
        f"Статус: {format_status(monitoring.get('status', 'unknown'))}\n"
        f"CPU: <b>{monitoring.get('cpu', 0):.1f}%</b>\n"
        f"RAM: <b>{monitoring.get('ram', 0):.1f} MB</b>\n"
        f"Disk: <b>{monitoring.get('disk', 0):.1f} MB</b>\n"
        f"Uptime: <b>{monitoring.get('uptime', '—')}</b>\n"
        f"Рестартов: <b>{monitoring.get('restarts', 0)}</b>"
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
        await callback.answer("Нет доступа", show_alert=True)
        return

    from services.monitoring import MonitoringService
    monitoring = MonitoringService(session)
    stats = await monitoring.get_stats_history(project_id, hours)

    if not stats:
        await callback.answer("Нет данных за этот период", show_alert=True)
        return

    avg_cpu = sum(s.cpu_percent for s in stats) / len(stats)
    max_cpu = max(s.cpu_percent for s in stats)
    avg_ram = sum(s.ram_mb for s in stats) / len(stats)
    max_ram = max(s.ram_mb for s in stats)

    text = (
        f"{Emoji.GRAPH_UP} <b>Графики за {hours}ч</b>\n\n"
        f"{Emoji.GRAPH_STATS} CPU:\n"
        f"  Среднее: {avg_cpu:.1f}%\n"
        f"  Максимум: {max_cpu:.1f}%\n\n"
        f"{Emoji.GRAPH_UP} RAM:\n"
        f"  Среднее: {avg_ram:.1f} MB\n"
        f"  Максимум: {max_ram:.1f} MB\n\n"
        f"{Emoji.INFO} Точек данных: {len(stats)}"
    )

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
