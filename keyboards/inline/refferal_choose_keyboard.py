from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.db_api.quick_commands import quick_cmd_user


async def get_refferal_option_keyboard(user_id: int):
    user = await quick_cmd_user.select_user(user_id)
    inline_keyboard = []
    inline_keyboard.append([InlineKeyboardButton(text="Показать код для приглашения", callback_data="reffer")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard


refferal_input_confirm_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да, есть", callback_data="yes_refferal")
        ],
        [
            InlineKeyboardButton(text="Нет", callback_data="no_refferal")
        ]
    ]
)