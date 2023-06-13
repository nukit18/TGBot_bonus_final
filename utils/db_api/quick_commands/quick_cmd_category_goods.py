import asyncio

from asyncpg import UniqueViolationError

from data import config
from utils.db_api.db_gino import db
from utils.db_api.schemas.category_goods import CategoryGoods


async def add_category_goods(id: int, category: str, category_name: str):
    try:
        catogory_goods = CategoryGoods(id=id, category=category, category_name=category_name)
        await catogory_goods.create()

    except UniqueViolationError:
        pass


async def select_category(id: int):
    category = await CategoryGoods.query.where(CategoryGoods.id == id).gino.first()
    return category


async def select_categories():
    categories = await CategoryGoods.query.gino.all()
    return categories