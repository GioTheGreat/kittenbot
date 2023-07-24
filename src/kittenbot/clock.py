from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime:
        pass


class ProdClock(Clock):
    def now(self) -> datetime:
        return datetime.now()
