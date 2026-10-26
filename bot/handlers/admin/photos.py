from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.config import settings
from bot.config_photos import (
    PHOTO_LABELS,
    get_all_photos,
    get_photo,
    set_photo,
)
from bot.keyboards.common import get_back_keyboard
from bot.utils.emojis import Emoji

router = Router()


class PhotoStates(StatesGroup):
    waiting_photo = State()
    waiting_key = State()


def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS


@router.callback_query(F.data == "admin_photos")
async def admin_photos_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return

    photos = get_all_photos()

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()

    for key, label in PHOTO_LABELS.items():
        has_photo = "✅" if photos.get(key) else "⬜"
        builder.row(
            InlineKeyboardButton(
                text=f"{has_photo} {label}",
                callback_data=f"admin_photo_set_{key}",
            )
        )

    builder.row(
        InlineKeyboardButton(text="◁ Назад", style="primary", callback_data="admin_panel"),
    )

    await callback.message.edit_text(
        f"{Emoji.MEDIA} <b>Управление фото</b>\n\n"
        f"✅ — фото установлено\n"
        f"⬜ — фото не установлено\n\n"
        f"Нажмите на пункт чтобы установить/заменить фото.",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_photo_set_"))
async def admin_photo_select(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔", show_alert=True)
        return

    key = callback.data.replace("admin_photo_set_", "")
    if key not in PHOTO_LABELS:
        await callback.answer("Неизвестный экран", show_alert=True)
        return
    label = PHOTO_LABELS.get(key, key)

    await state.update_data(photo_key=key)
    await state.set_state(PhotoStates.waiting_photo)

    current = get_photo(key)
    status = "✅ Установлено" if current else "❌ Не установлено"

    await callback.message.edit_text(
        f"{Emoji.MEDIA} <b>{label}</b>\n\n"
        f"Статус: {status}\n\n"
        f"Отправьте фото для этого экрана.\n"
        f"Или отправьте <code>удалить</code> чтобы убрать фото.",
        reply_markup=get_back_keyboard("admin_photos"),
    )
    await callback.answer()


@router.message(F.photo, PhotoStates.waiting_photo)
async def admin_photo_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    key = data.get("photo_key")
    if not key or key not in PHOTO_LABELS:
        await state.clear()
        await message.answer("??????????? ?????, ???????? ?????.")
        return
    label = PHOTO_LABELS.get(key, key)

    photo = message.photo[-1]
    file_id = photo.file_id

    set_photo(key, file_id)

    await state.clear()
    await message.answer(
        f"{Emoji.CHECK} Фото для <b>{label}</b> установлено!",
        reply_markup=get_back_keyboard("admin_photos"),
    )


@router.message(F.text, PhotoStates.waiting_photo)
async def admin_photo_text(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    text = message.text.strip()

    if text.lower() in ("удалить", "delete", "remove", "убрать"):
        data = await state.get_data()
        key = data.get("photo_key")
        if not key or key not in PHOTO_LABELS:
            await state.clear()
            await message.answer("??????????? ?????, ???????? ?????.")
            return
        label = PHOTO_LABELS.get(key, key)

        set_photo(key, None)

        await state.clear()
        await message.answer(
            f"{Emoji.CHECK} Фото для <b>{label}</b> удалено!",
            reply_markup=get_back_keyboard("admin_photos"),
        )
    else:
        await message.answer(
            "❌ Отправьте фото или напишите <code>удалить</code>",
        )
