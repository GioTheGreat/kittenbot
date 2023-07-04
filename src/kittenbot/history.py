from typing import Optional

from attr import define
from sqlalchemy import Engine, select, exists
from sqlalchemy.orm import Session, joinedload
from telegram import Message

from . import entities


@define
class History:
    engine: Engine

    def store(self, message: Message) -> None:
        entities.User.metadata.create_all(self.engine, checkfirst=True)
        entities.Chat.metadata.create_all(self.engine, checkfirst=True)
        entities.chat_users.metadata.create_all(self.engine, checkfirst=True)
        with Session(self.engine) as session:
            chat = entities.Chat(id=message.chat_id)
            is_new_chat = self._is_new_chat(session, message)
            if is_new_chat:
                print(f"adding new chat id {chat.id}")
                session.add(chat)
            user = self._get_user_by_id(session, message.from_user.id)
            if user:
                if not is_new_chat and not any(user_chat.id == chat.id for user_chat in user.chats):
                    user.chats.append(chat)
            else:
                user = entities.User(id=message.from_user.id, chats=[chat], username=message.from_user.username)
                print(f"adding new user {user.id}")
                session.add(user)
            session.commit()

    def get_user_id(self, username: str) -> Optional[int]:
        statement = select(entities.User.id).where(entities.User.username == username)
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
