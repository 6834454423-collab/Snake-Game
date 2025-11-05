# snakes_ladders.py
import random

class SnakeLadderGenerator:
    def __init__(self, num_snakes=5, num_ladders=5):
        self.num_snakes = num_snakes
        self.num_ladders = num_ladders

    def generate(self):
        snakes = {}
        ladders = {}
        used = set()

        for _ in range(self.num_ladders):
            start = random.randint(2, 80)
            end = start + random.randint(10, 18)
            if end >= 99 or start in used:
                continue
            ladders[start] = end
            used.add(start)

        for _ in range(self.num_snakes):
            start = random.randint(15, 95)
            end = start - random.randint(8, 20)
            if end <= 1 or start in used:
                continue
            snakes[start] = end
            used.add(start)

        return snakes, ladders
