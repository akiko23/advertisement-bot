import logging
from sqlalchemy import ScalarResult, delete, select, insert, update

from typing import Callable, List
from pydantic import UUID3
from sqlalchemy.exc import DataError, DBAPIError

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.result import ChunkedIteratorResult

from bot.db.models import Advertisement, User

logger = logging.getLogger(__name__)


class Repository:
    __slots__ = ('_session_pool',)

    def __init__(self, pool):
        self._session_pool = pool
        logging.info("Successfully connected to database!")

    async def _request_to_db(self, func: Callable, query: str) -> ChunkedIteratorResult:
        async with self._session_pool() as session:
            try:
                res = await (getattr(session, func.__name__))(query)
                await session.commit()

                return res
            except DBAPIError as e:
                logger.error(f'Db error: {e}')
                await session.rollback()

    async def add_user(self, user_id, username):
        await self._request_to_db(
            AsyncSession.execute,
            insert(User).
            values(
                user_id=user_id,
                username=username
            )
        )

    async def user_exists(self, user_id):
        return await self._request_to_db(
            AsyncSession.scalar,
            select(User.user_id).
            where(User.user_id == user_id)
        )

    async def get_all_users(self):
        return await self._request_to_db(
            AsyncSession.scalars,
            select(User.user_id)
        )

    async def _get_last_ad_id(self):
        return await self._request_to_db(
            AsyncSession.scalar,
            select(Advertisement.advertisement_id).
            order_by(Advertisement.advertisement_id.desc())
        )

    async def create_ad(
            self,
            title: str,
            photo: List[str],
            description: str,
            price: int,
            user_id: int,
    ):
        await self._request_to_db(
            AsyncSession.execute,
            insert(Advertisement)
            .values(
                title=title,
                photo=photo,
                description=description,
                price=price,
                user_id=user_id
            )
        )

    async def get_user_ads_data(self, user_id: int):
        return await self._request_to_db(
            AsyncSession.scalars,
            select(
                Advertisement.title,
                Advertisement.photo,
                Advertisement.description,
                Advertisement.price
            )
            .where(
                Advertisement.user_id == user_id
            )
        )

    async def get_user_ads(self, user_id: int):
        res = await self._request_to_db(
            AsyncSession.scalars,
            select(Advertisement)
            .where(
                Advertisement.user_id == user_id
            )
            .order_by(Advertisement.created_at.desc())
        )
        return res.all()

    async def update_ad_param(self, ad_for_edit: Advertisement, column_name, content):
        return await self._request_to_db(
            AsyncSession.execute,
            update(Advertisement)
            .where(Advertisement.advertisement_id == ad_for_edit.advertisement_id)
            .values(**{column_name: content})
        )

    async def get_ad_by_id(self, ad_id: int, need_username=False):
        options_to_select = [
            Advertisement.title,
            Advertisement.photo,
            Advertisement.description,
            Advertisement.price,
        ]

        if need_username:
            options_to_select.append(User.username)
        res = await self._request_to_db(
            AsyncSession.execute,
            select(*options_to_select)
            .join(User, Advertisement.user_id == User.user_id)
            .where(Advertisement.advertisement_id == ad_id)
        )
        return res.first()

    async def delete_ad(self, ad_to_delete: Advertisement):
        await self._request_to_db(
            AsyncSession.execute,
            delete(Advertisement).
            where(Advertisement.advertisement_id == ad_to_delete.advertisement_id)
        )

    async def get_all_others_ads(self, user_id: int) -> list[UUID3]:
        res: ScalarResult = await self._request_to_db(
            AsyncSession.scalars,
            select(Advertisement.advertisement_id).
            where(
                Advertisement.user_id != user_id
            )
        )
        return res.all()
