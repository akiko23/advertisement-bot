from aiogram import Router

from .ads_actions_with import usr_ads_actions_router
from .basic_commands import router as commands_router

usr_main_router = Router()
usr_main_router.include_routers(
    usr_ads_actions_router, 
    commands_router
)
