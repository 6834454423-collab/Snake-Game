import pygame
import math
from settings import ROWS, COLS, CELL_SIZE, BLACK, GREEN, RED, BOARD_OFFSET_X, BOARD_OFFSET_Y

def get_pos(cell):
    """แปลงหมายเลขช่อง (0–100) เป็นพิกัดบนกระดาน"""
    if cell == 100: 
        # ช่อง FINISH อยู่ข้างซ้ายของช่อง 99
        last_row = 99 // 10
        last_col = 99 % 10
        if last_row % 2 == 1:
            last_col = 9 - last_col
        last_x = BOARD_OFFSET_X + last_col * CELL_SIZE
        last_y = BOARD_OFFSET_Y + (ROWS - 1 - last_row) * CELL_SIZE
        return last_x - CELL_SIZE, last_y  # ขยับซ้ายออกมา 25px

    # คำนวณปกติ
    row = cell // 10
    col = cell % 10
    if row % 2 == 1:
        col = 9 - col
    x = BOARD_OFFSET_X + col * CELL_SIZE
    y = BOARD_OFFSET_Y + (ROWS - 1 - row) * CELL_SIZE
    return x, y


class Board:
    def __init__(self, font):
        self.font = font

    def draw(self, screen, snakes, ladders):
        screen.fill((220, 220, 220))

        # วาดช่อง 0–99
        for row in range(ROWS):
            for col in range(COLS):
                x = BOARD_OFFSET_X + col * CELL_SIZE
                y = BOARD_OFFSET_Y + (ROWS - 1 - row) * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, BLACK, rect, 2)

                cell_num = row * 10 + col
                if row % 2 == 1:
                    cell_num = row * 10 + (9 - col)

                # ข้อความในแต่ละช่อง
                if cell_num == 0:
                    label = "START"
                elif cell_num == 99:
                    label = "99"
                else:
                    label = str(cell_num)
                text = self.font.render(label, True, BLACK)
                screen.blit(text, (x + 5, y + 5))

        # ช่อง FINISH (อยู่นอกกระดาน ด้านซ้ายของช่อง 99)
        finish_x, finish_y = get_pos(100)
        finish_rect = pygame.Rect(finish_x, finish_y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, (255, 215, 0), finish_rect)
        pygame.draw.rect(screen, BLACK, finish_rect, 3)
        f_text = self.font.render("FINISH", True, BLACK)
        screen.blit(f_text, (finish_x + 5, finish_y + 15))

        # วาดบันได
        for start, end in ladders.items():
            sx, sy = get_pos(start)
            ex, ey = get_pos(end)
            pygame.draw.line(screen, GREEN,
                             (sx + CELL_SIZE//2, sy + CELL_SIZE//2),
                             (ex + CELL_SIZE//2, ey + CELL_SIZE//2), 5)

        # วาดงู (เส้นคลื่น)
        for start, end in snakes.items():
            sx, sy = get_pos(start)
            ex, ey = get_pos(end)
            x1, y1 = sx + CELL_SIZE // 2, sy + CELL_SIZE // 2
            x2, y2 = ex + CELL_SIZE // 2, ey + CELL_SIZE // 2

            num_points = 30
            snake_points = []
            for i in range(num_points + 1):
                t = i / num_points
                x = x1 + (x2 - x1) * t
                y = y1 + (y2 - y1) * t
                wave = math.sin(t * math.pi * 6) * 15
                dx = x2 - x1
                dy = y2 - y1
                length = math.hypot(dx, dy)
                if length == 0:
                    continue
                nx = -dy / length
                ny = dx / length
                x += nx * wave
                y += ny * wave
                snake_points.append((x, y))

            if len(snake_points) > 1:
                pygame.draw.lines(screen, (200, 0, 0), False, snake_points, 5)
                pygame.draw.circle(screen, (255, 50, 50), snake_points[0], 8)
                pygame.draw.circle(screen, (0, 0, 0), snake_points[0], 8, 2)
