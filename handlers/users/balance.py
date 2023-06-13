from aiogram.dispatcher.filters import Text
from aiogram import types
from keyboards.default import menu
from loader import dp
from utils.db_api.quick_commands import quick_cmd_user


@dp.message_handler(Text(startswith="Баланс:"))
async def update_balance(message: types.Message):
    # проверка зарегистрирован ли пользователь
    user = await quick_cmd_user.select_user(message.from_user.id)
    if user is None:
        await message.answer("Пожалуйста, зарегистрируйтесь. Для этого введите /start")
        return
    # проверка на админку
    if user.role != "user":
        await message.answer("Вы не пользователь!")
        return
    # отправка клавиатуры с новым балансом
    keyboard = await menu.menu_keyboard(user.balance)
    await message.answer("Баланс обновлен", reply_markup=keyboard)