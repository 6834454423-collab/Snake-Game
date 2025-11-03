# snakes_ladders.py
import random

def random_snakes_ladders():
    snakes = {}
    ladders = {}
    while len(snakes) < 5:
        start = random.randint(30, 98)
        end = random.randint(1, start - 1)
        if start != 100 and end != 20:
            snakes[start] = end
    while len(ladders) < 5:
        start = random.randint(1, 70)
        end = random.randint(start + 1, 99)
        ladders[start] = end
    return snakes, ladders
