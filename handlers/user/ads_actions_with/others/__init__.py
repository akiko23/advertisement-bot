from aiogram import Router

from .search import router as search_for_ads_router
from .watch import router as watch_all_ads_router

usr_ads_actions_with_others_router = Router()
usr_ads_actions_with_others_router.include_routers(
    search_for_ads_router, 
    watch_all_ads_router
)