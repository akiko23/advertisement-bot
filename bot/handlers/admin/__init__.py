from aiogram import Router
from .changelog import router as changelog_router


admin_main_router = Router()
admin_main_router.include_routers(changelog_router)
