from sqlalchemy import (
    Column,
    Integer, BIGINT,
    DateTime,
    CHAR, String,
    UUID,
    ARRAY,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs

from consts import DEFAULT_AD_PHOTO


__all__ = ("Base", "User", "Advertisement")


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, nullable=False)
    username = Column(CHAR(40), nullable=False)
    advertisements = Column(ARRAY(UUID))


class Advertisement(Base):
    __tablename__ = "advertisement"

    id = Column(Integer, primary_key=True, autoincrement=True)
    advertisement_id = Column(UUID, nullable=False)
    title = Column(CHAR(40), nullable=False)
    photo = Column(ARRAY(String), default=[DEFAULT_AD_PHOTO])
    description = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    owners_username = Column(CHAR(40))
