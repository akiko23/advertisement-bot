import logging
from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext

from bot.db.repository import Repository
from bot.functions.watch_ads import watch_others_ad, watch_user_ad

from bot.states.ad_actions import CreateAdForm, SearchForAds, WatchAllAds, WatchUserAds
import bot.markups.markups as mp

from bot.markups.callback_data_models import MainAdMenuOption, WatchAllAdsMenuOption

"""
The handlers that were defined for
choosing an option
"""

router = Router()


# handlers on main menu
@router.callback_query(MainAdMenuOption.filter(F.action == "create_new_ad"))
async def create_new_ad(
        call: types.CallbackQuery,
        state: FSMContext,
):
    await state.set_state(CreateAdForm.title)
    await state.update_data(msg_on_delete=call.message.message_id)

    await call.message.edit_text("Введите заголовок объявления", reply_markup=mp.ad_creating_keyboard)


@router.callback_query(MainAdMenuOption.filter(F.action == "watch_own_ads"))
async def watch_own_ads(
        call: types.CallbackQuery,
        state: FSMContext,
        bot: Bot,
        db: Repository
):
    await bot.delete_message(call.from_user.id, call.message.message_id)

    usr_ads = await db.get_user_ads(call.from_user.id)
    logging.info(f"User ads: {usr_ads}")
    if not usr_ads:
        return await call.message.answer("You don't have any ads", reply_markup=mp.main_menu)
    await state.set_state(WatchUserAds.on_watch)
    await state.update_data(usr_ads=usr_ads, current_ad=0)

    await watch_user_ad(user_id=call.from_user.id, msg_id=call.message.message_id, state=state, bot=bot, db=db)


@router.callback_query(MainAdMenuOption.filter(F.action == "watch_all_ads"))
async def watch_all_ads(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(WatchAllAds.choose_option)
    await call.message.edit_text("Выберите действие", reply_markup=mp.watch_all_ads_options)


# handlers on all ads watching
@router.callback_query(WatchAllAds.choose_option, WatchAllAdsMenuOption.filter(F.action == "watch_all"))
async def choose_option(call: types.CallbackQuery, state: FSMContext, bot: Bot, db: Repository):
    await bot.delete_message(call.from_user.id, call.message.message_id)

    all_ads = await db.get_all_others_ads(call.from_user.id)
    if not all_ads:
        return await call.message.answer("Пока что нет объявлений от других пользователей :(")

    await state.set_state(WatchAllAds.on_watch)
    await state.update_data({
        "all_ads": all_ads,
        "current_ad": 0
    })
    await watch_others_ad(
        user_id=call.from_user.id,
        msg_id=call.message.message_id,
        state=state,
        bot=bot,
        db=db
    )


@router.callback_query(WatchAllAds.choose_option, WatchAllAdsMenuOption.filter(F.action == "search"))
async def on_search(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(SearchForAds.on_search)
    await call.message.edit_text("Напишите, что бы вы хотели найти", reply_markup=mp.back_to_main_menu)


@router.callback_query(WatchAllAds.choose_option, WatchAllAdsMenuOption.filter(F.action == "back_to_ad_menu"))
async def back_to_ad_menu(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text('Главное меню', reply_markup=mp.main_menu)
