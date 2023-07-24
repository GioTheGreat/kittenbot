from datetime import timedelta

import sqlalchemy

from kittenbot import entities
from kittenbot.clock import ProdClock
from kittenbot.slowmode_user_repository import SlowmodeUserRepository


def test():
    engine = sqlalchemy.create_engine("sqlite:///:memory:")
    entities.SlowmodeUser.metadata.create_all(engine, checkfirst=True)
    repo = SlowmodeUserRepository(engine, ProdClock())
    r1 = repo.create_restriction(1, 1, timedelta(minutes=5))
    r2 = repo.get_active_restriction(1, 1)
    assert r1.user_id == r2.user_id and r1.chat_id == r2.chat_id
