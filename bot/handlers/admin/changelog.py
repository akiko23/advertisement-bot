import asyncio
from contextlib import suppress
import logging
from aiogram import Router, types, F, Bot

from bot.db.requests_cls import Database
from bot.consts import ADMIN_ID, BOT_CHANNEL_ID

router = Router()


@router.message(
    (F.from_user.id == ADMIN_ID) &
    (
            (F.text & F.text.startswith("Changelog")) |
            (F.caption & F.caption.startswith("Changelog"))
    )
)
async def send_changelog(msg: types.Message, db: Database, bot: Bot):
    """
    Function that sends changelog to all users
    The mailing would'nt work well if you have a lot of users 
    so it's better to send message to a channel
    """
    # for i, tg_id in enumerate(await db.get_all_users()):
    #     if i % 29 == 0:
    #         await asyncio.sleep(1.4)
    #     with suppress(TelegramNotFound, TelegramForbiddenError):
    #         await bot.copy_message(from_chat_id=ADMIN_ID, chat_id=tg_id, message_id=msg.message_id)

    await bot.copy_message(from_chat_id=ADMIN_ID, chat_id=BOT_CHANNEL_ID, message_id=msg.message_id)
