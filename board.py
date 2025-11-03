# board.py
import pygame
from settings import ROWS, COLS, CELL_SIZE, BLACK, WHITE, GREEN, RED, ORANGE, BOARD_OFFSET_X, BOARD_OFFSET_Y

def draw_board(screen, font):
    screen.fill(WHITE)
    for row in range(ROWS):
        for col in range(COLS):
            x = BOARD_OFFSET_X + col*CELL_SIZE
            y = BOARD_OFFSET_Y + row*CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 4)  # เส้นหนา Pixel
            # วางเลขช่อง
            cell_num = row * 10 + col
            if row % 2 == 1:
                cell_num = row * 10 + (9 - col)
            num_text = font.render(str(cell_num), True, BLACK)
            screen.blit(num_text, (x + 5, y + 5))

def get_pos(cell):
    row = cell // 10
    col = cell % 10
    if row % 2 == 1:
        col = 9 - col
    x = BOARD_OFFSET_X + col * CELL_SIZE
    y = BOARD_OFFSET_Y + row * CELL_SIZE
    return x, y

def draw_snakes_ladders(screen, snakes, ladders):
    for start, end in ladders.items():
        start_x, start_y = get_pos(start)
        end_x, end_y = get_pos(end)
        pygame.draw.line(screen, GREEN, (start_x + CELL_SIZE//2, start_y + CELL_SIZE//2),
                         (end_x + CELL_SIZE//2, end_y + CELL_SIZE//2), 6)
        pygame.draw.circle(screen, ORANGE, (end_x + CELL_SIZE//2, end_y + CELL_SIZE//2), 8)

    for start, end in snakes.items():
        start_x, start_y = get_pos(start)
        end_x, end_y = get_pos(end)
        pygame.draw.line(screen, RED, (start_x + CELL_SIZE//2, start_y + CELL_SIZE//2),
                         (end_x + CELL_SIZE//2, end_y + CELL_SIZE//2), 6)
        pygame.draw.circle(screen, BLACK, (end_x + CELL_SIZE//2, end_y + CELL_SIZE//2), 8)
