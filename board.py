# board.py
import pygame
import math
from settings import ROWS, COLS, CELL_SIZE, BOARD_OFFSET_X, BOARD_OFFSET_Y, BLACK, BROWN, GREY

def get_pos(cell):
    """
    แปลงหมายเลขช่อง (0..100) เป็นพิกัดซ้ายบนของช่อง (x, y)
    cell: 0..100 (0=start, 100=finish)
    ช่องจริงบนบอร์ดจะเป็น 0..99 (10x10) และช่อง 100 เป็น FINISH
    """
    # ช่องปกติ 0..99
    if 0 <= cell <= 99:
        row = cell // 10
        col = cell % 10
        # Boustrophedon (สลับทิศทางทุกแถว)
        if row % 2 == 1:
            col = 9 - col
        x = BOARD_OFFSET_X + col * CELL_SIZE
        y = BOARD_OFFSET_Y + (ROWS - 1 - row) * CELL_SIZE
        return x, y

    # ช่อง FINISH (100) วางไว้ข้างๆ ช่อง 99 (ซ้ายของช่อง 99 เพื่อให้แยก)
    if cell == 100:
        last_row = 99 // 10
        last_col = 99 % 10
        if last_row % 2 == 1:
            last_col = 9 - last_col
        last_x = BOARD_OFFSET_X + last_col * CELL_SIZE
        last_y = BOARD_OFFSET_Y + (ROWS - 1 - last_row) * CELL_SIZE
        # วาง finish ข้างซ้ายของช่อง 99
        return last_x - CELL_SIZE - 10, last_y

    return -1, -1

def get_cell_center(cell):
    x, y = get_pos(cell)
    return x + CELL_SIZE // 2, y + CELL_SIZE // 2

class Board:
    def __init__(self, font):
        self.font = font

    def draw_grid(self, surface, offset=(0, 0)):
        ox, oy = offset
        for row in range(ROWS):
            for col in range(COLS):
                x = BOARD_OFFSET_X + col * CELL_SIZE + ox
                y = BOARD_OFFSET_Y + (ROWS - 1 - row) * CELL_SIZE + oy
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, GREY, rect)
                pygame.draw.rect(surface, BLACK, rect, 2)

                # คำนวณหมายเลข cell (Boustrophedon)
                cell_num = row * 10 + col
                if row % 2 == 1:
                    cell_num = row * 10 + (9 - col)

                # START ให้เป็นคำ, ช่องอื่นใส่เลข
                label = "START" if cell_num == 0 else str(cell_num)
                text = self.font.render(label, True, BLACK)
                surface.blit(text, (x + 4, y + 4))

    def draw_finish(self, surface):
        fx, fy = get_pos(100)
        frect = pygame.Rect(fx, fy, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, (255, 215, 0), frect)  # สีทอง
        pygame.draw.rect(surface, BLACK, frect, 3)
        ftxt = self.font.render("FINISH", True, BLACK)
        surface.blit(ftxt, (fx + 4, fy + 14))

    def draw_ladders(self, surface, ladders):
        for start, end in ladders.items():
            sx, sy = get_pos(start)
            ex, ey = get_pos(end)
            c1 = (sx + CELL_SIZE//2, sy + CELL_SIZE//2)
            c2 = (ex + CELL_SIZE//2, ey + CELL_SIZE//2)

            dx = c2[0] - c1[0]
            dy = c2[1] - c1[1]
            length = math.hypot(dx, dy)
            if length == 0:
                continue

            # vector perpendicular (for ladder thickness)
            nx = -dy / length
            ny = dx / length
            offset = 6

            p1s = (c1[0] - nx*offset, c1[1] - ny*offset)
            p1e = (c2[0] - nx*offset, c2[1] - ny*offset)
            p2s = (c1[0] + nx*offset, c1[1] + ny*offset)
            p2e = (c2[0] + nx*offset, c2[1] + ny*offset)

            pygame.draw.line(surface, BROWN, p1s, p1e, 6)
            pygame.draw.line(surface, BROWN, p2s, p2e, 6)
            pygame.draw.line(surface, BLACK, p1s, p1e, 1)
            pygame.draw.line(surface, BLACK, p2s, p2e, 1)

    def draw_snakes(self, surface, snakes):
        for start, end in snakes.items():
            sx, sy = get_pos(start)
            ex, ey = get_pos(end)
            x1, y1 = sx + CELL_SIZE//2, sy + CELL_SIZE//2
            x2, y2 = ex + CELL_SIZE//2, ey + CELL_SIZE//2

            dx = x2 - x1
            dy = y2 - y1
            length = math.hypot(dx, dy)
            if length == 0:
                continue

            nx = -dy / length
            ny = dx / length
            num_points = 30
            points = []
            for i in range(num_points + 1):
                t = i / num_points
                x = x1 + dx * t
                y = y1 + dy * t
                wave = math.sin(t * math.pi * 6) * 12
                x += nx * wave
                y += ny * wave
                points.append((x, y))

            pygame.draw.lines(surface, (200, 0, 0), False, points, 6)
            # head
            pygame.draw.circle(surface, (255, 60, 60), points[0], 8)
            pygame.draw.circle(surface, BLACK, points[0], 8, 2)

    def draw(self, surface, snakes, ladders, offset=(0,0)):
        surface.fill(WHITE := (255,255,255))
        self.draw_grid(surface, offset)
        self.draw_finish(surface)
        self.draw_ladders(surface, ladders)
        self.draw_snakes(surface, snakes)
