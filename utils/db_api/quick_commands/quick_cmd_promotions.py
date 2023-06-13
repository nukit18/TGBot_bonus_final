from asyncpg import UniqueViolationError

from data.config import URL_TO_SAVE_PHOTO_PROMO
from utils.db_api.quick_commands import quick_cmd_category_goods
from utils.db_api.schemas.promotions import Promotions


async def add_promo(name: str, text: str, photo_name: str):
    try:
        photo_url = (URL_TO_SAVE_PHOTO_PROMO + photo_name).partition('static\\')[2]
        promo = Promotions(name=name, photo_url=photo_url, text=text)
        await promo.create()

    except UniqueViolationError:
        pass


async def get_last_promo_id():
    promo_ids = await Promotions.select("id").order_by(Promotions.id).gino.all()
    if len(promo_ids) == 0:
        return 0
    return promo_ids[-1][0]


async def check_name_img(full_name_img):
    promo = await Promotions.query.where(Promotions.photo_url == full_name_img).gino.first()
    if promo:
        return True
    return False


async def select_all_promo():
    promotions = await Promotions.query.gino.all()
    return promotions


async def select_promo_by_id(id: int):
    promo = await Promotions.query.where(Promotions.id == id).gino.first()
    return promo


async def remove_promo_by_id(id: int):
    promo = await Promotions.query.where(Promotions.id == id).gino.first()
    await promo.delete()