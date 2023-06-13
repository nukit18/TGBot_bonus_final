from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import quote_html

from keyboards.default.menu_admin import admin_keyboard_func
from keyboards.inline.admin_keyboards_inline import choose_action_role_keyboard, admin_get_employee_keyboard, \
    change_employee_role_keyboard, add_employee_keyboard
from loader import dp, bot
from utils.db_api.quick_commands import quick_cmd_user


@dp.callback_query_handler(state="*", text="cancel")
async def cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await state.reset_data()
    await state.finish()
    keyboard = await admin_keyboard_func(call.from_user.id)
    await bot.send_message(call.from_user.id, "Отменяю", reply_markup=keyboard)


@dp.message_handler(Text(equals="Изменить роли сотрудников"))
async def update_balance(message: types.Message, state: FSMContext):
    # проверка зарегистрирован ли пользователь
    user = await quick_cmd_user.select_user(message.from_user.id)
    if user is None:
        await message.answer("Пожалуйста, зарегистрируйтесь. Для этого введите /start")
        return
    # проверка на админку
    if user.role != "admin":
        await message.answer("Вы не администратор!")
        return
    await state.set_state("choose_action_role")
    await message.answer("Выберите необходимое действие:", reply_markup=choose_action_role_keyboard)


@dp.callback_query_handler(state="choose_action_role")
async def choose_action_role(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    if call.data == "add_employee":
        await state.set_state("input_code_add_employee")
        await bot.send_message(call.from_user.id, "Введите реферальный код пользователя, которого хотите добавить (пользователь может получить его отправив команду /refferal")
        return
    await state.set_state("change_role")
    keyboard = await admin_get_employee_keyboard()
    await bot.send_message(call.from_user.id, "Выберите нужного сотрудника из списка для изменения его роли:", reply_markup=keyboard)


# изменение роли
@dp.callback_query_handler(state="change_role")
async def change_role(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    user_id = call.data
    await state.update_data(user_id=user_id)
    user = await quick_cmd_user.select_user(int(user_id))
    text = "Выберите действие:\n" \
           "Сотрудник:\n" \
           f"<b>Имя:</b> {quote_html(user.name)} {quote_html(user.surname)}\n" \
           f"<b>Телефон:</b> {quote_html(user.phone_number)}\n" \
           f"<b>Роль:</b> {quote_html(user.role)}\n" \
           f"<u>При выборе \"изменить роль\" роль сотрудника поменяется автоматически (если стояла роль админ - " \
           f"станет менеджер и наоборот).</u> "
    await state.set_state("action_change_role")
    await bot.send_message(call.from_user.id, text, reply_markup=change_employee_role_keyboard, parse_mode="HTML")


@dp.callback_query_handler(state="action_change_role")
async def action_change_role(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    user = await quick_cmd_user.select_user(int(data.get("user_id")))
    await bot.send_message(call.from_user.id, "Сотрудник:\n"
                                              f"<b>Имя:</b> {quote_html(user.name)} {quote_html(user.surname)}\n"
                                              f"<b>Телефон:</b> {quote_html(user.phone_number)}\n")
    if call.data == "change_role":
        if user.role == "admin":
            await quick_cmd_user.update_role(user.id, "manager")
            await bot.send_message(call.from_user.id, "Роль успешна изменена на Менеджера")
        else:
            await quick_cmd_user.update_role(user.id, "admin")
            await bot.send_message(call.from_user.id, "Роль успешна изменена на Администратора")
    elif call.data == "remove":
        await quick_cmd_user.update_role(user.id, "user")
        await bot.send_message(call.from_user.id, "Роль успешна изменена на обычного покупателя")
    await state.reset_data()
    await state.finish()


# добавление нового сотрундника
@dp.message_handler(state="input_code_add_employee")
async def input_code_add_employee(message: types.Message, state: FSMContext):
    refcode = message.text
    user = await quick_cmd_user.get_user_by_refcode(refcode)
    if not user:
        await message.answer("Пользователь не найден, проверьте правильность кода и отправьте его еще раз")
        return
    await state.update_data(user_id=user.id)
    text = f"Найден пользователь:\n" \
           f"<b>Имя:</b> {quote_html(user.name)} {quote_html(user.surname)}\n" \
           f"<b>Телефон:</b> {quote_html(user.phone_number)}\n" \
           f"Выберите действие:"
    await state.set_state("add_employee_action")
    await message.answer(text, parse_mode="HTML", reply_markup=add_employee_keyboard)


@dp.callback_query_handler(state="add_employee_action")
async def add_employee_action(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    if call.data == "manager":
        await quick_cmd_user.update_role(int(data.get("user_id")), "manager")
        await bot.send_message(call.from_user.id, "Пользователю успешно назначена роль Менеджера")
    elif call.data == "admin":
        await quick_cmd_user.update_role(int(data.get("user_id")), "admin")
        await bot.send_message(call.from_user.id, "Пользователю успешно назначена роль Администратора")
    await state.reset_data()
    await state.finish()
