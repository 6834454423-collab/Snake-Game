# player.py
import pygame
from settings import PLAYER_COLORS, CELL_SIZE
from board import get_pos

class Player:
    def __init__(self, player_id):
        self.id = player_id
        self.position = 0  # เริ่มที่ช่อง 0 (START)
        self.color = PLAYER_COLORS[player_id]

    def move(self, steps):
        self.position += steps
        if self.position > 100:
            self.position = 100  # FINISH

    def draw(self, screen):
        x, y = get_pos(self.position)
        center = (x + CELL_SIZE // 2, y + CELL_SIZE // 2)
        pygame.draw.circle(screen, (0, 0, 0), center, CELL_SIZE // 3 + 3)
        pygame.draw.circle(screen, self.color, center, CELL_SIZE // 3)
