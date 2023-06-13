import asyncio
import datetime

from loader import bot, dp
from utils.db_api.quick_commands import quick_cmd_mail, quick_cmd_user


async def mailing_schedule():
    await asyncio.sleep(0)
    print("Запускаем скрипт отправки рассылок")
    while True:
        await send_mailing()
        await asyncio.sleep(30)


async def send_mailing():
    mails = await quick_cmd_mail.select_all_mails()
    for mail in mails:
        if datetime.datetime.now().strftime("%Y-%m-%d") == mail.date.strftime("%Y-%m-%d") and datetime.datetime.now().strftime("%H:%M") == mail.time.strftime("%H:%M"):
            users = await quick_cmd_user.select_all_users()
            for user in users:
                if user.role == "user":
                    try:
                        await bot.copy_message(chat_id=user.id, from_chat_id=mail.id, message_id=mail.message_id)
                    except:
                        pass
            await quick_cmd_mail.delete_mail(mail.id, mail.message_id)