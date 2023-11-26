from datetime import datetime

from sqlalchemy import (
    String,
    ARRAY,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.consts import DEFAULT_AD_PHOTO
from bot.db.config import Base

__all__ = ('User', 'Advertisement')


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    username: Mapped[str] = mapped_column(String(40))
    advertisements: Mapped[list['Advertisement']] = relationship(
        back_populates='user',
        cascade='all, delete'
    )


class Advertisement(Base):
    __tablename__ = 'advertisements'

    advertisement_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(40))
    photo: Mapped[list[str]] = mapped_column(ARRAY(String), default=[DEFAULT_AD_PHOTO])
    description: Mapped[str]
    price: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'))
    user: Mapped['User'] = relationship(back_populates='advertisements', foreign_keys=[user_id])
