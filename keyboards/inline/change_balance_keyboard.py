from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


change_balance_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Списать баллы", callback_data="writeoff")
            ],
            [
                InlineKeyboardButton(text="Начислить баллы", callback_data="earn")
            ],
            [
                InlineKeyboardButton(text="Отменить", callback_data="cancel")
            ]
        ]
    )


confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data="yes")
            ],
            [
                InlineKeyboardButton(text="Изменить", callback_data="no")
            ],
        ]
    )


choice_sum_writeoff_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Максимально возможное", callback_data="max")
            ],
            [
                InlineKeyboardButton(text="Определенное", callback_data="definite")
            ],
        ]
    )


confirm_points_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data="yes_points")
            ],
            [
                InlineKeyboardButton(text="Изменить", callback_data="no_points")
            ],
        ])


confirm_earn_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
            [
                InlineKeyboardButton(text="Начислить", callback_data="earn_yes")
            ],
                [
                    InlineKeyboardButton(text="Изменить", callback_data="earn_no")
                ],
            [
                InlineKeyboardButton(text="Отменить", callback_data="cancel")
            ],
        ])