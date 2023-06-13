from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отправить номер телефона",
                           request_contact=True)
        ]
    ],
    resize_keyboard=True
)