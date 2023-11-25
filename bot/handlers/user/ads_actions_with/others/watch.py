import logging
from aiogram import Bot, Router, types, F
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext

from bot.db.repository import Repository
from bot.utils.watch_ads import watch_others_ads

from bot.states.ad_actions import WatchAllAds
import bot.markups.markups as mp

router = Router()


@router.callback_query(WatchAllAds.on_watch, F.data.startswith("scroll_ad"))
async def on_watch_all_ads(call: types.CallbackQuery, state: FSMContext, bot: Bot, db: Repository):
    logging.info("Scrolling ads..")
    user_id, data = call.from_user.id, await state.get_data()
    for m_id in data["msgs_on_delete"]:
        try:
            await bot.delete_message(user_id, m_id)
        except TelegramAPIError:
            logging.warning(await state.get_data())
            logging.error(f"On exception: {call.message.message_id}")
    data["current_ad"] += [1, -1][call.data.split(":")[1] == "prev"]

    await state.set_data(data)
    await watch_others_ads(
        user_id=call.from_user.id,
        msg_id=call.message.message_id,
        state=state,
        bot=bot,
        db=db,
        current_ad_ind=data["current_ad"]
    )


@router.callback_query(WatchAllAds.on_watch, F.data == "back_to_watch_others_menu")
async def back_to_watch_others_menu(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    user_id, data = call.from_user.id, await state.get_data()
    for m_id in data["msgs_on_delete"]:
        try:
            await bot.delete_message(user_id, m_id)
        except TelegramAPIError:
            logging.warning(data)
            logging.error(f"On exception: {call.message.message_id}")
    await state.set_state(WatchAllAds.choose_option)
    await bot.send_message(user_id, "Выберите действие", reply_markup=mp.watch_all_ads_options)


@router.callback_query(WatchAllAds.on_watch, F.data == "back_to_ad_menu")
async def back_to_ad_menu(call: types.CallbackQuery, state: FSMContext, bot: Bot, db: Repository):
    user_id, data = call.from_user.id, await state.get_data()
    for m_id in data["msgs_on_delete"]:
        try:
            await bot.delete_message(user_id, m_id)
        except TelegramAPIError:
            logging.warning(await state.get_data())
            logging.error(f"On exception: {call.message.message_id}")
    await state.clear()
    await bot.send_message(user_id, 'Главное меню', reply_markup=mp.main_menu)
