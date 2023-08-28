from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .callback_data_models import MainAdMenuOption, ParamOnEdit, WatchAllAdsMenuOption


main_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить обьявление', callback_data=MainAdMenuOption(action="create_new_ad").pack()),
                InlineKeyboardButton(text='Все объявления', callback_data=MainAdMenuOption(action="watch_all_ads").pack()),
            ],
            [
                InlineKeyboardButton(text='Мои обьявления', callback_data=MainAdMenuOption(action="watch_own_ads").pack())
            ]
        ]
    )


ad_params_on_edit = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Фото', callback_data=ParamOnEdit(param_name="photo").pack()),
                InlineKeyboardButton(text='Название', callback_data=ParamOnEdit(param_name="title").pack()),
                InlineKeyboardButton(text='Описание', callback_data=ParamOnEdit(param_name="description").pack()),
                InlineKeyboardButton(text='Цену', callback_data=ParamOnEdit(param_name="price").pack())
            ],

            [
                InlineKeyboardButton(text='Назад', callback_data='back_to_watching_ads_before_edit')
            ]
        ],
    )


break_ad_creating_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Отмена', callback_data='break_ad_creating')
        ]
    ]
)

break_ad_editing_keyb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Отмена', callback_data='break_ad_editing')
        ]
    ]
)

back_to_main_menu = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text='Вернуться в главное меню', callback_data='back_to_ad_menu')
        ]
    ]
)

kb_after_edit = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text='К просмотру объявлений', callback_data='back_to_watching_ads_after_edit'),
            InlineKeyboardButton(text='В главное меню', callback_data='back-to_advertisement_menu'),
        ]
    ]
)


def kb_on_user_ad_watching(all_ads_len, current_num):
    builder = InlineKeyboardBuilder()
    two_btns_required = (0 < current_num < all_ads_len - 1)

    if current_num == 0 and all_ads_len != 1:
        builder.button(text='➡️', callback_data='usr_ad_watch:next')
    elif (current_num == all_ads_len - 1) and all_ads_len != 1:
        builder.button(text='⬅️', callback_data='usr_ad_watch:prev')
    elif two_btns_required:
        builder.button(text='⬅️', callback_data='usr_ad_watch:prev')
        builder.button(text='➡️', callback_data='usr_ad_watch:next')

    builder.button(text='🖋Изменить', callback_data='edit_ad')
    builder.button(text='🗑Удалить', callback_data='delete_ad')

    builder.button(text='В главное меню', callback_data='back-to_advertisement_menu')
    if all_ads_len == 1:
        builder.adjust(2, 1)
    else:
        builder.adjust(1 + two_btns_required, 2, 1)
    return builder.as_markup()


watch_all_ads_options = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Поиск по названию', callback_data=WatchAllAdsMenuOption(action="search").pack()),
            InlineKeyboardButton(text='Смотреть все', callback_data=WatchAllAdsMenuOption(action="watch_all").pack())
        ],
        [
            InlineKeyboardButton(text='Вернуться в главное меню', callback_data=WatchAllAdsMenuOption(action="back_to_ad_menu").pack())
        ]
    ]
)


def kb_on_others_ad_watching(all_ads_len, current_num):
    builder = InlineKeyboardBuilder()
    two_btns_required = (0 < current_num < all_ads_len - 1)

    if not current_num and all_ads_len != 1:
        builder.button(text='➡️', callback_data='scroll_ad:next')
    elif (current_num == all_ads_len - 1) and all_ads_len != 1:
        builder.button(text='⬅️', callback_data='scroll_ad:prev')
    elif two_btns_required:
        builder.button(text='⬅️', callback_data='scroll_ad:prev')
        builder.button(text='➡️', callback_data='scroll_ad:next')

    builder.button(text="Назад", callback_data='back_to_watch_others_menu')
    builder.button(text='Главное меню', callback_data='back_to_ad_menu')
    if all_ads_len == 1:
        builder.adjust(2, 1)
    else:
        builder.adjust(1 + two_btns_required, 1)
    return builder.as_markup()
