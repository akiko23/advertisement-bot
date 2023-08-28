import logging
import uuid
from sqlalchemy import ScalarResult, delete, select, insert, update
from datetime import datetime

from typing import Callable, List
from pydantic import UUID3

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.result import ChunkedIteratorResult

from .models import Advertisement, User
    

class Database:
    __slots__ = ("_session_pool", )

    def __init__(self, pool):
        self._session_pool = pool
        logging.info("Successfully connected to database!")


    async def _request_to_db(self, func: Callable, SQL: str) -> ChunkedIteratorResult:
        async with self._session_pool() as session:
            async with session.begin():
                return await (getattr(session, func.__name__))(SQL)
        

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
            select(Advertisement.id).
            order_by(Advertisement.id.desc())
        )


    async def create_ad(
        self, 
        title: str, 
        photo: List[str], 
        description: str,
        price: int,
        user_id: int,
        username: str
    ):
        ad_id = uuid.uuid3(uuid.NAMESPACE_DNS, str(await self._get_last_ad_id()))
        await self._request_to_db(
            AsyncSession.execute,
            insert(Advertisement).
            values(
                advertisement_id=ad_id,
                title=title,
                photo=photo,
                description=description,
                price=price,
                created_at=datetime.now(),
                owners_username=username
            )
        )

        # add new ad to user ads
        user_ads = await self.get_user_ads(user_id)
        await self._request_to_db(
            AsyncSession.execute,
            update(User).
            where(
                User.user_id == user_id
            ).
            values(advertisements=user_ads + [ad_id])
        )


    async def get_user_ads_data(self, user_id: int):
        user_ads = await self.get_user_ads(user_id)
        return await self._request_to_db(
            AsyncSession.scalars, 
            select(
                Advertisement.title,
                Advertisement.photo,
                Advertisement.description,
                Advertisement.price
            ).where(
                Advertisement.advertisement_id.in_(user_ads)
            )
        )


    async def get_user_ads(self, user_id: int):
        res = await self._request_to_db(
            AsyncSession.scalar,
            select(User.advertisements).
            where(
                User.user_id == user_id
            )
        )
        return [list(), res][bool(res)]
    

    async def update_ad_param(self, ad_id: UUID3, param_name, content):
        return await self._request_to_db(
            AsyncSession.execute,
            update(Advertisement).
            where(Advertisement.advertisement_id == ad_id).
            values(**{param_name: content})
        )


    async def get_ad_by_uid(self, ad_id: UUID3, need_uname=False):
        options_to_select = [
            Advertisement.title, 
            Advertisement.photo,
            Advertisement.description,
            Advertisement.price,
        ]
        if need_uname:
            options_to_select.append(Advertisement.owners_username)
        res = await self._request_to_db(
            AsyncSession.execute,
            select(*options_to_select).
            where(Advertisement.advertisement_id == ad_id)
        )
        return res.first()
    

    async def delete_ad(self, ad_id: UUID3, user_id: int):
        await self._request_to_db(
            AsyncSession.execute,
            delete(Advertisement).
            where(Advertisement.advertisement_id == ad_id)
        )
        user_ads = await self.get_user_ads(user_id)
        user_ads.remove(ad_id)

        await self._request_to_db(
            AsyncSession.execute,
            update(User).
            where(User.user_id == user_id).
            values(advertisements=user_ads)
        )
    

    async def get_all_others_ads(self, user_id: int) -> list[UUID3]:
        user_ads = await self.get_user_ads(user_id)
        res: ScalarResult = await self._request_to_db(
            AsyncSession.scalars, 
            select(Advertisement.advertisement_id).
            where(
                Advertisement.advertisement_id.not_in(user_ads)
            )
        )
        return res.fetchall()
        