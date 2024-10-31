from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           ReplyKeyboardMarkup, KeyboardButton)


main_reply = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="/start")]],
    resize_keyboard=True)


inline_after_parse = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Да", callback_data="new_parse")],
    [InlineKeyboardButton(text="Нет", callback_data="stop_working")]])