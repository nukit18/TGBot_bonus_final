from sqlalchemy import Column, BigInteger, sql, String

from utils.db_api.db_gino import TimedBaseModel


class Promotions(TimedBaseModel):
    __tablename__ = 'promotions'
    id = Column(BigInteger, primary_key=True)
    photo_url = Column(String(200))
    name = Column(String(200))
    text = Column(String(1000))

    query: sql.Select