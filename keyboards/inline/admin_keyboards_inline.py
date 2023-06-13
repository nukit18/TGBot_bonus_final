from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.db_api.quick_commands import quick_cmd_category_goods, quick_cmd_goods, quick_cmd_promotions, quick_cmd_user, \
    quick_cmd_mail

admin_confirm_text = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Все верно", callback_data="yes_text_mail")
        ],
        [
            InlineKeyboardButton(text="Нет, изменить", callback_data="no_text_mail")
        ]
    ]
)

admin_confirm_time = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Все верно", callback_data="yes_time_mail")
        ],
        [
            InlineKeyboardButton(text="Нет, изменить", callback_data="no_time_mail")
        ],
        [
            InlineKeyboardButton(text="Отменить рассылку", callback_data="cancel_mailing")
        ]
    ]
)

admin_choose_goods_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить товар", callback_data="add_goods")
        ],
        [
            InlineKeyboardButton(text="Удалить товар", callback_data="remove_goods")
        ],
        [
            InlineKeyboardButton(text="Добавить акцию", callback_data="add_promo")
        ],
        [
            InlineKeyboardButton(text="Удалить акцию", callback_data="remove_promo")
        ]
    ]
)


async def admin_choose_category():
    categories = await quick_cmd_category_goods.select_categories()
    inline_keyboard = []
    for category in categories:
        inline_keyboard.append([InlineKeyboardButton(text=category.category_name, callback_data=category.id)])
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard


confirm_change_goods_promo_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Все верно", callback_data="yes_goods")
        ],
        [
            InlineKeyboardButton(text="Отменить", callback_data="cancel_goods")
        ]
    ]
)


async def admin_get_goods_keyboard(category_id: int):
    goods = await quick_cmd_goods.get_goods_by_category_id(category_id)
    inline_keyboard = []
    for item in goods:
        inline_keyboard.append([InlineKeyboardButton(text=item.name, callback_data=item.id)])
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard


async def admin_get_promotions_keyboard():
    promotions = await quick_cmd_promotions.select_all_promo()
    inline_keyboard = []
    for item in promotions:
        inline_keyboard.append([InlineKeyboardButton(text=item.name, callback_data=item.id)])
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard


async def admin_get_employee_keyboard():
    employees = await quick_cmd_user.select_managers_admins()
    inline_keyboard = []
    for user in employees:
        text = f"Имя: {user.name}\n" \
               f"Телефон: {user.phone_number}\n" \
               f"Роль: {user.role}"
        inline_keyboard.append([InlineKeyboardButton(text=text, callback_data=user.id)])
    inline_keyboard.append([InlineKeyboardButton(text="Отменить", callback_data="cancel")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard


choose_action_role_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить сотрудника", callback_data="add_employee")
        ],
        [
            InlineKeyboardButton(text="Изменить роли сотрудников", callback_data="change_roles")
        ]
    ]
)


change_employee_role_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Изменить роль", callback_data="change_role")
        ],
        [
            InlineKeyboardButton(text="Удалить", callback_data="remove")
        ],
        [
            InlineKeyboardButton(text="Отменить", callback_data="cancel")
        ]
    ]
)


add_employee_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Назначить менеджером", callback_data="manager")
        ],
        [
            InlineKeyboardButton(text="Назначить администратором", callback_data="admin")
        ],
        [
            InlineKeyboardButton(text="Отменить", callback_data="cancel")
        ]
    ]
)


control_mail_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Написать рассылку", callback_data="add_mail")
        ],
        [
            InlineKeyboardButton(text="Просмотреть список рассылок", callback_data="change_mail")
        ],
        [
            InlineKeyboardButton(text="Отменить", callback_data="cancel")
        ]
    ]
)


async def view_mails_keyboard(data):
    inline_keyboard = [[InlineKeyboardButton(text="Удалить", callback_data=data)]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard