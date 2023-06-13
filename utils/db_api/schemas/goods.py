import sqlalchemy.dialects.postgresql
from sqlalchemy import Column, BigInteger, sql, String

from utils.db_api.db_gino import TimedBaseModel


class Goods(TimedBaseModel):
    __tablename__ = 'goods'
    id = Column(BigInteger, primary_key=True)
    category = Column(String(50))
    category_name = Column(String(100))
    photo_url = Column(String(200))
    name = Column(String(200))
    price = Column(String(50))
    description = Column(String(1000))

    query: sql.Select