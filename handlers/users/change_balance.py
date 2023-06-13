import asyncio

from aiogram.dispatcher.filters import Text
from aiogram import types

from data.config import BOT_NAME, SEC_TO_DEL
from keyboards.default import menu
from loader import dp, bot
from utils.db_api.quick_commands import quick_cmd_user
import qrcode
import os


# удаляет код и сообщение
async def remove_code(id: int):
    user = await quick_cmd_user.select_user(id)
    if user.msg_id_code:
        await bot.delete_message(user.id, user.msg_id_code)
        await quick_cmd_user.delete_code(id)


@dp.message_handler(Text(equals="Показать код"))
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
    # удаляет старый код и сообщение, если есть
    await remove_code(message.from_user.id)
    # генерация и отправка qr-кода
    await quick_cmd_user.generate_code(message.from_user.id)
    user = await quick_cmd_user.select_user(message.from_user.id)
    code = user.code
    data = f"https://t.me/{BOT_NAME}?start={code}"
    filename = f"{code}.png"
    img = qrcode.make(data)
    img.save(f'qrcodes/{filename}')
    photo = open(f'qrcodes/{code}.png', 'rb')
    msg = await message.answer_photo(photo, caption=f"Данный код одноразовый и будет дейстовать {SEC_TO_DEL} секунд")
    await quick_cmd_user.update_msg_id(user.id, msg.message_id)
    os.remove(f'qrcodes/{code}.png')
    # запуск удаления сообщения через n-секунд
    for i in range(1, SEC_TO_DEL+1):
        await asyncio.sleep(1)
        user = await quick_cmd_user.select_user(message.from_user.id)
        if user.code != code:
            return
        await bot.edit_message_caption(chat_id=user.id, message_id=msg.message_id,
                                       caption=f"Данный код одноразовый и будет дейстовать {SEC_TO_DEL - i} секунд")
    await remove_code(message.from_user.id)