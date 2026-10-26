from __future__ import annotations

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)

from bot.config_photos import get_photo


async def smart_edit(
    target,
    text: str,
    photo_key: str | None = None,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: str = "HTML",
) -> Message | None:
    """
    Универсальная функция для редактирования сообщений.
    Автоматически определяет тип target (CallbackQuery или Message)
    и выбирает правильный метод редактирования.
    
    Args:
        target: CallbackQuery или Message
        text: Текст сообщения
        photo_key: Ключ фото из config_photos (опционально)
        reply_markup: Клавиатура
        parse_mode: Режим парсинга (по умолчанию HTML)
    
    Returns:
        Отредактированное или новое сообщение
    """
    if isinstance(target, CallbackQuery):
        message = target.message
    else:
        message = target
    
    return await edit_photo_or_text(
        message=message,
        text=text,
        photo_key=photo_key or "control_panel",  # Дефолтный ключ
        reply_markup=reply_markup,
        parse_mode=parse_mode,
    )


async def send_photo_or_text(
    target,
    text: str,
    photo_key: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: str = "HTML",
) -> Message | None:
    photo_file_id = get_photo(photo_key)

    if isinstance(target, CallbackQuery):
        if photo_file_id:
            try:
                await target.message.delete()
            except Exception:
                pass
            try:
                return await target.message.answer_photo(
                    photo=photo_file_id,
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
            except Exception:
                return await target.message.answer(
                    text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
        else:
            return await target.message.edit_text(
                text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
    elif isinstance(target, Message):
        if photo_file_id:
            try:
                return await target.answer_photo(
                    photo=photo_file_id,
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
            except Exception:
                return await target.answer(
                    text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
        else:
            return await target.answer(
                text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
    return None


async def edit_photo_or_text(
    message,
    text: str,
    photo_key: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: str = "HTML",
) -> Message | None:
    from aiogram.exceptions import TelegramBadRequest
    import logging
    import traceback
    
    logger = logging.getLogger(__name__)
    
    photo_file_id = get_photo(photo_key)

    if photo_file_id:
        # Есть фото для этого ключа
        if message.photo:
            # Сообщение уже содержит фото - меняем фото и caption
            try:
                return await message.edit_media(
                    media=InputMediaPhoto(
                        media=photo_file_id,
                        caption=text,
                        parse_mode=parse_mode,
                    ),
                    reply_markup=reply_markup,
                )
            except TelegramBadRequest as e:
                if "message is not modified" in str(e).lower():
                    return message
                # Если не получилось отредактировать - удаляем и создаем новое
                try:
                    await message.delete()
                except Exception:
                    pass
                try:
                    return await message.answer_photo(
                        photo=photo_file_id,
                        caption=text,
                        reply_markup=reply_markup,
                        parse_mode=parse_mode,
                    )
                except Exception:
                    return await message.answer(
                        text,
                        reply_markup=reply_markup,
                        parse_mode=parse_mode,
                    )
        else:
            # Сообщение текстовое - удаляем и создаем с фото
            try:
                await message.delete()
            except Exception:
                pass
            try:
                return await message.answer_photo(
                    photo=photo_file_id,
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
            except Exception:
                return await message.answer(
                    text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
    else:
        # Нет фото для этого ключа
        if message.photo:
            # Сообщение содержит фото, но нужен текст - удаляем и создаем текстовое
            try:
                await message.delete()
            except Exception:
                pass
            return await message.answer(
                text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
        else:
            # Сообщение текстовое - редактируем текст
            try:
                return await message.edit_text(
                    text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
            except TelegramBadRequest as e:
                # Игнорируем ошибку "message is not modified"
                if "message is not modified" in str(e).lower():
                    logger.warning(
                        f"[edit_photo_or_text] Message not modified error ignored.\n"
                        f"Photo key: {photo_key}"
                    )
                    return message
                else:
                    logger.error(
                        f"[edit_photo_or_text] Telegram error occurred.\n"
                        f"Photo key: {photo_key}\n"
                        f"Text length: {len(text)}\n"
                        f"Error: {str(e)}\n"
                        f"Traceback:\n{traceback.format_exc()}"
                    )
                    raise
