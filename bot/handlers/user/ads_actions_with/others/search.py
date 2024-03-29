import logging

from aiogram import Bot, Router, F, types
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext

from bot.db.repository import Repository
from bot.utils.watch_ads import watch_others_ads
import bot.markups.markups as mp
from bot.states.ad_actions import SearchForAds, WatchAllAds

router = Router()


async def get_ad_text(ad_id: int, db: Repository):
    title, _, description, *__ = await db.get_ad_by_id(ad_id)
    return "|".join((title.strip(), description.strip())).lower()


@router.message(SearchForAds.on_search, F.text)
async def get_value(msg: types.Message, state: FSMContext, bot: Bot, db: Repository):
    value = msg.text.lower().strip()

    all_ads = await db.get_all_others_ads(msg.from_user.id)
    res = [ad_id for ad_id in all_ads if value in (await get_ad_text(ad_id, db))]
    if not res:
        await state.set_state(WatchAllAds.choose_option)

        await bot.delete_message(msg.from_user.id, msg.message_id - 1)
        return await msg.answer("По вашему запросу не найдено ни одного объявления",
                                reply_markup=mp.watch_all_ads_options)

    await state.set_state(WatchAllAds.on_watch)
    await state.update_data(all_ads=res)

    await bot.send_message(msg.from_user.id, "По вашему запросу найдено " + str(len(res)) + " объявл.")
    await watch_others_ads(
        user_id=msg.from_user.id,
        msg_id=msg.message_id,
        state=state,
        bot=bot,
        db=db,
        on_search=True
    )


@router.callback_query(SearchForAds.on_search, F.data == "back_to_watch_others_menu")
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


@router.callback_query(SearchForAds.on_search, F.data == "back_to_ad_menu")
async def back_to_ad_menu(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    user_id, data = call.from_user.id, await state.get_data()
    for m_id in data.get("msgs_on_delete", tuple()):
        try:
            await bot.delete_message(user_id, m_id)
        except TelegramAPIError:
            logging.warning(await state.get_data())
            logging.error(f"On exception: {call.message.message_id}")
    await state.clear()

    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(user_id, 'Главное меню', reply_markup=mp.main_menu)
