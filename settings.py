# settings.py
WIDTH, HEIGHT = 1500, 600  # ขนาดหน้าจอใหญ่
ROWS, COLS = 10, 10
CELL_SIZE = 60  # ขนาดช่องคงที่เพื่อให้ง่ายต่อการคำนวณ

# คำนวณ Offset กระดานให้อยู่กลางจอ
BOARD_WIDTH = CELL_SIZE * COLS
BOARD_HEIGHT = CELL_SIZE * ROWS
BOARD_OFFSET_X = (WIDTH - BOARD_WIDTH) // 2
BOARD_OFFSET_Y = (HEIGHT - BOARD_HEIGHT) // 2

# Pixel color palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (160, 32, 240)
BROWN = (139, 69, 19)

PLAYER_COLORS = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA]
