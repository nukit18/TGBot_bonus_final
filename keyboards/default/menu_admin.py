from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

from utils.db_api.quick_commands import quick_cmd_user
from data.config import URL_SITE

web_app = WebAppInfo(url=URL_SITE)


async def admin_keyboard_func(user_id: int):
    role = await quick_cmd_user.get_role(user_id)
    keyboard = []
    if role == "admin":
        keyboard.append([KeyboardButton(text="Изменить роли сотрудников")])
    else:
        pass
    keyboard.append([KeyboardButton(text="Управление рассылками")])
    keyboard.append([KeyboardButton(text="Изменить список товаров и акций")])
    keyboard.append([KeyboardButton(text="Ассортимент магазина", web_app=web_app)])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


