import logging

from aiogram import Bot, Router, F, types
from aiogram.fsm.context import FSMContext

from bot.db.requests_cls import Database

from bot.functions.watch_ads import watch_user_ad
from bot.states.ad_actions import EditAd, WatchUserAds
import bot.markups.markups as mp


router = Router()

@router.callback_query(WatchUserAds.on_watch, F.data.startswith("usr_ad_watch"))
async def usr_ad_watch(
    call: types.CallbackQuery, 
    state: FSMContext,
    bot: Bot,
    db: Database
):
    user_id, data = call.from_user.id, await state.get_data()
    for m_id in data["msgs_on_delete"]:
        try:
            await bot.delete_message(user_id, m_id)
        except:
            logging.warning(await state.get_data())
            logging.error(f"On exception: {call.message.message_id}")
    data["current_ad"] += [1, -1][call.data.split(":")[1] == "prev"]

    await state.set_data(data)
    await watch_user_ad(user_id, call.message.message_id, state, bot, db, data["current_ad"])


@router.callback_query(WatchUserAds.on_watch, F.data == "edit_ad")
async def edit_ad(call: types.CallbackQuery, state: FSMContext, db: Database):
    data = await state.get_data()
    
    await state.set_state(EditAd.param_to_change)
    await state.update_data({
        "ad_on_edit_id": (await db.get_user_ads(call.from_user.id))[data["current_ad"]],
        "msgs_on_delete": data["msgs_on_delete"],
        "current_ad": data["current_ad"]
    })
    if call.message.content_type == "photo":
        return await call.message.edit_caption(
            caption=call.message.caption + "\n\nВыберите, что хотите изменить", 
            reply_markup=mp.ad_params_on_edit
        ) 
    await call.message.edit_text(
        text=call.message.text + "\n\nВыберите, что хотите изменить", 
        reply_markup=mp.ad_params_on_edit
    )


@router.callback_query(WatchUserAds.on_watch, F.data == "delete_ad")
async def delete_ad(call: types.CallbackQuery, state: FSMContext, bot: Bot, db: Database):
    data = await state.get_data()
    user_id = call.from_user.id

    for m_id in (await state.get_data())["msgs_on_delete"]:
        try:
            await bot.delete_message(user_id, m_id)
        except:
            logging.warning(await state.get_data())
            logging.info(f"On exception: {call.message.message_id}")

    ad_id = (await db.get_user_ads(user_id))[data["current_ad"]]

    logging.warning(f"{await db.get_user_ads(user_id)}; Ad num: {data['current_ad']}; Ad uid: {ad_id}")
    await db.delete_ad(ad_id, user_id)
    await state.clear()

    await bot.send_message(user_id, "Объявление успешно удалено", reply_markup=mp.main_menu)

@router.message(WatchUserAds())
@router.callback_query(WatchUserAds())
async def stop_watching(upd: types.Message | types.CallbackQuery, state: FSMContext, bot: Bot):
    user_id = upd.from_user.id
    logging.info(await state.get_data())

    for m_id in (await state.get_data()).get("msgs_on_delete", tuple()):
        try:
            await bot.delete_message(user_id, m_id)
        except:
            logging.warning(await state.get_data())
            logging.info(f"On exception: {upd.message.message_id}")
    await state.clear()
    await bot.send_message(user_id, 'Главное меню', reply_markup=mp.main_menu)
