from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup,
                           InlineKeyboardButton, WebAppInfo)
menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Додати пісню"),
            KeyboardButton(text="Показати плейлист")
        ],

    ],
    resize_keyboard=True,
    input_field_placeholder="🔹 Обери дію з меню"
)
