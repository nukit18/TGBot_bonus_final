import sqlalchemy.dialects.postgresql
from sqlalchemy import Column, BigInteger, sql, Date, Time

from utils.db_api.db_gino import TimedBaseModel


class Mail(TimedBaseModel):
    __tablename__ = 'mail'
    id = Column(BigInteger, primary_key=True)
    message_id = Column(BigInteger, primary_key=True)
    date = Column(Date)
    time = Column(Time)

    query: sql.Select