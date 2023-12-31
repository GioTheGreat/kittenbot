import random
from typing import TypeVar, List, Optional

from attr import define

T = TypeVar("T")


@define
class RandomGenerator:
    def get_bool(self, probability: float) -> bool:
        return random.random() <= probability

    def get_int(self, min_inclusive: int, max_inclusive: int):
        return random.randint(min_inclusive, max_inclusive)

    def choice(self, items: List[T]) -> Optional[T]:
        if not items:
            return None
        return random.choice(items)
