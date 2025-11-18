#settings.py
import pygame

pygame.init()
info = pygame.display.Info()

# nearly full screen (95% of actual screen)
SCREEN_WIDTH = int(info.current_w * 0.95)
SCREEN_HEIGHT = int(info.current_h * 0.9)

# board size relative to screen
BOARD_MARGIN = 100
CELL_COUNT = 10
CELL_SIZE = (SCREEN_HEIGHT - 2 * BOARD_MARGIN) // CELL_COUNT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
BLUE = (100, 149, 237)
LIGHT_BLUE = (173, 216, 230)
GREEN = (50, 205, 50)
RED = (220, 20, 60)

# Aliases and extras used by other modules
WIDTH = SCREEN_WIDTH
HEIGHT = SCREEN_HEIGHT

# grid aliases
ROWS = CELL_COUNT
COLS = CELL_COUNT

# center the board on screen
BOARD_OFFSET_X = (WIDTH - (CELL_SIZE * COLS)) // 2
BOARD_OFFSET_Y = (HEIGHT - (CELL_SIZE * ROWS)) // 2

# synonyms
GREY = GRAY
BROWN = (139, 69, 19)

# Player colors used in `player.py`
PLAYER_COLORS = [
	(220, 20, 60),   # red
	(65, 105, 225),  # royal blue
	(34, 139, 34),   # forest green
	(255, 165, 0),   # orange
]

# Board color options and current selection
BOARD_COLOR_OPTIONS = [
    (GRAY, "Grey"),
    (LIGHT_BLUE, "Light Blue"),
    (GREEN, "Green"),
    (BROWN, "Brown"),
]

# Default board color (cells)
BOARD_COLOR = GRAY

# Christmas theme toggle
CHRISTMAS_THEME = False

# Christmas palette (used by confetti and optional themed cells)
CHRISTMAS_PALETTE = [
	(220, 20, 60),   # red
	(34, 139, 34),   # green
	(255, 215, 0),   # gold
]
