from typing import List

from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


chat_users = Table(
    "chat_users",
    Base.metadata,
    Column("chat_id", ForeignKey("chat.id"), primary_key=True),
    Column("user_id", ForeignKey("user.id"), primary_key=True)
)


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(primary_key=True)
    users: Mapped[List["User"]] = relationship(secondary=chat_users, back_populates="chats")


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    chats: Mapped[List[Chat]] = relationship(secondary=chat_users, back_populates="users")
