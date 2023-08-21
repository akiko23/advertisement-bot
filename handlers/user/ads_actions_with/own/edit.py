from aiogram import Bot, Router, F, types
from aiogram.fsm.context import FSMContext
from functions.check_valid import check_valid_msg
from db.requests_cls import Database
from functions.check_valid import check_valid_price

from states.ad_actions import EditAd, WatchUserAds

import markups.markups as mp
from markups.callback_data_models import MainAdMenuOption, ParamOnEdit

from functions.watch_ads import watch_user_ad


router = Router()

@router.callback_query(EditAd.param_to_change, F.data.startswith("param"))
async def set_param_to_change(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    param_to_change = call.data.split(":")[1]

    # logging.info("Start editing ad number " + repr(data))
    for m_id in data["msgs_on_delete"]:
        try:
            await bot.delete_message(call.from_user.id, m_id)
        except:
            pass
    await state.set_state(EditAd.new_value)
    await state.update_data({
        "ad_on_edit_id": data["ad_on_edit_id"],
        "param_to_change": param_to_change,
        "msg_on_delete": call.message.message_id + 1,
        "current_ad": data["current_ad"],
    })
    await call.message.answer("Отправьте новое значение", reply_markup=mp.break_ad_editing_keyb)


@router.message(EditAd.new_value, F.photo)
async def set_new_val(
    msg: types.Message, 
    state: FSMContext, 
    bot: Bot, 
    db: Database,
    media_group: list[types.PhotoSize]
):
    data = await state.get_data()
    ad_id = data["ad_on_edit_id"]

    new_photo = [m.file_id for m in media_group] if media_group else [msg.photo[-1].file_id]
    if data["param_to_change"] != "photo":
        return await msg.answer("Incorrect format", reply_markup=mp.break_ad_editing_keyb)
    await db.update_ad_param(
        ad_id=ad_id,
        param_name="photo",
        content=new_photo,
    )
    try:
        await bot.delete_message(msg.from_user.id, data["msg_on_delete"])
    except:
        pass
    await state.set_data(data)
    await msg.answer("Новое значение успешно выставлено", reply_markup=mp.kb_after_edit)
    

@router.message(EditAd.new_value, F.text)
async def set_new_val(msg: types.Message, state: FSMContext, bot: Bot, db: Database):
    data = await state.get_data()
    match data["param_to_change"]:
        case "photo":
            return await msg.answer("Incorrect format", reply_markup=mp.break_ad_editing_keyb)
        case "price":
            new_val, exc_msg = check_valid_price(msg.text)
            if exc_msg:
                return await msg.answer(exc_msg, reply_markup=mp.break_ad_editing_keyb)
        case _:
            new_val, exc_msg = check_valid_msg(msg.text)
            if exc_msg:
                return await msg.answer(
                    exc_msg,
                    reply_markup=mp.break_ad_editing_keyb
                )
    await db.update_ad_param(ad_id=data["ad_on_edit_id"], param_name=data["param_to_change"], content=new_val)

    try:
        await bot.delete_message(msg.from_user.id, data["msg_on_delete"])
    except:
        pass
    await msg.answer("Новое значение успешно выставлено", reply_markup=mp.kb_after_edit)


@router.callback_query(EditAd.param_to_change, F.data == "back_to_watching_ads_before_edit")
async def back_to_watching_ads_before_editing(call: types.CallbackQuery, state: FSMContext, bot: Bot, db: Database):
    data = await state.get_data()

    usr_ads = await db.get_user_ads(call.from_user.id)
    current_ad = data["current_ad"]

    title, photo, descripton, price = await db.get_ad_by_uid(data["ad_on_edit_id"])
    
    await state.set_state(WatchUserAds.on_watch)
    await state.update_data({
        "current_ad": current_ad,
        "msgs_on_delete": data["msgs_on_delete"]
    })

    if len(photo) == 1:
        return await call.message.edit_caption(
            caption=f"Название: {title}\nОписание: {descripton}\nЦена: {price}",
            reply_markup=mp.kb_on_user_ad_watching(len(usr_ads), current_ad)
        )
    await call.message.edit_text(
        text=f"Название: {title}\nОписание: {descripton}\nЦена: {price}",
        reply_markup=mp.kb_on_user_ad_watching(len(usr_ads), current_ad)
    )
    

@router.callback_query(EditAd.new_value, F.data == "back_to_watching_ads_after_edit")
async def back_to_watching_ads_after_editing(call: types.CallbackQuery, state: FSMContext, bot: Bot, db: Database):
    data = await state.get_data()

    await state.set_state(WatchUserAds.on_watch)
    await state.update_data({
        "usr_ads": await db.get_user_ads(call.from_user.id)
    })

    await bot.delete_message(call.from_user.id, call.message.message_id)
    await watch_user_ad(
        user_id=call.from_user.id,
        msg_id=call.message.message_id,
        state=state,
        bot=bot,
        db=db,
        current_ad_ind=data["current_ad"]
    )


@router.callback_query(EditAd.new_value, F.data == "back-to_advertisement_menu")
async def back_to_advertisement_menu(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()

    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.message.answer('Вы вернулись в главное меню', reply_markup=mp.main_menu)


@router.callback_query(EditAd.new_value, F.data == "break_ad_editing")
async def break_ad_editing(call: types.CallbackQuery):
    await call.message.edit_text("Вы отменили процесс изменения", reply_markup=mp.kb_after_edit)
    

# wrong scenario handler   
@router.message(EditAd())
@router.callback_query(EditAd())
async def process_weird_usr_actions(upd: types.Message | types.CallbackQuery, state: FSMContext):
    if isinstance(upd, types.Message):
        return await upd.answer("Weird action", reply_markup=mp.break_ad_editing_keyb)
    await upd.message.answer("Weird action", reply_markup=mp.break_ad_editing_keyb)

