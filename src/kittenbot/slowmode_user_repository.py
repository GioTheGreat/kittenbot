from datetime import datetime, timedelta
from typing import Optional

from attr import define
from sqlalchemy import Engine, select, delete, update
from sqlalchemy.orm import Session

from kittenbot.clock import Clock
from kittenbot.entities import SlowmodeUser


@define
class SlowmodeUserRepository:
    engine: Engine
    clock: Clock

    def get_active_restriction(self, chat_id: int, user_id: int) -> Optional[SlowmodeUser]:
        statement = select(SlowmodeUser).where(
            SlowmodeUser.user_id == user_id
            and SlowmodeUser.chat_id == chat_id
            and SlowmodeUser.until_date > self.clock.now()
        )
        with Session(self.engine) as session:
            return session.execute(statement).scalar()

    def create_restriction(
            self,
            chat_id: int,
            user_id: int,
            interval: timedelta,
            until_date: Optional[datetime] = None
    ) -> SlowmodeUser:
        restriction = SlowmodeUser(
            user_id=user_id,
            chat_id=chat_id,
            interval=interval,
            until_date=until_date
        )
        with Session(self.engine, expire_on_commit=False) as session:
            session.add(restriction)
            session.commit()
        return restriction

    def delete_restriction(self, chat_id: int, user_id: int) -> None:
        statement = delete(SlowmodeUser).where(
            SlowmodeUser.chat_id == chat_id
            and SlowmodeUser.user_id == user_id
        )
        with Session(self.engine) as session:
            session.execute(statement)
            session.commit()

    def update_restriction(self, chat_id: int, user_id: int, interval: timedelta) -> SlowmodeUser:
        statement = update(SlowmodeUser).where(
            SlowmodeUser.chat_id == chat_id
            and SlowmodeUser.user_id == user_id
        ).values(interval=interval)
        with Session(self.engine) as session:
            restriction = session.execute(statement).scalar()
            session.commit()
        return restriction
