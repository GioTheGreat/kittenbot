from typing import Optional, List

from attr import define
from loguru import logger
from sqlalchemy import Engine, select, exists, insert
from sqlalchemy.orm import Session, joinedload
from telegram import Message

from . import entities


@define
class History:
    engine: Engine

    def store(self, message: Message) -> None:
        with Session(self.engine) as session:
            chat = entities.Chat(id=message.chat_id)
            is_new_chat = self._is_new_chat(session, message)
            if is_new_chat:
                logger.debug("adding new chat id {chat_id}", chat_id=chat.id)
                session.add(chat)
            user = self._get_user_by_id(session, message.from_user.id)
            if not user:
                user = entities.User(id=message.from_user.id, username=message.from_user.username)
                logger.debug("adding new user id {user_id}", user_id=user.id)
                session.add(user)

            is_known_relation_user_to_chat = session.query(
                exists(entities.chat_users)
                .where(entities.chat_users.c.chat_id == chat.id
                       and entities.chat_users.c.user_id == user.id)
            )

            if not is_known_relation_user_to_chat:
                session.execute(
                    insert(entities.chat_users)
                    .values(chat_id=chat.id, user_id=user.id)
                )

            session.commit()

    def get_user_id(self, username: str) -> List[int]:
        statement = select(entities.User.id).where(entities.User.username == username)
        with Session(self.engine) as session:
            return list(session.execute(statement).scalars())

    def get_user_name(self, user_id: int) -> Optional[str]:
        statement = select(entities.User.username).where(entities.User.id == user_id)
        with Session(self.engine) as session:
            return session.execute(statement).scalar()

    def _is_new_chat(self, session: Session, message: Message) -> bool:
        return not session.query(
            exists(entities.Chat)
            .where(entities.Chat.id == message.chat_id)
        ).scalar()

    def _get_user_by_id(self, session: Session, id_: int) -> Optional[entities.User]:
        return session.execute(
            select(entities.User)
            .where(entities.User.id == id_)
            .options(joinedload(entities.User.chats))
        ).scalar()
