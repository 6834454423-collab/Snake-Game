# players.py
import pygame
from settings import PLAYER_COLORS, CELL_SIZE
from board import get_pos

def draw_players(screen, players):
    for idx, pos in enumerate(players):
        x, y = get_pos(pos)
        center = (x + CELL_SIZE//2, y + CELL_SIZE//2)
        radius = CELL_SIZE // 3

        pygame.draw.circle(screen, (0, 0, 0), center, radius + 3)
        pygame.draw.circle(screen, PLAYER_COLORS[idx], center, radius)
        pygame.draw.circle(screen, (255, 255, 255), center, radius//3)
