from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from data.config import ADD_REFFERAL, ADD_REFFER
from keyboards.default import menu
from keyboards.inline.refferal_choose_keyboard import get_refferal_option_keyboard
from loader import dp, bot
from utils.db_api.quick_commands import quick_cmd_user


@dp.message_handler(Command("refferal"))
async def refferal(message: types.Message, state: FSMContext):
    # проверка зарегистрирован ли пользователь
    user = await quick_cmd_user.select_user(message.from_user.id)
    if user is None:
        await message.answer("Пожалуйста, зарегистрируйтесь. Для этого введите /start")
        return
    # проверка на админку
    if user.role != "user":
        await message.answer("Вы не пользователь!")
        return
    keyboard = await get_refferal_option_keyboard(message.from_user.id)
    await state.set_state("choose_refferal_option")
    text = f"Привет, условия акции просты - приглашай друзей и получайте баллы. За каждого приглашенного ты получишь {ADD_REFFER} баллов, а тот, кого ты приглашаешь получит првественный бонус в размере {ADD_REFFERAL} баллов. Выбери, необходимое действие:"
    await message.answer(text, reply_markup=keyboard)


@dp.callback_query_handler(state="choose_refferal_option", text="reffer")
async def choose_refferal_option(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    user = await quick_cmd_user.select_user(call.from_user.id)
    keyboard = await menu.menu_keyboard(user.balance)
    await bot.send_message(call.from_user.id, f"Твой код для приглашения:\n<u>{user.personal_invite_code}</u>", parse_mode="HTML", reply_markup=keyboard)
    await state.reset_data()
    await state.finish()


@dp.message_handler(state="input_code_refferal")
async def input_code_refferal(message: types.Message, state: FSMContext):
    if len(message.text) > 99:
        await message.answer("Ошибка, введи покороче")
        return
    success = await quick_cmd_user.update_invite_code_activate(message.from_user.id, message.text)
    user = await quick_cmd_user.select_user(message.from_user.id)
    keyboard = await menu.menu_keyboard(user.balance)
    if success:
        await message.answer("Отлично, баллы были начислены на оба аккаунта!", reply_markup=keyboard)
    else:
        await message.answer("Проверь правильность кода и повтори еще раз.", reply_markup=keyboard)
        return
    await state.reset_data()
    await state.finish()