from datetime import datetime

from sqlalchemy import (
    DateTime,
    CHAR, String,
    ARRAY, ForeignKey, func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs

from bot.consts import DEFAULT_AD_PHOTO


__all__ = ('Base', 'User', 'Advertisement')


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False, nullable=False)
    username: Mapped[str] = mapped_column(CHAR(40), nullable=False)
    advertisements: Mapped[list['Advertisement']] = relationship(
        back_populates='user',
        cascade='all, delete'
    )


class Advertisement(Base):
    __tablename__ = 'advertisements'

    advertisement_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(CHAR(40), nullable=False)
    photo: Mapped[list[str]] = mapped_column(ARRAY(String), default=[DEFAULT_AD_PHOTO])
    description: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'))
    user: Mapped['User'] = relationship(back_populates='advertisements', foreign_keys=[user_id])
