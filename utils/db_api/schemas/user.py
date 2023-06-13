import sqlalchemy.dialects.postgresql
from sqlalchemy import Column, BigInteger, String, sql, Date, Boolean

from utils.db_api.db_gino import TimedBaseModel


class User(TimedBaseModel):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    phone_number = Column(String(100))
    personal_invite_code = Column(String(100))
    invite_code_is_active = Column(Boolean)
    name = Column(String(100))
    surname = Column(String(100))
    balance = Column(BigInteger)
    code = Column(String(100))
    msg_id_code = Column(BigInteger)
    role = Column(String(10))

    query: sql.Select