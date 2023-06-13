import random
from datetime import date, datetime
from sqlalchemy import sql
from asyncpg import UniqueViolationError

from data.config import ADD_REFFERAL, ADD_REFFER
from keyboards.default import menu
from loader import bot
from utils.db_api.db_gino import db
from utils.db_api.schemas.user import User
import secrets


# три роли: admin/user/manager
async def add_user(id: int, phone_number: str, name: str, surname: str, balance: int = 0, role: str = "user"):
    try:
        while True:
            personal_invite_code = secrets.token_hex(10)
            check = await check_invite_code(personal_invite_code)
            if not check:
                break
        user = User(id=id, phone_number=phone_number, name=name,
                    surname=surname, balance=balance, role=role, invite_code_is_active=False, personal_invite_code=personal_invite_code)
        await user.create()

    except UniqueViolationError:
        pass


async def update_invite_code_activate(user_id_refferal, invite_code_reffer):
    user_reffer = await User.query.where(User.personal_invite_code == invite_code_reffer).gino.first()
    user_refferal = await User.query.where(User.id == user_id_refferal).gino.first()
    if not user_reffer or user_refferal.invite_code_is_active or user_refferal.id == user_reffer.id:
        return False
    balance_refferal = user_refferal.balance
    await user_refferal.update(balance=balance_refferal + ADD_REFFERAL).apply()
    await user_refferal.update(invite_code_is_active=True).apply()
    balance_reffer = user_reffer.balance
    await user_reffer.update(balance=balance_reffer + ADD_REFFER).apply()
    keyboard = await menu.menu_keyboard(balance_reffer + ADD_REFFER)
    await bot.send_message(user_reffer.id, "Баланс обновлен (реферальный код)", reply_markup=keyboard)
    return True


async def check_invite_code(invite_code):
    user = await User.query.where(User.personal_invite_code == invite_code).gino.first()
    if user:
        return True
    return False


async def select_all_users():
    users = await User.query.gino.all()
    return users


# id выдаются в виде списка, например (33445,)
async def get_ids():
    users_ids = await User.select("id").gino.all()
    return users_ids


async def get_codes():
    users_codes = await User.select("code").gino.all()
    return {code[0] for code in users_codes}


async def select_user(id: int):
    user = await User.query.where(User.id == id).gino.first()
    return user


# добавить проверку регуляркой (номер телефона может изменится с +7 на 8)
async def select_by_phone(phone_number: str):
    user = await User.query.where(User.phone_number == phone_number).gino.first()
    return user


# значение value может быть и положительным, и отрицательным, в зависимости от изменения суммы
async def change_balance(id: int, value: int):
    user = await User.get(id)
    balance = user.balance
    await user.update(balance=balance + value).apply()


async def generate_code(id: int):
    user = await User.get(id)
    code = secrets.token_hex(16)
    await user.update(code=code).apply()


async def update_msg_id(id: int, msg_id: int):
    user = await User.get(id)
    await user.update(msg_id_code=msg_id).apply()


async def delete_code(id:int):
    user = await User.get(id)
    await user.update(code=None).apply()
    await user.update(msg_id_code=None).apply()


async def get_role(id: int):
    user = await User.query.where(User.id == id).gino.first()
    return user.role


async def update_role(id: int, new_role: str):
    user = await User.query.where(User.id == id).gino.first()
    await user.update(role=new_role).apply()


async def select_by_code(code: str):
    user = await User.query.where(User.code == code).gino.first()
    return user


async def select_managers_admins():
    users = await User.query.where(User.role != "user").gino.all()
    return users


async def get_user_by_refcode(refcode: str):
    user = await User.query.where(User.personal_invite_code == refcode).gino.first()
    return user