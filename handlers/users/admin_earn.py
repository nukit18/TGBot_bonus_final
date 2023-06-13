from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from data.config import PAYMENT_PERCENT, EARN_PERCENT
from handlers.users.change_balance import remove_code
from keyboards.default import send_number_phone, menu
from keyboards.inline.change_balance_keyboard import change_balance_keyboard, confirm_keyboard, \
    choice_sum_writeoff_keyboard, confirm_points_keyboard, confirm_earn_keyboard
from loader import dp, bot
from utils.db_api.quick_commands import quick_cmd_user


@dp.callback_query_handler(text="cancel", state="confirm_earn")
async def cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Хорошо, возвращаюсь")
    await state.reset_data()
    await state.finish()


@dp.callback_query_handler(text="earn", state="change_balance")
async def writeoff(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Введите сумму покупки: ")
    await state.set_state("input_sum_earn")


@dp.message_handler(state="input_sum_earn")
async def input_sum_earn(message: types.Message, state: FSMContext):
    try:
        sum = float(message.text.replace(",", "."))
        points = int(sum*EARN_PERCENT)
    except:
        await message.answer("Проверьте правильность написания суммы")
        return
    await message.answer(f"Сумма покупки: *{sum}*\nПокупателю начислиться: *{points}*", reply_markup=confirm_earn_keyboard,
                         parse_mode="Markdown")
    await state.update_data(points=points)
    await state.set_state("confirm_earn")


@dp.callback_query_handler(state="confirm_earn")
async def confirm_earn(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    if call.data == "earn_yes":
        # начисление
        data = await state.get_data()
        user = await quick_cmd_user.select_user(data.get("id_user"))
        # проверка что код еще действует
        if user.code is None or user.code != data.get("code"):
            await bot.send_message(call.from_user.id, "Ошибка! Попросите у покупателя код заново")
            await state.reset_data()
            await state.finish()
            return
        await quick_cmd_user.change_balance(user.id, data.get("points"))
        await bot.send_message(call.from_user.id, f"Баллы начислены, баланс покупателя: *{user.balance+data.get('points')}*", parse_mode="Markdown")
        # уведомляем пользователя и удаляем его код
        await remove_code(user.id)
        keyboard = await menu.menu_keyboard(user.balance + data.get('points'))
        await bot.send_message(user.id, "Баланс обновлен", reply_markup=keyboard)
    elif call.data == "earn_no":
        # повторный ввод суммы
        await state.set_state("input_sum_earn")
        await bot.send_message(call.from_user.id, "Напишите сумму покупки:")
        return
    await state.reset_data()
    await state.finish()
