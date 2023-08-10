from aiogram import executor
from aiogram.dispatcher import FSMContext

from functions import *
from states import Advertisement

param_to_change = []
current_num = [0]


@dp.message_handler(commands=['start'])
async def test(msg: types.Message):
    uid = msg.from_user.id

    if not db.user_exists(uid):
        await bot.send_message(id,
                               'Добро пожаловать в бота по выставке обьявлений! Для начала работы зайдите в меню '
                               'командой /menu. Для справки можете зайти в /help')
        db.add_user(id)

    else:
        await bot.send_message(id, 'Добро пожаловать! Зайдите в меню командой /menu')


@dp.message_handler(commands=['help'])
async def test(msg: types.Message):
    await bot.send_message(msg.from_user.id,
                           'Приветствую! Это бот для выставки объявлений. Воспользуйтесь кнопками в /menu для работы '
                           'с ботом, помощь с конвертированием валют в /convert.\nЕсли '
                           'вы нашли какой-то баг, или есть какие-то вопросы на счет бота, пишите разработчику '
                           '@akiko233')


@dp.message_handler(commands=['creator'])
async def test(msg: types.Message):
    await bot.send_message(msg.from_user.id,
                           'Cоздатель @akiko233')


@dp.message_handler(commands=['menu'])
async def reply_menu(msg: types.Message):
    await comeback_to_advert_menu(msg)


@dp.message_handler(commands=['convert'])
async def reply_menu(msg: types.Message):
    await bot.send_message(msg.from_user.id,
                           'Введите пару валют в формате: 1(количество)_usd(первая валюта) rub(вторая валюта)')


@dp.callback_query_handler(Text('break_load_process'), state=Advertisement.all_states)
async def break_load(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    await state.finish()
    await bot.send_message(call.from_user.id, 'Вы отменили загрузку объявления❌',
                           reply_markup=markups.back_to_main_menu)

    db.delete_advertisement(call.from_user.id, db.get_last_id(call.from_user.id))


@dp.callback_query_handler(Text('break_change_process'), state=Advertisement.AdvertisementActions.all_states)
async def break_load(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    await state.finish()
    await bot.send_message(call.from_user.id, 'Вы отменили процесс изменения❌'
    if state == Advertisement.AdvertisementActions.change_param
    else 'Вы отменили действие❌')


@dp.callback_query_handler(Text(startswith='back'))
async def comeback(call: types.CallbackQuery):
    action = call.data.split('-')[1]
    if action == 'to_user_advertisement':
        await watch_user_advertisements(call, call.from_user.id)
    elif action == 'to_user_advertisements':
        await watch_user_advertisements(call, call.from_user.id)
    else:
        await comeback_to_advert_menu(call)


@dp.callback_query_handler(Text(startswith='advertisement'), state=None)
async def actions_with_advertisements(call: types.CallbackQuery):
    user_id = call.from_user.id
    action = call.data.split('_')[1]

    if action == 'add':
        if len(db.get_user_advertisements_data(user_id)) >= 7:
            await bot.delete_message(call.from_user.id, call.message.message_id)
            await bot.send_message(user_id, 'Нельзя выставлять больше 7 обьявлений!❌')

        else:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

            user_name = call.from_user.username
            db.set_advertisement_user(user_id, user_name)

            await bot.send_message(call.from_user.id, 'Отправьте фото объявления',
                                   reply_markup=markups.break_load_process_keyboard)
            await Advertisement.photo.set()

    elif action == 'userwatch':
        await watch_user_advertisements(call, call.from_user.id)

    elif action == 'watchall':
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id, 'Выберите опцию',
                               reply_markup=markups.watch_all_advertisements_options())

        @dp.callback_query_handler(Text(startswith='all_advertisements'))
        async def watching_advertisements_actions(callback: types.CallbackQuery):
            act = callback.data.split('-')[1]

            if act == 'search':
                await Advertisement.AdvertisementActions.SearchStates.get_value.set()
                await search_advertisements(callback, current_num)
            elif act == 'watch':
                await bot.delete_message(callback.from_user.id, callback.message.message_id)
                await watch_all_advertisements_process(current_num=current_num, id=callback.from_user.id)

    elif action.startswith('change'):
        await bot.delete_message(call.from_user.id, call.message.message_id)
        unique_id = action.split('-')[1]

        await bot.send_message(user_id, 'Выберите, что хотите изменить', reply_markup=markups.choose_param_to_change())

    elif action == 'delete':
        await bot.delete_message(call.from_user.id, call.message.message_id)
        advert_json = call.as_json()

        try:
            unique_id = int(advert_json.split('"caption"')[1].split('\\n')[2].split(': ')[1])

            db.delete_advertisement(user_id, unique_id)
            await bot.send_message(user_id, "Объявление успешно удалено✅", reply_markup=markups.back_to_main_menu)
        except Exception as e:
            await bot.send_message(user_id, "Объявление не удалено❌")


@dp.callback_query_handler(Text(startswith='change'), state=None)
async def start_changing_advertisement(change_call: types.CallbackQuery):
    await bot.delete_message(change_call.from_user.id, change_call.message.message_id)
    param_to_change.append(change_call.data.split('-')[1])

    await bot.send_message(change_call.from_user.id, f'Отправьте новое {param_to_change[0]}',
                            reply_markup=markups.break_changing_process_keyboard)
    await Advertisement.AdvertisementActions.change_param.set()

    @dp.message_handler(content_types=['text', 'photo'], state=Advertisement.AdvertisementActions.change_param)
    async def changing_process(msg: types.Message, state: FSMContext):
        incorrect_format = 'Цена не может включать в себя буквы или быть больше 50000' if param_to_change[
                                                                                                0] == 'price' else 'Неправильный формат'
        correct_format = 'Изменения успешно внесены✅'
        try:
            value_to_change = int(msg.text) if param_to_change[0] == 'price' else msg.text

            if param_to_change[0] == 'photo':
                db.change_advertisement(unique_id=unique_id, param_to_change='photo_id',
                                        value=msg.photo[0].file_id)
            elif param_to_change[0] == 'price':
                if value_to_change < 50000:
                    db.change_advertisement(unique_id=unique_id, param_to_change=param_to_change[0],
                                                    value=value_to_change)
                else:
                    raise ValueError
                else:
                    db.change_advertisement(unique_id=unique_id, param_to_change=param_to_change[0],
                                                value=value_to_change)

                    await bot.delete_message(msg.from_user.id, msg.message_id - 1)
                    await bot.send_message(msg.from_user.id, correct_format, reply_markup=markups.back_to_main_menu)

                    await state.finish()
                    param_to_change.clear()
        except Exception:
            await bot.delete_message(msg.from_user.id, msg.message_id - 1)
            await bot.send_message(msg.from_user.id, incorrect_format,
                                    reply_markup=markups.back_to_main_menu)
            await state.finish()
        param_to_change.clear()

@dp.message_handler(content_types=['photo'], state=Advertisement.photo)
async def set_advertisement_photo(message: types.Message):
    photo_id = message.photo[0].file_id
    user_id = message.from_user.id

    db.set_something(db.get_last_id(user_id), 'photo_id', photo_id)

    await bot.send_message(user_id, "Теперь введите название", reply_markup=markups.break_load_process_keyboard)
    await Advertisement.name.set()


@dp.message_handler(content_types=['text'], state=Advertisement.name)
async def set_advertisement_name(message: types.Message, state: FSMContext):
    incorrect_statement_msg = f'Запрещено использовать {", ".join([f"""{s}""" for s in forbidden_chars])}\nЗагрузка объявления не удалась❌',

    if check_valid_msg(message):
        await bot.send_message(message.from_user.id, "Теперь добавьте описание",
                               reply_markup=markups.break_load_process_keyboard)
        

        await Advertisement.description.set()
    else:
        await bot.send_message(message.from_user.id, incorrect_statement_msg)
        await state.finish()


@dp.message_handler(content_types=['text'], state=Advertisement.description)
async def set_advertisement_description(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data({"description": message.text})

    await bot.send_message(message.from_user.id, 'Введите цену(в рублях)',
                           reply_markup=markups.interrupt_adv_creating)
    await Advertisement.price.set()


@dp.message_handler(content_types=['text'], state=Advertisement.price)
async def set_advertisement_price(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        if not int(message.text) <= 50000:
            return bot.send_message(user_id, "Цена не может превышать 50000 рублей",)
        
        last_user_advertisement = db.get_user_advertisements_data(user_id)[-1]
        await bot.send_photo(user_id, last_user_advertisement[3],
                             caption=f"Ваше объявление успешно сохранено✅\n"
                                     f"\nУникальный номер: {last_user_advertisement[0]}"
                                     f"\nНазвание: {last_user_advertisement[4]}"
                                     f"\nОписание: {last_user_advertisement[5]}"
                                     f"\nЦена: {last_user_advertisement[-1]} рублей",
                             reply_markup=markups.back_to_main_menu)
        await state.finish()
    except ValueError:
        await bot.send_message(user_id, 'Цена не может включать в себя буквы или быть больше 50000!',
                               reply_markup=markups.break_load_process_keyboard)


@dp.message_handler(content_types=['text'])
async def get_text_from_user(msg: types.Message):
    try:
        first_currency, quantity, second_currency = msg.text.upper().split()
        await bot.send_message(msg.from_user.id,
                               f"{quantity} {first_currency} это {convert_currencies(first_currency, int(quantity), second_currency)} {second_currency}")
    except:
        await bot.send_message(msg.from_user.id, 'Я не понимаю, что это значит')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
