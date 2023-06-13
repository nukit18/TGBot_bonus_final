from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

from data.config import URL_SITE

web_app = WebAppInfo(url=URL_SITE)


async def menu_keyboard(balance: int):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f"Баланс: {balance}")
            ],
            [
                KeyboardButton(text="Показать код"),
            ],
            [
                KeyboardButton(text="Ассортимент магазина", web_app=web_app)
            ]
        ],
        resize_keyboard=True
    )
    return keyboard