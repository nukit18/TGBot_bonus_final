from datetime import date, datetime
from sqlalchemy import sql
from asyncpg import UniqueViolationError

from utils.db_api.db_gino import db
from utils.db_api.schemas.mail import Mail


async def add_mail(id: int, message_id: int, date: date, time: datetime.time):
    try:
        mail = Mail(id=id, message_id=message_id, date=date, time=time)
        await mail.create()

    except UniqueViolationError:
        pass


async def select_all_mails():
    mails = await Mail.query.gino.all()
    return mails


async def delete_mail(id: int, message_id: int):
    mail = await Mail.query.where((Mail.id == id) & (Mail.message_id == message_id)).gino.first()
    await mail.delete()