from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.utils.emojis import Emoji, EmojiID

router = Router()


@router.callback_query(F.data.startswith("project_versions_"))
async def versions_menu(callback: CallbackQuery, project_service, db_user):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer("Проект не найден", show_alert=True)
        return

    versions = await project_service.get_versions(project_id)

    from bot.keyboards.user import get_versions_keyboard
    await callback.message.edit_text(
        f"{Emoji.TIME_PAST} <b>Версии: {project.name}</b>\n\n"
        f"Всего версий: {len(versions)}",
        reply_markup=get_versions_keyboard(project_id, versions),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("version_view_"))
async def version_view(callback: CallbackQuery, project_service, db_user, session):
    parts = callback.data.split("_")
    project_id = int(parts[2])
    version_id = int(parts[3])

    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer("Нет доступа", show_alert=True)
        return

    from repositories.project import ProjectVersionRepository
    version_repo = ProjectVersionRepository(session)
    version = await version_repo.get_by_id(version_id)

    if version is None:
        await callback.answer("Версия не найдена", show_alert=True)
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔄 Откатить",
            callback_data=f"version_restore_{project_id}_{version_id}",
            style="primary",
            icon_custom_emoji_id=EmojiID.LOADING,
        ),
    )
    builder.row(
        InlineKeyboardButton(text="◁ Назад", callback_data=f"project_versions_{project_id}"),
    )

    await callback.message.edit_text(
        f"{Emoji.TIME_PAST} <b>Версия {version.version_number}</b>\n\n"
        f"Создана: {version.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"Python: {version.python_version}\n"
        f"Entry: <code>{version.entry_point}</code>",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("version_restore_"))
async def version_restore(callback: CallbackQuery, project_service, db_user):
    parts = callback.data.split("_")
    project_id = int(parts[2])
    version_id = int(parts[3])

    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer("Нет доступа", show_alert=True)
        return

    success = await project_service.restore_version(project_id, version_id)
    if success:
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="◁ Назад", callback_data=f"project_versions_{project_id}"),
        )
        await callback.message.edit_text(
            f"{Emoji.CHECK} Версия восстановлена.\n\n"
            f"Для применения изменений перезапустите проект.",
            reply_markup=builder.as_markup(),
        )
    else:
        await callback.answer("❌ Ошибка восстановления", show_alert=True)
