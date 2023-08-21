import logging

from aiogram import Bot, Router, F, types
from aiogram.fsm.context import FSMContext
from asyncpg.exceptions import DataError

from bot.db.requests_cls import Database
from bot.functions.check_valid import check_valid_description, check_valid_title
from bot.states.ad_actions import CreateAdForm
import bot.markups.markups as mp


router = Router()

# new ad's title
@router.message(CreateAdForm.title, F.text)
async def ad_title(
    msg: types.Message,
    state: FSMContext,
    bot: Bot
):
    data = await state.get_data()

    title, exc_msg = check_valid_title(msg.text)
    if exc_msg:
        return await msg.answer(
            exc_msg, 
            reply_markup=mp.break_ad_creating_keyboard
        )
    await bot.delete_message(msg.from_user.id, data["msg_on_delete"])

    await state.update_data(title=title, msg_on_delete=msg.message_id + 1)
    await state.set_state(CreateAdForm.photo)

    return await msg.answer("Отправьте фото вашего объявления (можно несколько)", reply_markup=mp.break_ad_creating_keyboard)
    

# new ad's photo
@router.message(CreateAdForm.photo, F.photo & F.media_group_id)
async def ad_photo(
    msg: types.Message, 
    state: FSMContext,
    bot: Bot,
    media_group: list[types.PhotoSize]
):
    data = await state.get_data()

    try:
        await bot.delete_message(msg.from_user.id, data["msg_on_delete"])
    except:
        logging.error(await state.get_data())

    await state.set_state(CreateAdForm.description)
    await state.update_data({
        "photo": [m.file_id for m in media_group],
        "msg_on_delete": msg.message_id + len(media_group)
    })
    
    await msg.answer("Введите описание (длина - минимум 25 символов)", reply_markup=mp.break_ad_creating_keyboard)        


@router.message(CreateAdForm.photo, F.photo)
async def ad_photo(
    msg: types.Message, 
    state: FSMContext,
    bot: Bot,
):
    data = await state.get_data()

    try:
        await bot.delete_message(msg.from_user.id, data["msg_on_delete"])
    except:
        logging.error(await state.get_data())

    await state.set_state(CreateAdForm.description)
    await state.update_data({
        "photo": [msg.photo[-1].file_id],
        "msg_on_delete": msg.message_id + 1
    })

    await msg.answer("Введите описание (длина - минимум 25 символов)", reply_markup=mp.break_ad_creating_keyboard)


# new ad's description
@router.message(CreateAdForm.description, F.text)
async def ad_description(
    msg: types.Message, 
    state: FSMContext,
    bot: Bot
):
    data = await state.get_data()

    try:
        await bot.delete_message(msg.from_user.id, data["msg_on_delete"])
    except:
        logging.error(await state.get_data())

    description, exc_msg = check_valid_description(msg.text)
    if exc_msg:
        return await msg.answer(
            exc_msg, 
            reply_markup=mp.break_ad_creating_keyboard
        )

    await state.set_state(CreateAdForm.price)
    await state.update_data(description=description, msg_on_delete=msg.message_id + 1)
    
    await msg.answer("И наконец, укажите цену в $ (в пределах 40000)", reply_markup=mp.break_ad_creating_keyboard)
    

# new ad's price
@router.message(CreateAdForm.price, (F.text.isdigit()) & (F.text.cast(int) <= 10000))
async def ad_description(
    msg: types.Message, 
    state: FSMContext,
    bot: Bot,
    db: Database
):
    form_data = await state.get_data()

    try:
        del form_data["msg_on_delete"]
        await db.create_ad(
            **form_data, 
            price=int(msg.text), 
            user_id=msg.from_user.id,
            username=msg.from_user.username
        )
    except DataError:
        await state.clear()
        return await msg.answer(
            "!Объявление не удалось добавить. Проверьте корректность введенных вами данных и создайте снова", 
            reply_markup=mp.main_menu
        )
    try:
        await bot.delete_message(msg.from_user.id, (await state.get_data())["msg_on_delete"])
    except:
        pass
    await msg.answer("Ваше объявление было успешно добавлено", reply_markup=mp.main_menu)
    await state.clear()


@router.callback_query(CreateAdForm(), F.data == "break_ad_creating")
async def break_ad_creating(
    call: types.CallbackQuery, 
    state: FSMContext,
    bot: Bot
):
    await state.clear()

    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id, "Вы отменили процесс создания и вернулись в главное меню", reply_markup=mp.main_menu)


@router.message(CreateAdForm.photo, ~F.photo)
async def incorrect_ad_data_format(msg: types.Message):
    await msg.answer("Некорректный тип данных, ожидалось photo", reply_markup=mp.break_ad_creating_keyboard)
