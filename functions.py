import requests
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode

import markups
from config import db, bot, forbidden_chars, dp


def convert_currencies(first_currency='USD', quantity=1, second_currency='RUB'):
    url = f"https://free.currconv.com/api/v7/convert?apiKey=cd2ff852330c08894153&q={first_currency}_{second_currency}&compact=ultra"
    response = requests.get(url).json()

    # return Decimal(response[f"{first_currency}_{second_currency}"] * quantity)
    return round(response[f"{first_currency}_{second_currency}"] * quantity, 3)


async def watch_all_advertisements_process(current_num, id):
    try:
        current_num.append(0)
        all_advertisements = db.get_not_user_advertisements_data(id)

        if len(all_advertisements) > 0:
            advert = all_advertisements[current_num[0]]
            await bot.send_photo(id, advert[3],
                                 caption=f"Название: {advert[4]}\nОписание: {advert[5]}\nЦена: {advert[-1]} рублей\n"
                                         f"\nПродавец @{advert[2]}",
                                 reply_markup=markups.set_menu_on_watching(current_num[0], id))
        else:
            await bot.send_message(id, 'Пока что нет объявлений от других пользователей😢',
                                   reply_markup=markups.back_to_main_menu)
    except IndexError:
        current_num[0] = 0


def check_valid_msg(msg):
    try:
        return True if not any([s in msg.text for s in forbidden_chars]) else False
    except:
        return False


async def comeback_to_advert_menu(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await watch_profile(call.from_user.id)


async def watch_user_advertisements(call: types.CallbackQuery, id, del_previous=True):
    await bot.delete_message(call.from_user.id, call.message.message_id) if del_previous is True else None

    if len(db.get_user_advertisements_data(id)) != 0:
        user_advertisements = db.get_user_advertisements_data(id)
        await bot.send_message(call.from_user.id, 'Выберите объявление',
                               reply_markup=markups.on_choose_advertisement(user_advertisements))

        @dp.callback_query_handler(Text(startswith='useradvertisement'))
        async def get_one_user_advertisement(callback: types.CallbackQuery):
            await bot.delete_message(callback.from_user.id, callback.message.message_id)

            advert = db.get_user_advertisement_by_id(callback.data.split('_')[1])
            await bot.send_photo(callback.from_user.id, advert[3],
                                 caption=f"<b>{advert[-3].upper()}</b>\n\nУникальный номер: {advert[0]}\nОписание: {advert[-2]}\nЦена: {advert[-1]} рублей",
                                 reply_markup=markups.actions_with_advertisement(advert[0]), parse_mode=ParseMode.HTML)
    else:
        await bot.send_message(call.from_user.id, 'У вас нет объявлений, чтобы их посмотреть', reply_markup=markups.back_to_main_menu)


async def watch_profile(id):
    await bot.send_message(id,
                           f'Количество ваших объявлений: {len(db.get_user_advertisements_data(id))}',
                           reply_markup=markups.advertisement_menu())

