from aiogram import Router

from .own import usr_ads_actions_with_owns_router
from .others import usr_ads_actions_with_others_router

usr_ads_actions_router = Router()
usr_ads_actions_router.include_routers(
    usr_ads_actions_with_owns_router, 
    usr_ads_actions_with_others_router, 
)