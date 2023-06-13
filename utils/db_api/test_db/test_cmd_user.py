import asyncio

from data import config
from utils.db_api.quick_commands import quick_cmd_user
from utils.db_api.db_gino import db


async def test():
    await db.set_bind(config.POSTGRES_URI)
    await db.gino.drop_all()
    await db.gino.create_all()

    print("Добавляем пользователей")
    await quick_cmd_user.add_user(1, "+79194794816", "Никита", "Бабин")
    await quick_cmd_user.add_user(3245346, "+79194794813", "Саня", "Иванов")
    await quick_cmd_user.add_user(34645654, "+79194794814", "Семен", "Бабин", 0, "admin")
    await quick_cmd_user.add_user(15473289, "+79194794815", "Иван", "Бабин")
    await quick_cmd_user.add_user(34534843, "+79194794817", "Олег", "Бабин")
    print("Пользователи добавлены!")
    print("----------------------------------------")

    print("Получаем всех пользователей")
    users = await quick_cmd_user.select_all_users()
    print("Все пользователи:\n", [user.name for user in users])
    print("id Первого и 3 пользователя:\n", users[0], users[2])
    print("Баланс первого:", users[0].balance)
    print("----------------------------------------")

    print("Получаем айди всех пользователей:\n", await quick_cmd_user.get_ids())
    print("----------------------------------------")

    print("Выбираем пользователя по айди:",
          await quick_cmd_user.select_user(1))
    print("----------------------------------------")

    print("Выбираем пользователя по номеру телефона: ",
          await quick_cmd_user.select_by_phone("+79194794817"))
    print("----------------------------------------")

    print("Меняем баланс в 1 пользователе")
    print("Увеличиваем на 500")
    await quick_cmd_user.change_balance(1, 500)
    print("Текущий баланс:",
          (await quick_cmd_user.select_user(1)).balance)
    print("Уменьшем на 200")
    await quick_cmd_user.change_balance(1, -200)
    print("Текущий баланс:",
          (await quick_cmd_user.select_user(1)).balance)
    print("----------------------------------------")
    print("Запрос пользоваетля которого нет в системе")
    print(await quick_cmd_user.select_user(777))

    print("----------------------------------------")
    print("Проверяем генерацию токенов, генерируем для трех пользователей токены, для одного удаляем")
    await quick_cmd_user.generate_code(1)
    await quick_cmd_user.generate_code(34645654)
    await quick_cmd_user.generate_code(3245346)
    await quick_cmd_user.delete_code(3245346)

    print("----------------------------------------")
    print("Делаем двух пользователей админами и у одного забираем права")
    print(await quick_cmd_user.get_role(1))
    print(await quick_cmd_user.get_role(34645654))




loop = asyncio.get_event_loop()
loop.run_until_complete(test())