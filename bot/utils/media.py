from __future__ import annotations

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)

from bot.config_photos import get_photo


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
            return await target.message.answer_photo(
                photo=photo_file_id,
                caption=text,
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
            return await target.answer_photo(
                photo=photo_file_id,
                caption=text,
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
        try:
            await message.delete()
        except Exception:
            pass
        return await message.answer_photo(
            photo=photo_file_id,
            caption=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
    else:
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
                    f"File: {__file__}\n"
                    f"Function: edit_photo_or_text\n"
                    f"Photo key: {photo_key}\n"
                    f"Text length: {len(text)}\n"
                    f"Error: {str(e)}"
                )
                return message
            else:
                logger.error(
                    f"[edit_photo_or_text] Telegram error occurred.\n"
                    f"File: {__file__}\n"
                    f"Function: edit_photo_or_text\n"
                    f"Photo key: {photo_key}\n"
                    f"Text length: {len(text)}\n"
                    f"Error: {str(e)}\n"
                    f"Traceback:\n{traceback.format_exc()}"
                )
                raise
