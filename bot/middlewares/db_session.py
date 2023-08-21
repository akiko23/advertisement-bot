from typing import Dict, Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
 

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, db_obj):
        super().__init__()
        self._db_obj = db_obj

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["db"] = self._db_obj
        return await handler(event, data)
