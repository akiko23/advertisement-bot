from aiogram import Router

from .create import router as create_ad_router
from .edit import router as edit_ad_router
from .watch import router as watch_ads_router

usr_ads_actions_with_owns_router = Router()
usr_ads_actions_with_owns_router.include_routers(
    create_ad_router, 
    edit_ad_router, 
    watch_ads_router
)
