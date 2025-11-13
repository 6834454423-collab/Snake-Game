# dice.py
import random

class Dice:
    def roll(self):
        """คืนค่า 1..6"""
        return random.randint(1, 6)
