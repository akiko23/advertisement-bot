import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from bot.db.repository import Repository

from bot.middlewares.db_session import DbRepoMiddleware
from bot.middlewares.media_group import MediaGroupMiddleware

from bot.handlers.options import router as options_router
from bot.handlers.user import usr_main_router
from bot.handlers.admin import admin_main_router

from bot.consts import LOGGING_FORMAT
from bot.config_reader import config


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=LOGGING_FORMAT
    )
    # initialise database connection
    engine = create_async_engine(config.postgres_dsn, future=True, echo=False)
    session_pool = async_sessionmaker(engine, expire_on_commit=False)

    dp = Dispatcher()

    # setup middlewares
    dp.message.middleware(MediaGroupMiddleware())
    dp.update.middleware(DbRepoMiddleware(db_obj=Repository(pool=session_pool)))

    dp.include_routers(options_router, usr_main_router, admin_main_router)

    bot = Bot(token=config.bot_token, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


asyncio.run(main())
