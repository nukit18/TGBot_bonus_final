import secrets

from aiogram import types
from aiogram.utils.markdown import quote_html
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import os

from data.config import URL_TO_SAVE_PHOTO, URL_TO_SAVE_PHOTO_PROMO
from keyboards.default.menu_admin import admin_keyboard_func
from keyboards.inline.admin_keyboards_inline import admin_choose_goods_keyboard, admin_choose_category, \
    confirm_change_goods_promo_keyboard, admin_get_goods_keyboard, admin_get_promotions_keyboard
from loader import dp, bot
from utils.db_api.quick_commands import quick_cmd_user, quick_cmd_category_goods, quick_cmd_goods, quick_cmd_promotions


@dp.message_handler(Text(startswith="Изменить список товаров и акций"))
async def choose_options(message: types.Message, state: FSMContext):
    # проверка зарегистрирован ли пользователь
    user = await quick_cmd_user.select_user(message.from_user.id)
    if user is None:
        await message.answer("Пожалуйста, зарегистрируйтесь. Для этого введите /start")
        return
    # проверка на админку
    if user.role == "user":
        await message.answer("У вас нет доступа!")
        return
    await message.answer("Выберите что хотели бы изменить:", reply_markup=admin_choose_goods_keyboard)
    await state.set_state("choose_change")


# Добавление товара в базу данных
@dp.callback_query_handler(text="add_goods", state="choose_change")
async def add_goods(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    keyboard = await admin_choose_category()
    await bot.send_message(call.from_user.id, "Отлично, выбери категорию, в которую добавить товар:",
                           reply_markup=keyboard)
    await state.set_state("choose_category_add")


@dp.callback_query_handler(state="choose_category_add")
async def choose_category(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await state.update_data(category_id=call.data)
    await bot.send_message(call.from_user.id, "Отлично, напиши название товара")
    await state.set_state("input_name_product_add")


@dp.message_handler(state="input_name_product_add")
async def input_name_product(message: types.Message, state: FSMContext):
    if len(message.text) > 199:
        await message.answer("Слишком длинное название, введи заново")
        return
    await state.update_data(name=message.text)
    await message.answer("Теперь введи цену товара (в рублях):")
    await state.set_state("input_price_product_add")


@dp.message_handler(state="input_price_product_add")
async def input_price_product(message: types.Message, state: FSMContext):
    if len(message.text) > 50:
        await message.answer("Слишком длинная цена, введи заново")
        return
    await state.update_data(price=message.text)
    await message.answer("Теперь введи описание (до 1000 символов):")
    await state.set_state("input_description_product_add")


@dp.message_handler(state="input_description_product_add")
async def input_description_product(message: types.Message, state: FSMContext):
    if len(message.text) > 1000:
        await message.answer("Слишком длинное описание, введи заново")
        return
    await state.update_data(description=message.text)
    await message.answer("Отлично! Отправь фотографию товара:")
    await state.set_state("input_photo_product_add")


@dp.message_handler(state="input_photo_product_add", content_types=types.ContentType.PHOTO)
async def input_photo_product(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("Отправьте, пожалуйста, фотографию")
        return
    while True:
        photo_name = f"{secrets.token_hex(16)}.png"
        check_name = await quick_cmd_goods.check_name_img(URL_TO_SAVE_PHOTO + photo_name)
        if not check_name:
            break
    await message.photo[-1].download(destination_file=URL_TO_SAVE_PHOTO + photo_name)
    await state.update_data(photo_name=photo_name)
    data = await state.get_data()
    category = await quick_cmd_category_goods.select_category(int(data.get("category_id")))
    if len(data.get('description')) > 650:
        await bot.send_photo(message.from_user.id, message.photo[-1].file_id,
                             caption=f"<b>Добавляем данный товар?</b>\n"
                                     f"<b>Название:</b> {quote_html(data.get('name'))}\n"
                                     f"<b>Цена:</b> {quote_html(data.get('price'))} руб.\n"
                                     f"<b>Категория:</b> {quote_html(category.category_name)}\n",
                             parse_mode="HTML")
        await message.answer(f"<b>Описание:</b> {quote_html(data.get('description'))}",
                             reply_markup=confirm_change_goods_promo_keyboard, parse_mode="HTML")
    else:
        await bot.send_photo(message.from_user.id, message.photo[-1].file_id, caption=f"<b>Добавляем данный товар?</b>\n"
                                                                          f"<b>Название:</b> {quote_html(data.get('name'))}\n"
                                                                          f"<b>Цена:</b> {quote_html(data.get('price'))} руб.\n"
                                                                          f"<b>Категория:</b> {quote_html(category.category_name)}\n"
                                                                          f"<b>Описание:</b> {quote_html(data.get('description'))}",
                         reply_markup=confirm_change_goods_promo_keyboard, parse_mode="HTML")
    await state.set_state("confirm_good_add")


@dp.callback_query_handler(state="confirm_good_add")
async def confirm_add_good(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    keyboard = await admin_keyboard_func(call.from_user.id)
    if call.data == "cancel_goods":
        if os.path.isfile(URL_TO_SAVE_PHOTO + data.get('photo_name')):
            os.remove(URL_TO_SAVE_PHOTO + data.get('photo_name'))
        await state.reset_data()
        await state.finish()
        await bot.send_message(call.from_user.id, "*Хорошо, отменяю*", parse_mode="Markdown", reply_markup=keyboard)
        return
    await quick_cmd_goods.add_goods(data.get('name'), data.get('price'), data.get('description'),
                                    data.get('photo_name'), int(data.get('category_id')))
    await state.reset_data()
    await state.finish()
    await bot.send_message(call.from_user.id, "*Товар успешно добавлен!*", parse_mode="Markdown", reply_markup=keyboard)


# удаление товаров из бд
@dp.callback_query_handler(text="remove_goods", state="choose_change")
async def remove_goods(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    keyboard = await admin_choose_category()
    await bot.send_message(call.from_user.id, "Отлично, выбери категорию в которой находится товар:",
                           reply_markup=keyboard)
    await state.set_state("choose_category_remove")


@dp.callback_query_handler(state="choose_category_remove")
async def choose_category_remove(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    keyboard = await admin_get_goods_keyboard(int(call.data))
    await bot.send_message(call.from_user.id, "Теперь выбери товар, который нужно удалить:", reply_markup=keyboard)
    await state.set_state("choose_goods_remove")


@dp.callback_query_handler(state="choose_goods_remove")
async def choose_goods_remove(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    product = await quick_cmd_goods.select_product_by_id(int(call.data))
    await state.update_data(product_id=call.data)
    photo_url = URL_TO_SAVE_PHOTO.partition('static')[0] + "static\\" + product.photo_url
    try:
        photo = open(f"{photo_url}", 'rb')
        if len(product.description) > 650:
            await bot.send_photo(call.from_user.id, photo=photo, caption=f"<b>Удаляем данный товар?</b>\n"
                                                                     f"<b>Название:</b> {quote_html(product.name)}\n"
                                                                     f"<b>Цена:</b> {quote_html(product.price)}\n",
                             parse_mode="HTML")
            await bot.send_message(call.from_user.id, f"<b>Описание:</b> {quote_html(product.description)}",
                             reply_markup=confirm_change_goods_promo_keyboard, parse_mode="HTML")
        else:
            await bot.send_photo(call.from_user.id, photo=photo, caption=f"<b>Удаляем данный товар?</b>\n"
                                                                         f"<b>Название:</b> {quote_html(product.name)}\n"
                                                                         f"<b>Цена:</b> {quote_html(product.price)}\n"
                                                                         f"<b>Описание:</b> {quote_html(product.description)}",
                                 reply_markup=confirm_change_goods_promo_keyboard, parse_mode="HTML")
        photo.close()
    except Exception as e:
        await bot.send_message(call.from_user.id, text=f"<b>Удаляем данный товар?</b>\n"
                                                          f"<b>Фото отсутствует</b>\n"
                                                          f"<b>Название:</b> {quote_html(product.name)}\n"
                                                          f"<b>Цена:</b> {quote_html(product.price)}\n"
                                                          f"<b>Описание:</b> {quote_html(product.description)}",
                             reply_markup=confirm_change_goods_promo_keyboard, parse_mode="HTML")
    await state.update_data(photo_url=photo_url)
    await state.set_state("confirm_good_remove")


@dp.callback_query_handler(state="confirm_good_remove")
async def confirm_good_remove(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    keyboard = await admin_keyboard_func(call.from_user.id)
    if call.data == "cancel_goods":
        await state.reset_data()
        await state.finish()
        await bot.send_message(call.from_user.id, "*Хорошо, отменяю*", parse_mode="Markdown", reply_markup=keyboard)
        return
    data = await state.get_data()
    if os.path.isfile(data.get('photo_url')):
        os.remove(data.get('photo_url'))
    await quick_cmd_goods.remove_product_by_id(int(data.get('product_id')))
    await state.reset_data()
    await state.finish()
    await bot.send_message(call.from_user.id, "*Товар успешно удален!*", parse_mode="Markdown", reply_markup=keyboard)


# Добавление акции
@dp.callback_query_handler(text="add_promo", state="choose_change")
async def add_promo(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Напишите название вашей акции:")
    await state.set_state("input_name_promo_add")


@dp.message_handler(state="input_name_promo_add")
async def input_name_promo_add(message: types.Message, state: FSMContext):
    if len(message.text) > 199:
        await message.answer("Название должно быть меньше 200 символов, введите еще раз")
        return
    await state.update_data(name=message.text)
    await message.answer("Отлично, введите описание для акции")
    await state.set_state("input_text_promo_add")


@dp.message_handler(state="input_text_promo_add")
async def input_text_promo_add(message: types.Message, state: FSMContext):
    if len(message.text) > 999:
        await message.answer("Максимальное количество символов в описании - 1000. Введите еще раз")
        return
    await state.update_data(text=message.text)
    await message.answer("Отправьте фотографию для вашей акции")
    await state.set_state("input_photo_promo_add")


@dp.message_handler(state="input_photo_promo_add", content_types=types.ContentType.PHOTO)
async def input_photo_promo_add(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("Отправьте, пожалуйста, фотографию")
        return
    while True:
        photo_name = f"{secrets.token_hex(16)}.png"
        check_name = await quick_cmd_promotions.check_name_img(URL_TO_SAVE_PHOTO_PROMO + photo_name)
        if not check_name:
            break
    await message.photo[-1].download(destination_file=URL_TO_SAVE_PHOTO_PROMO + photo_name)
    await state.update_data(photo_name=photo_name)
    data = await state.get_data()
    if len(data.get('text')) > 700:
        await bot.send_photo(message.from_user.id, message.photo[-1].file_id, caption="<b>Добавляем данную акцию?</b>\n"
                                                                                      f"<b>Название:</b> {quote_html(data.get('name'))}\n",
                             parse_mode="HTML")
        await message.answer(f"<b>Описание:</b> {quote_html(data.get('text'))}\n",
                             reply_markup=confirm_change_goods_promo_keyboard, parse_mode="HTML")
    else:
        await bot.send_photo(message.from_user.id, message.photo[-1].file_id, caption="<b>Добавляем данную акцию?</b>\n"
                                                                          f"<b>Название:</b> {quote_html(data.get('name'))}\n"
                                                                          f"<b>Описание:</b> {quote_html(data.get('text'))} руб.\n",
                         reply_markup=confirm_change_goods_promo_keyboard, parse_mode="HTML")
    await state.set_state("confirm_promo_add")


@dp.callback_query_handler(state="confirm_promo_add")
async def confirm_promo_add(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    keyboard = await admin_keyboard_func(call.from_user.id)
    if call.data == "cancel_goods":
        if os.path.isfile(URL_TO_SAVE_PHOTO_PROMO + data.get('photo_name')):
            os.remove(URL_TO_SAVE_PHOTO_PROMO + data.get('photo_name'))
        await state.reset_data()
        await state.finish()
        await bot.send_message(call.from_user.id, "*Хорошо, отменяю*", parse_mode="Markdown", reply_markup=keyboard)
        return
    await quick_cmd_promotions.add_promo(data.get('name'), data.get('text'), data.get('photo_name'))
    await state.reset_data()
    await state.finish()
    await bot.send_message(call.from_user.id, "*Акция успешно добавлена!*", parse_mode="Markdown", reply_markup=keyboard)


# Удаление акции
@dp.callback_query_handler(text="remove_promo", state="choose_change")
async def remove_promo(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    keyboard = await admin_get_promotions_keyboard()
    await bot.send_message(call.from_user.id, "Выберите акцию, которую нужно удалить:", reply_markup=keyboard)
    await state.set_state("choose_promo_remove")


@dp.callback_query_handler(state="choose_promo_remove")
async def choose_promo_remove(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    id = int(call.data)
    await state.update_data(id=id)
    promo = await quick_cmd_promotions.select_promo_by_id(id)
    photo_url = URL_TO_SAVE_PHOTO_PROMO.partition('static')[0] + "static\\" + promo.photo_url
    try:
        photo = open(f"{photo_url}", 'rb')
        if len(promo.text) > 700:
            await bot.send_photo(call.from_user.id, photo=photo, caption=f"<b>Удаляем данную акцию?</b>\n"
                                                                         f"<b>Название:</b> {quote_html(promo.name)}\n",
                                 parse_mode="HTML")
            await bot.send_message(f"<b>Описание:</b> {quote_html(promo.text)}\n",
                                 reply_markup=confirm_change_goods_promo_keyboard, parse_mode="HTML")
        else:
            await bot.send_photo(call.from_user.id, photo=photo, caption=f"<b>Удаляем данную акцию?</b>\n"
                                                                     f"<b>Название:</b> {quote_html(promo.name)}\n"
                                                                     f"<b>Описание:</b> {quote_html(promo.text)}\n",
                             reply_markup=confirm_change_goods_promo_keyboard, parse_mode="HTML")
        photo.close()
    except Exception as e:
        await bot.send_message(call.from_user.id, text=f"<b>Удаляем данную акцию?</b>\n"
                                                       f"<b>Фотография отсутствует</b>\n"
                                                        f"<b>Название:</b> {quote_html(promo.name)}\n"
                                                        f"<b>Описание:</b> {quote_html(promo.text)}\n",
                               reply_markup=confirm_change_goods_promo_keyboard, parse_mode="HTML")
    await state.update_data(photo_url=photo_url)
    await state.set_state("confirm_promo_remove")


@dp.callback_query_handler(state="confirm_promo_remove")
async def confirm_promo_remove(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    keyboard = await admin_keyboard_func(call.from_user.id)
    if call.data == "cancel_goods":
        await state.reset_data()
        await state.finish()
        await bot.send_message(call.from_user.id, "*Хорошо, отменяю*", parse_mode="Markdown", reply_markup=keyboard)
        return
    data = await state.get_data()
    if os.path.isfile(data.get('photo_url')):
        os.remove(data.get('photo_url'))
    await quick_cmd_promotions.remove_promo_by_id(int(data.get('id')))
    await state.reset_data()
    await state.finish()
    await bot.send_message(call.from_user.id, "*Акция успешно удалена!*", parse_mode="Markdown", reply_markup=keyboard)

