import random

from attr import define


@define
class BinaryRandomGenerator:
    probability: float

    def generate(self) -> bool:
        return random.random() <= self.probability
