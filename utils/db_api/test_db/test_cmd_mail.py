import asyncio
import datetime

from data import config
from utils.db_api.quick_commands import quick_cmd_mail
from utils.db_api.db_gino import db


async def test():
    await db.set_bind(config.POSTGRES_URI)
    await db.gino.drop_all()
    await db.gino.create_all()

    print("Добавляем рассылки")
    date_time = datetime.datetime.strptime('2022-02-02 12:25', "%Y-%m-%d %H:%M")
    await quick_cmd_mail.add_mail(1, 1, date_time.date(), date_time.time())
    await quick_cmd_mail.add_mail(1, 2, datetime.date(day=28, month=7, year=14), datetime.time(hour=5, minute=24))
    await quick_cmd_mail.add_mail(2, 2, datetime.date(day=30, month=6, year=10), datetime.time(hour=20, minute=24))
    await quick_cmd_mail.add_mail(2, 3, datetime.date(day=30, month=5, year=22), datetime.time(hour=15, minute=24))

    mails = await quick_cmd_mail.select_all_mails()
    for mail in mails:
        print(mail.id, mail.message_id, mail.date, mail.time)

    print("Удаляем одну запись")
    await quick_cmd_mail.delete_mail(1, 2)
    mails = await quick_cmd_mail.select_all_mails()
    for mail in mails:
        print(mail.id, mail.message_id, mail.date, mail.time)


loop = asyncio.get_event_loop()
loop.run_until_complete(test())