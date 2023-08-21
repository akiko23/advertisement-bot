import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from db.requests_cls import Database

from middlewares.db_session import DbSessionMiddleware
from middlewares.media_group import MediaGroupMiddleware

from handlers.options import router as options_router
from handlers.user import usr_main_router

import consts
from config_reader import config


async def main():
    logging.basicConfig(
        level=logging.INFO, 
        format=consts.LOGGING_FORMAT
    )
    # initialise database connection
    engine = create_async_engine(config.postgres_dsn, future=True, echo=False)
    session_pool = async_sessionmaker(engine, expire_on_commit=False)

    dp = Dispatcher()

    # setup middlewares
    dp.message.middleware(MediaGroupMiddleware())
    dp.update.middleware(DbSessionMiddleware(db_obj=Database(pool=session_pool)))

    dp.include_routers(options_router, usr_main_router) 

    bot = Bot(token=config.bot_token, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


asyncio.run(main())