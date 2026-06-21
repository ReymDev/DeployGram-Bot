from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.utils.emojis import Emoji, EmojiID

router = Router()


class CoOwnerStates(StatesGroup):
    waiting_id = State()


@router.callback_query(F.data.startswith("project_coowners_"))
async def coowners_menu(callback: CallbackQuery, project_service, db_user, session):
    project_id = int(callback.data.split("_")[-1])
    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer("Проект не найден", show_alert=True)
        return

    from repositories.coowner import CoOwnerRepository
    coowner_repo = CoOwnerRepository(session)
    coowners = await coowner_repo.get_by_project_id(project_id)

    from bot.keyboards.user import get_coowners_keyboard
    await callback.message.edit_text(
        f"{Emoji.PEOPLE} <b>Совладельцы: {project.name}</b>\n\n"
        f"Роли:\n"
        f"  <b>Owner</b> — полный доступ\n"
        f"  <b>Developer</b> — запуск, остановка, логи, файлы",
        reply_markup=get_coowners_keyboard(project_id, coowners),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("coowner_add_"))
async def coowner_add(callback: CallbackQuery, state: FSMContext, db_user):
    project_id = int(callback.data.split("_")[-1])
    await state.update_data(coowner_project_id=project_id)
    await callback.message.edit_text(
        f"{Emoji.PROFILE} Отправьте Telegram ID пользователя для добавления:",
    )
    await state.set_state(CoOwnerStates.waiting_id)
    await callback.answer()


@router.callback_query(F.data.startswith("coowner_remove_"))
async def coowner_remove(callback: CallbackQuery, project_service, db_user, session):
    parts = callback.data.split("_")
    project_id = int(parts[2])
    coowner_id = int(parts[3])

    project = await project_service.get_project(project_id)
    if project is None or project.user_id != db_user.id:
        await callback.answer("Нет доступа", show_alert=True)
        return

    from repositories.coowner import CoOwnerRepository
    coowner_repo = CoOwnerRepository(session)
    await coowner_repo.delete(coowner_id)

    await callback.answer("Совладелец удалён", show_alert=True)

    coowners = await coowner_repo.get_by_project_id(project_id)
    from bot.keyboards.user import get_coowners_keyboard
    await callback.message.edit_text(
        f"{Emoji.PEOPLE} <b>Совладельцы: {project.name}</b>",
        reply_markup=get_coowners_keyboard(project_id, coowners),
    )


@router.message(F.text, CoOwnerStates.waiting_id)
async def coowner_id_received(message: Message, state: FSMContext, session, db_user):
    data = await state.get_data()
    project_id = data.get("coowner_project_id")

    try:
        target_telegram_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите числовой Telegram ID")
        return

    if target_telegram_id == db_user.telegram_id:
        await message.answer("❌ Нельзя добавить самого себя")
        return

    from repositories.user import UserRepository
    user_repo = UserRepository(session)
    target_user = await user_repo.get_by_telegram_id(target_telegram_id)

    if target_user is None:
        await message.answer(
            "❌ Пользователь не найден. Он должен хотя бы раз запустить бота."
        )
        return

    from repositories.coowner import CoOwnerRepository
    coowner_repo = CoOwnerRepository(session)
    existing = await coowner_repo.get_by_user_and_project(target_user.id, project_id)
    if existing:
        await message.answer("❌ Этот пользователь уже совладелец")
        return

    await coowner_repo.create(
        project_id=project_id,
        user_id=target_user.id,
        role="developer",
    )

    await state.clear()
    await message.answer(
        f"{Emoji.CHECK} Пользователь <b>{target_user.username or target_telegram_id}</b> добавлен как совладелец.",
        reply_markup=get_back_keyboard(f"project_coowners_{project_id}"),
    )
