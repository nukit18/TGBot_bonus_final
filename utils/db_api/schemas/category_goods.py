import sqlalchemy.dialects.postgresql
from sqlalchemy import Column, BigInteger, sql, String

from utils.db_api.db_gino import TimedBaseModel


class CategoryGoods(TimedBaseModel):
    __tablename__ = 'category_goods'
    id = Column(BigInteger, primary_key=True)
    category = Column(String(50))
    category_name = Column(String(100))

    query: sql.Select