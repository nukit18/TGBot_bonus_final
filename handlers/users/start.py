from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from handlers.users.admin_writeoff import change_balance
from keyboards.default import send_number_phone, menu
from keyboards.default.menu_admin import admin_keyboard_func
from keyboards.inline.refferal_choose_keyboard import refferal_input_confirm_keyboard
from loader import dp, bot
from utils.db_api.quick_commands import quick_cmd_user


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await state.reset_data()
    await state.finish()
    user = await quick_cmd_user.select_user(message.from_user.id)
    if user is not None:
        # проверка на админку
        if user.role != "user":
            args = message.get_args()
            codes = await quick_cmd_user.get_codes()
            if args not in codes:
                keyboard = await admin_keyboard_func(message.from_user.id)
                await message.answer("Добро пожаловать!", reply_markup=keyboard)
                return
            await change_balance(message.from_user.id, str(args), state)
            return
        # отдаем главное меню
        user = await quick_cmd_user.select_user(message.from_user.id)
        keyboard = await menu.menu_keyboard(user.balance)
        await message.answer(f"Привет, {message.from_user.full_name}!", reply_markup=keyboard)
    else:
        # регистрация
        await message.answer(f"Привет, {message.from_user.full_name}!")
        await state.set_state("input_phone")
        await message.answer(f"Давай познакомимся, отправь свой номер телефона по кнопке ниже.",
                             reply_markup=send_number_phone.keyboard)


@dp.message_handler(state="input_phone")
async def reg_phone_wrong(message: types.Message, state: FSMContext):
    await message.answer("Отправь телефон именно по кнопке ниже",
                         reply_markup=send_number_phone.keyboard)


@dp.message_handler(content_types=types.ContentType.CONTACT, state="input_phone")
async def registration_phone(message: types.Message, state: FSMContext):
    if len(message.contact.phone_number) > 99:
        await message.answer("Ошибка, введи покороче")
        return
    await state.update_data(phone=message.contact.phone_number)
    await message.answer("Отлично, теперь введи свое Имя:")
    await state.set_state("input_name")


@dp.message_handler(state="input_name")
async def registration_name(message: types.Message, state: FSMContext):
    if len(message.text) > 99:
        await message.answer("Ошибка, введи покороче")
        return
    await state.update_data(name=message.text)
    await message.answer("Введи свою Фамилию:")
    await state.set_state("input_surname")


@dp.message_handler(state="input_surname")
async def registration_surname(message: types.Message, state: FSMContext):
    if len(message.text) > 99:
        await message.answer("Ошибка, введи покороче")
        return
    surname = message.text
    data = await state.get_data()
    await quick_cmd_user.add_user(id=message.from_user.id, phone_number=data.get("phone"),
                                  name=data.get("name"), surname=surname)
    # высылаем меню

    await state.set_state("choose_input_code_refferal")
    await message.answer("У вас есть пригласительный код?", reply_markup=refferal_input_confirm_keyboard)


@dp.callback_query_handler(state="choose_input_code_refferal")
async def choose_input_code_refferal(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    if call.data == "no_refferal":
        user = await quick_cmd_user.select_user(call.from_user.id)
        keyboard = await menu.menu_keyboard(user.balance)
        await bot.send_message(chat_id=call.from_user.id, text="Хорошо, спасибо за регистрацию!", reply_markup=keyboard)
        await state.reset_data()
        await state.finish()
        return
    await state.set_state("input_code_refferal")
    await bot.send_message(chat_id=call.from_user.id, text="Хорошо, отправь мне, пожалуйста, твой пригласительный код.")




