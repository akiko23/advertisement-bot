from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from config import db


def advertisement_menu():
    advertisement_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить обьявление', callback_data='advertisement_add'),
                InlineKeyboardButton('Все объявления', callback_data='advertisement_watchall'),
            ],
            [
                InlineKeyboardButton('Мои обьявления', callback_data='advertisement_userwatch')
            ]
        ]
    )
    return advertisement_keyboard


def actions_with_advertisement(unique_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('Изменить', callback_data=f'advertisement_change-{unique_id}'),
                InlineKeyboardButton('Удалить', callback_data='advertisement_delete'),

            ],
            [
                InlineKeyboardButton('Назад', callback_data='back-to_user_advertisements')
            ]
        ]
    )
    return keyboard


def choose_param_to_change():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('Фото', callback_data='change-photo'),
                InlineKeyboardButton('Название', callback_data='change-name'),
                InlineKeyboardButton('Описание', callback_data='change-description'),
                InlineKeyboardButton('Цену', callback_data='change-price')
            ],

            [
                InlineKeyboardButton('Назад', callback_data='back-to_user_advertisement')
            ]
        ],

    )
    return keyboard


break_load_process_keyboard = InlineKeyboardMarkup()
btn_cancel_load = InlineKeyboardButton(text='Отмена', callback_data='break_load_process')
break_load_process_keyboard.insert(btn_cancel_load)

break_changing_process_keyboard = InlineKeyboardMarkup()
btn_cancel_change = InlineKeyboardButton(text='Отмена', callback_data='break_change_process')
break_changing_process_keyboard.insert(btn_cancel_change)

back_to_main_menu = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton('Вернуться в главное меню', callback_data='back-to_advertisement_menu')
        ]
    ]
)


def set_menu_on_watching(current_num, id):
    all_ads_len = len(db.get_not_user_advertisements_data(id))

    inline_obj = []
    if current_num == all_ads_len - 1:
        inline_obj = [InlineKeyboardButton('Предыдущее', callback_data='watch-prev')]
    elif current_num == 0:
        inline_obj = [InlineKeyboardButton('Следующее', callback_data='watch-next')]
    if 0 < current_num < all_ads_len - 1:
        inline_obj = [InlineKeyboardButton('Предыдущее', callback_data='watch-prev'), InlineKeyboardButton('Следующее', callback_data='watch-next')]

    return InlineKeyboardMarkup(
        inline_keyboard=
        [
            inline_obj,
            [
                InlineKeyboardButton('Вернуться в главное меню', callback_data='back-to_advertisement_menu')
            ]
        ]
    )


def on_choose_advertisement(user_advertisements):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=ad[4], callback_data=f"useradvertisement_{ad[0]}")
                for ad in user_advertisements
            ],
            [
                InlineKeyboardButton('Вернуться в главное меню', callback_data='back-to_advertisement_menu')
            ]
        ]
    )
