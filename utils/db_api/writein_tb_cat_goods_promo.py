import asyncio

from data import config
from utils.db_api.quick_commands import quick_cmd_promotions, quick_cmd_category_goods, quick_cmd_goods
from utils.db_api.db_gino import db


async def create():
    # await db.set_bind(config.POSTGRES_URI)
    # await db.gino.drop_all()
    # await db.gino.create_all()

    # print('Добавляем акции с фото')
    # photo_name = "promo1.jpg"
    # text = "Объявляем масшатбную акцию на весь ассортимент 50%. Объявляем масшатбную акцию на весь ассортимент 50%. Объявляем масшатбную акцию на весь ассортимент 50%. Объявляем масшатбную акцию на весь ассортимент 50%. Объявляем масшатбную акцию на весь ассортимент 50%. Объявляем масшатбную акцию на весь ассортимент 50%. Объявляем масшатбную акцию на весь ассортимент 50%."
    # await quick_cmd_promotions.add_promo("Акция 50% на все!", text, photo_name)
    # photo_name = "promo2.jpg"
    # text = "Объявляем масшатбную акцию на весь ассортимент 50%. Объявляем масшатбную акцию на весь ассортимент 50%. Объявляем масшатбную акцию на весь ассортимент 50%. Объявляем масшатбную акцию на весь ассортимент 50%. Объявляем масшатбную акцию на весь ассортимент 50%. Объявляем масшатбную акцию на весь ассортимент 50%. Объявляем масшатбную акцию на весь ассортимент 50%."
    # await quick_cmd_promotions.add_promo("Акция 50% на айфоны!", text, photo_name)

    print("Создаем 3 категории товаров")
    await quick_cmd_category_goods.add_category_goods(1, "category_1", "Электроника")
    await quick_cmd_category_goods.add_category_goods(2, "category_2", "Красота и здоровье")
    await quick_cmd_category_goods.add_category_goods(3, "category_3", "Аксессуары")

    # print('Добавляем товары с фото')
    # photo_name = "iphone11.png"
    # await quick_cmd_goods.add_goods(1, "IPhone 11 White", "24990",
    #                                 "Iphone 11 128gb white Iphone 11 128gb white Iphone 11 128gb white Iphone 11 128gb white Iphone 11 128gb white Iphone 11 128gb white Iphone 11 128gb whiteIphone 11 128gb white",
    #                                 photo_name, 1)
    # photo_name = "iphone12.jpg"
    # await quick_cmd_goods.add_goods(2, "IPhone 12 Black", "32990", "IPhone 12 256GB black edition", photo_name, 2)
    #
    # photo_name = "iphone11.png"
    # await quick_cmd_goods.add_goods(3, "IPhone 11 White", "34999",
    #                                 "Iphone 11 128gb white Iphone 11 128gb white Iphone 11 128gb white Iphone 11 128gb white Iphone 11 128gb white Iphone 11 128gb white Iphone 11 128gb whiteIphone 11 128gb white",
    #                                 photo_name, 3)



# loop = asyncio.get_event_loop()
# loop.run_until_complete(create())