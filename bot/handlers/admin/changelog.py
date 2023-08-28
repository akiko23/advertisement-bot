import asyncio
from contextlib import suppress
import logging
from aiogram import Router, types, F, Bot
from aiogram.exceptions import TelegramNotFound, TelegramForbiddenError

from bot.db.requests_cls import Database

from bot.consts import ADMIN_ID

router = Router()


@router.message(
    (F.from_user.id == ADMIN_ID) & 
    (
        (F.text & F.text.startswith("changelog")) | 
        (F.caption & F.caption.startswith("changelog"))
    )
)
async def send_changelog(msg: types.Message, db: Database, bot: Bot):
    for i, tg_id in enumerate(await db.get_all_users()):
        if i % 29 == 0:
            await asyncio.sleep(10)
        else:
            with suppress(TelegramNotFound, TelegramForbiddenError):
                await bot.copy_message(from_chat_id=ADMIN_ID, chat_id=tg_id, message_id=msg.message_id)

