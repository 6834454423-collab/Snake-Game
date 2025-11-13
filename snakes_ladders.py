# snakes_ladders.py
import random

class SnakeLadderGenerator:
    def __init__(self, num_snakes=5, num_ladders=5):
        self.num_snakes = num_snakes
        self.num_ladders = num_ladders

    def generate(self):
        snakes = {}
        ladders = {}
        used = set([0, 100])

        # ladders: start < end
        count = 0
        while count < self.num_ladders:
            start = random.randint(2, 70)
            end = start + random.randint(8, 18)
            if end >= 99 or start in used or end in used:
                continue
            ladders[start] = end
            used.add(start); used.add(end)
            count += 1

        # snakes: start > end
        count = 0
        while count < self.num_snakes:
            start = random.randint(15, 95)
            end = start - random.randint(8, 20)
            if end <= 1 or start in used or end in used:
                continue
            snakes[start] = end
            used.add(start); used.add(end)
            count += 1

        return snakes, ladders
