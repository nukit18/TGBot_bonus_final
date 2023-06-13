import datetime
from aiogram.utils.markdown import quote_html

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from keyboards.default.menu_admin import admin_keyboard_func
from keyboards.inline.admin_keyboards_inline import admin_confirm_text, admin_confirm_time, control_mail_keyboard, \
    view_mails_keyboard
from loader import dp, bot
from utils.db_api.quick_commands import quick_cmd_mail, quick_cmd_user


@dp.message_handler(Text(startswith="Управление рассылками"))
async def start_mailing(message: types.Message, state: FSMContext):
    # проверка зарегистрирован ли пользователь
    user = await quick_cmd_user.select_user(message.from_user.id)
    if user is None:
        await message.answer("Пожалуйста, зарегистрируйтесь. Для этого введите /start")
        return
    # проверка на админку
    if user.role == "user":
        await message.answer("Вы не администратор!")
        return
    await state.set_state("choose_action_mailing")
    await message.answer("Выберите действие:", reply_markup=control_mail_keyboard)


@dp.callback_query_handler(state="choose_action_mailing")
async def choose_action_mailing(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    if call.data == "cancel":
        await bot.send_message(call.from_user.id, "Отменяю")
        await state.reset_data()
        await state.finish()
        return
    if call.data == "add_mail":
        await bot.send_message(call.from_user.id, "Отлично, напишите сообщение для рассылки.\nТакже можете приложить фотографию или видео.")
        await state.set_state("write_mailing")
        return
    mails = await quick_cmd_mail.select_all_mails()
    if len(mails) == 0:
        await bot.send_message(call.from_user.id, "Рассылок нет")
        await state.reset_data()
        await state.finish()
        return
    for mail in mails:
        keyboard = await view_mails_keyboard(str(mail.id) + ":" + str(mail.message_id))
        await bot.send_message(call.from_user.id, f"--------------------------------------\nВремя и дата отправки: {mail.date} {mail.time}")
        await bot.copy_message(chat_id=call.from_user.id, from_chat_id=mail.id, message_id=mail.message_id,
                               reply_markup=keyboard)
    await bot.send_message(call.from_user.id, "Если хотите отменить - отправьте /start")
    await state.set_state("remove_mails")


@dp.callback_query_handler(state="remove_mails")
async def remove_mails(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    keyboard = await admin_keyboard_func(call.from_user.id)
    data = call.data.split(":")
    await quick_cmd_mail.delete_mail(int(data[0]), int(data[1]))
    await bot.send_message(call.from_user.id, "Рассылка удалена", reply_markup=keyboard)
    await state.reset_data()
    await state.finish()


@dp.message_handler(state="write_mailing", content_types=types.ContentType.ANY)
async def write_mailing(message: types.Message, state: FSMContext):
    if message.photo:
        if message.caption is None:
            text = "Отправляем только фото без текста?"
        else:
            text = "Проверьте правильность написания текста и приложение:\n" + message.caption
        await bot.send_photo(message.from_user.id, photo=message.photo[0].file_id, caption=text,
                             reply_markup=admin_confirm_text)
    elif message.video:
        if message.caption is None:
            text = "Отправляем только видео без текста?"
        else:
            text = "Проверьте правильность написания текста и приложение:\n" + message.caption
        await bot.send_video(message.from_user.id, video=message.video.file_id, caption=text,
                             reply_markup=admin_confirm_text)
    else:
        await message.answer("Проверьте правильность написания текста:\n" + message.text, reply_markup=admin_confirm_text)
    await state.update_data(message_id=message.message_id)
    await state.set_state("confirm_text_mailing")


@dp.callback_query_handler(state="confirm_text_mailing")
async def confirm_text_mailing(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    if call.data == "no_text_mail":
        await bot.send_message(call.from_user.id, "Хорошо, отправьте текст\фото\видео заново")
        await state.set_state("write_mailing")
        return
    await bot.send_message(call.from_user.id, "Теперь введите дату отправки сообщения в формате: *ГГГГ-ММ-ДД ЧЧ:ММ*", parse_mode="Markdown")
    await state.set_state("write_mailing_time")


@dp.message_handler(state="write_mailing_time")
async def write_mailing_time(message: types.Message, state: FSMContext):
    try:
        date_time = datetime.datetime.strptime(message.text, "%Y-%m-%d %H:%M")
    except:
        await message.answer("Проверьте правильность написания, формат: *ГГГГ-ММ-ДД ЧЧ:ММ*", parse_mode="Markdown")
        await state.set_state("write_mailing_time")
        return
    if date_time <= datetime.datetime.now():
        await message.answer("Проверьте правильность написания, возможно данная дата уже прошла")
        await state.set_state("write_mailing_time")
        return
    await state.update_data(date_time=date_time)
    await message.answer(f"Время рассылки: <b>{quote_html(message.text)}</b>\nВерно?", parse_mode="HTML",
                         reply_markup=admin_confirm_time)
    await state.set_state("confirm_mailing_time")


@dp.callback_query_handler(state="confirm_mailing_time")
async def confirm_mailing_time(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    if call.data == "no_time_mail":
        await bot.send_message(call.from_user.id, "Хорошо, введите дату и время рассылки заново, формат: *ГГГГ-ММ-ДД ЧЧ:ММ*",
                               parse_mode="Markdown")
        await state.set_state("write_mailing_time")
        return
    elif call.data == "yes_time_mail":
        data = await state.get_data()
        date_time = data.get("date_time")
        await quick_cmd_mail.add_mail(call.from_user.id, data.get("message_id"), date_time.date(), date_time.time())
        await bot.send_message(call.from_user.id, "Отлично, рассылка добавлена!")
    else:
        await bot.send_message(call.from_user.id, "Хорошо, отменяю")
    await state.reset_data()
    await state.finish()