from aiogram import Bot
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.fsm.context import FSMContext

from bot.db.models import Advertisement
from bot.db.repository import Repository
import bot.markups.markups as mp


async def watch_user_ad(
    user_id: int, 
    msg_id: int, 
    state: FSMContext, 
    bot: Bot,
    db: Repository,
    current_ad_ind: int = 0
):
    usr_ads: list[Advertisement] = (await state.get_data())["usr_ads"]

    current_ad = usr_ads[current_ad_ind]
    title, photo, description, price = await db.get_ad_by_id(current_ad.advertisement_id)

    await state.update_data(
        msgs_on_delete=tuple(i for i in range(msg_id + 1, msg_id + len(photo) + 2 - (len(photo) == 1))),
    )
    caption = f"<b>Название</b>: {title}\n\n<b>Описание</b>: {description}\n\n<b>Цена</b>: {price}$"
    if len(photo) > 1:
        await bot.send_media_group(
            chat_id=user_id,
            media=[InputMediaPhoto(media=p) for p in photo],
        )
        return await bot.send_message(
            user_id, caption,
            reply_markup=mp.kb_on_user_ad_watching(len(usr_ads), current_ad_ind)
        )
    await bot.send_photo(
        user_id, 
        photo[0], 
        caption=caption, 
        reply_markup=mp.kb_on_user_ad_watching(len(usr_ads), current_ad_ind)
    )


async def watch_others_ads(
    user_id: int, 
    msg_id: int, 
    state: FSMContext, 
    bot: Bot,
    db: Repository,
    current_ad_ind: int = 0,
    on_search: bool = False
):
    all_ads = (await state.get_data())["all_ads"]
    title, photo, descripton, price, owner = await db.get_ad_by_id(all_ads[current_ad_ind], need_username=True)

    await state.update_data(
        msgs_on_delete=tuple(i for i in range(msg_id + 1, msg_id + len(photo) + 2 - (len(photo) == 1) + on_search)),
    )
    ad_text = (f"<b>Название</b>: {title}\n\n<b>Описание</b>: {descripton}\n"
               f"\n<b>Цена</b>: {price}$\n\n<b>Продавец</b>: @{owner}")
    if len(photo) > 1:
        await bot.send_media_group(
            chat_id=user_id,
            media=[InputMediaPhoto(media=p) for p in photo],
        )
        return await bot.send_message(
            user_id, 
            text=ad_text,
            reply_markup=mp.kb_on_others_ad_watching(len(all_ads), current_ad_ind)
        )
    await bot.send_photo(
        user_id, 
        photo[0], 
        caption=ad_text, 
        reply_markup=mp.kb_on_others_ad_watching(len(all_ads), current_ad_ind)
    )
