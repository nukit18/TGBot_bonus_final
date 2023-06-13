from aiogram import executor
from utils.db_api import db_gino, writein_tb_cat_goods_promo
from loader import dp
import middlewares, filters, handlers
import logging

from utils.mailing_scheduler import mailing_schedule
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    logging.getLogger("gino").setLevel(logging.ERROR)
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)

    print("Подключаем БД")
    await db_gino.on_startup(dp)
    print("Готово")

    # print("Чистим БД")
    # await db_gino.db.gino.drop_all()
    # print("Готово")
    #
    # print("Создаем таблицу")
    # await db_gino.db.gino.create_all()
    # print("Готово")
    #
    # print("Создаем 3 категории")
    # await writein_tb_cat_goods_promo.create()
    # print("Готово")

    # задача отправки рассылок
    dp.loop.create_task(mailing_schedule())

    # Уведомляет про запуск
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)

