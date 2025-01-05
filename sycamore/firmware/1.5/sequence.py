import random

class Sequence:
    def __init__(self):
        self._sequence = [None] * 64
        self.seed()

    @property
    def sequence(self):
        return self._sequence

    def seed(self):
        for i in range(len(self._sequence)):
            self._sequence[i] = random.randint(0, 4095)
