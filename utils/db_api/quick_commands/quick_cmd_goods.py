from asyncpg import UniqueViolationError

from data.config import URL_TO_SAVE_PHOTO
from utils.db_api.quick_commands import quick_cmd_category_goods
from utils.db_api.schemas.goods import Goods


async def add_goods(name: str, price: str, description: str, photo_name: str, category_id: int):
    try:
        photo_url = (URL_TO_SAVE_PHOTO + photo_name).partition('static\\')[2]
        category_model = await quick_cmd_category_goods.select_category(category_id)
        goods = Goods(name=name, price=price, description=description, photo_url=photo_url,
                      category=category_model.category, category_name=category_model.category_name)
        await goods.create()

    except UniqueViolationError:
        pass


async def get_last_product_id():
    goods_ids = await Goods.select("id").order_by(Goods.id).gino.all()
    if len(goods_ids) == 0:
        return 0
    print(goods_ids)
    return goods_ids[-1][0]


async def check_name_img(full_name_img):
    goods = await Goods.query.where(Goods.photo_url == full_name_img).gino.first()
    if goods:
        return True
    return False


async def get_goods_by_category_id(category_id: int):
    category = await quick_cmd_category_goods.select_category(category_id)
    goods = await Goods.query.where(Goods.category == category.category).gino.all()
    return goods


async def select_product_by_id(id: int):
    product = await Goods.query.where(Goods.id == id).gino.first()
    return product


async def remove_product_by_id(id: int):
    product = await Goods.query.where(Goods.id == id).gino.first()
    await product.delete()