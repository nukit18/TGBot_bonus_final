from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import PAYMENT_PERCENT
from handlers.users.change_balance import remove_code
from keyboards.default import menu
from keyboards.inline.change_balance_keyboard import change_balance_keyboard, confirm_keyboard, \
    choice_sum_writeoff_keyboard, confirm_points_keyboard
from loader import dp, bot
from utils.db_api.quick_commands import quick_cmd_user


async def change_balance(id_admin: int, code: str, state: FSMContext):
    user = await quick_cmd_user.select_by_code(code)
    await bot.send_message(chat_id=id_admin, text=f"Баланс: *{user.balance}*\nВыберите неодходимое действие", reply_markup=change_balance_keyboard,
                           parse_mode="Markdown")
    await state.update_data(id_user=user.id)
    await state.update_data(code=code)
    await state.update_data(balance=user.balance)
    await state.set_state("change_balance")


@dp.callback_query_handler(text="cancel", state="change_balance")
async def cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Хорошо, возвращаюсь")
    await state.reset_data()
    await state.finish()


@dp.callback_query_handler(text="writeoff", state="change_balance")
async def writeoff(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    if data.get("balance") == 0:
        await bot.send_message(call.from_user.id, "К сожалению, списывать нечего")
        await state.reset_data()
        await state.finish()
        return
    await bot.send_message(call.from_user.id, "Введите сумму покупки покупателя(в рублях, цифрами):")
    await state.set_state("input_sum_purchase")


@dp.message_handler(state="input_sum_purchase")
async def input_sum_purchase(message: types.Message, state: FSMContext):
    try:
        sum = float(message.text.replace(",", "."))
    except:
        await message.answer("Проверьте правильность написания суммы")
        return
    await message.answer(f"Сумма покупки указана верно?\nСумма: *{sum}*", reply_markup=confirm_keyboard, parse_mode="Markdown")
    await state.update_data(sum_purchase=sum)
    await state.set_state("confirm_purchase")


@dp.callback_query_handler(state="confirm_purchase")
async def confirm_purchase(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    if call.data == "no":
        await bot.send_message(call.from_user.id, "Хорошо, введите сумму покупки заново:")
        await state.set_state("input_sum_purchase")
        return
    await bot.send_message(call.from_user.id, "Выберите сколько баллов нужно списать?", reply_markup=choice_sum_writeoff_keyboard)
    await state.set_state("choice_sum_writeoff")


@dp.callback_query_handler(state="choice_sum_writeoff")
async def choice_sum_writeoff(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    user = await quick_cmd_user.select_user(data.get("id_user"))
    if user.code is None or user.code != data.get("code"):
        await bot.send_message(call.from_user.id, "Ошибка! Попросите у покупателя код заново")
        await state.reset_data()
        await state.finish()
        return
    if call.data == "max":
        if user.balance >= int((data.get("sum_purchase"))*PAYMENT_PERCENT):
            balance_to_writeoff = int((data.get("sum_purchase"))*PAYMENT_PERCENT)
        else:
            balance_to_writeoff = user.balance
        await quick_cmd_user.change_balance(user.id, -balance_to_writeoff)
        await bot.send_message(call.from_user.id, f"Баланс обновлен, "
                                                f"сумма покупки после списания баллов: "
                                                f"*{data.get('sum_purchase')-balance_to_writeoff}*",
                               parse_mode="Markdown")
        # удаялем код у пользователя и отправляем ему новый баланс
        await remove_code(user.id)
        keyboard = await menu.menu_keyboard(user.balance-balance_to_writeoff)
        await bot.send_message(user.id, "Баланс обновлен", reply_markup=keyboard)
    elif call.data == "definite":
        await bot.send_message(call.from_user.id,
                               f"Введите количество баллов к списанию, максимальное количество баллов к списанию: *{int((data.get('sum_purchase'))*PAYMENT_PERCENT)}*"
                               f"\nБаланс покупателя: *{user.balance}*",
                               parse_mode="Markdown")
        await state.set_state("input_points_writeoff")
        return
    await state.reset_data()
    await state.finish()


@dp.message_handler(state="input_points_writeoff")
async def input_points_writeoff(message: types.Message, state: FSMContext):
    try:
        sum = int(message.text)
    except:
        await message.answer("Проверьте правильность написания")
        return
    data = await state.get_data()
    user = await quick_cmd_user.select_user(data.get("id_user"))
    if sum > user.balance or sum > int((data.get("sum_purchase"))*PAYMENT_PERCENT):
        await message.answer("Проверьте правильность указания количества")
        return
    await message.answer(f"Количество баллов указано верно?\nВы ввели: *{sum}*", reply_markup=confirm_points_keyboard, parse_mode="Markdown")
    await state.update_data(points_writeoff=sum)
    await state.set_state("confirm_points")
    return


@dp.callback_query_handler(state="confirm_points")
async def confirm_points(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    if call.data == "no_points":
        await state.set_state("input_points_writeoff")
        await bot.send_message(call.from_user.id, "Хорошо, введите количество баллов заново")
        return
    data = await state.get_data()
    user = await quick_cmd_user.select_user(data.get("id_user"))
    if user.code is None or user.code != data.get("code"):
        await bot.send_message(call.from_user.id, "Ошибка! Попросите у покупателя код заново")
        await state.reset_data()
        await state.finish()
        return
    await quick_cmd_user.change_balance(user.id, -data.get("points_writeoff"))
    await bot.send_message(call.from_user.id, f"Баланс обновлен, "
                                              f"сумма покупки после списания баллов: "
                                              f"*{data.get('sum_purchase') - data.get('points_writeoff')}*",
                           parse_mode="Markdown")
    # удаялем код у пользователя и отправляем ему новый баланс
    await remove_code(user.id)
    keyboard = await menu.menu_keyboard(user.balance - data.get('points_writeoff'))
    await bot.send_message(user.id, "Баланс обновлен", reply_markup=keyboard)
    await state.reset_data()
    await state.finish()
