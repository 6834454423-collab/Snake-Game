# utils.py
import pygame
from settings import BLACK

def draw_text(surface, text, pos, font, color=BLACK):
    """วาดข้อความง่าย ๆ"""
    txt = font.render(text, True, color)
    surface.blit(txt, pos)
