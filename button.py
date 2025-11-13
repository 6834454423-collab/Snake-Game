# button.py
# ---------------------------
# This file defines a simple Button class for clickable UI elements.

import pygame
from settings import BLACK, WHITE, GRAY

class Button:
    def __init__(self, x, y, width, height, text, font, bg_color=GRAY, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = (min(bg_color[0] + 30, 255), 
                            min(bg_color[1] + 30, 255),
                            min(bg_color[2] + 30, 255))

    def draw(self, screen):
        """Draw the button on the screen with hover effect"""
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.bg_color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # border

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        """Return True if button was clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False
