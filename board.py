# board.py (Enhanced Ladder Visibility)
import pygame
import math
import settings
import colorsys
from settings import ROWS, COLS, CELL_SIZE, BOARD_OFFSET_X, BOARD_OFFSET_Y, BLACK, BROWN



def get_pos(cell):
    """
    แปลงหมายเลขช่อง (0..100) เป็นตำแหน่งซ้ายบนของช่อง
    """
    if 0 <= cell <= 99:
        row = cell // 10
        col = cell % 10
        if row % 2 == 1:
            col = 9 - col
        x = BOARD_OFFSET_X + col * CELL_SIZE
        y = BOARD_OFFSET_Y + (ROWS - 1 - row) * CELL_SIZE
        return x, y

    if cell == 100:
        last_row = 99 // 10
        last_col = 99 % 10
        if last_row % 2 == 1:
            last_col = 9 - last_col
        last_x = BOARD_OFFSET_X + last_col * CELL_SIZE
        last_y = BOARD_OFFSET_Y + (ROWS - 1 - last_row) * CELL_SIZE
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
                cell_idx = row * COLS + col

                # Christmas pattern
                if getattr(settings, "CHRISTMAS_THEME", False):
                    if (row + col) % 2 == 0:
                        base = (200, 30, 60)
                    else:
                        base = (30, 140, 60)
                    nr_i, ng_i, nb_i = base
                    alpha = 220
                    cell_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    cell_surf.fill((nr_i, ng_i, nb_i, alpha))
                    surface.blit(cell_surf, (x, y))

                    seed = (cell_idx * 97) % 100
                    if seed < 8:
                        sx = x + CELL_SIZE - 8 - ((cell_idx * 19) % 6)
                        sy = y + 6 + ((cell_idx * 11) % 10)
                        pygame.draw.circle(surface, (255, 255, 255, 200), (sx, sy), 2)
                else:
                    base = settings.BOARD_COLOR
                    r_f, g_f, b_f = base[0] / 255, base[1] / 255, base[2] / 255
                    h, s, v = colorsys.rgb_to_hsv(r_f, g_f, b_f)
                    delta = ((cell_idx * 37) % 13) - 6
                    factor = 1.0 + (delta / 500.0)
                    v2 = max(0, min(1, v * factor))
                    nr, ng, nb = colorsys.hsv_to_rgb(h, s, v2)
                    nr_i, ng_i, nb_i = int(nr * 255), int(ng * 255), int(nb * 255)

                    cell_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    cell_surf.fill((nr_i, ng_i, nb_i, 210))
                    surface.blit(cell_surf, (x, y))

                pygame.draw.rect(surface, BLACK, rect, 2)

                cell_num = row * 10 + col
                if row % 2 == 1:
                    cell_num = row * 10 + (9 - col)

                label = "START" if cell_num == 0 else str(cell_num)
                text = self.font.render(label, True, BLACK)
                surface.blit(text, (x + 4, y + 4))

    def draw_finish(self, surface):
        fx, fy = get_pos(100)
        rect = pygame.Rect(fx, fy, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, (255, 215, 0), rect)
        pygame.draw.rect(surface, BLACK, rect, 3)
        surface.blit(self.font.render("FINISH", True, BLACK), (fx + 4, fy + 14))

    # -------------------------------------------------------
    # ENHANCED LADDER DRAWING (double rails + rungs + outline)
    # -------------------------------------------------------
    def draw_ladders(self, surface, ladders):
        for start, end in ladders.items():
            sx, sy = get_cell_center(start)
            ex, ey = get_cell_center(end)

            dx = ex - sx
            dy = ey - sy
            length = math.hypot(dx, dy)
            if length == 0:
                continue

            nx = -dy / length
            ny = dx / length
            rail_offset = 10

            # Rails
            r1s = (sx - nx * rail_offset, sy - ny * rail_offset)
            r1e = (ex - nx * rail_offset, ey - ny * rail_offset)
            r2s = (sx + nx * rail_offset, sy + ny * rail_offset)
            r2e = (ex + nx * rail_offset, ey + ny * rail_offset)

            # Outline (thicker black)
            pygame.draw.line(surface, BLACK, r1s, r1e, 10)
            pygame.draw.line(surface, BLACK, r2s, r2e, 10)

            # Main rails (brown)
            pygame.draw.line(surface, BROWN, r1s, r1e, 6)
            pygame.draw.line(surface, BROWN, r2s, r2e, 6)

            # Rungs
            steps = 6
            for i in range(steps + 1):
                t = i / steps
                rx = sx + dx * t
                ry = sy + dy * t
                p_start = (rx - nx * rail_offset, ry - ny * rail_offset)
                p_end = (rx + nx * rail_offset, ry + ny * rail_offset)
                pygame.draw.line(surface, BLACK, p_start, p_end, 6)
                pygame.draw.line(surface, (220, 180, 120), p_start, p_end, 4)

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

            points = []
            for i in range(31):
                t = i / 30
                px = x1 + dx * t
                py = y1 + dy * t
                wave = math.sin(t * math.pi * 6) * 12
                px += nx * wave
                py += ny * wave
                points.append((px, py))

            pygame.draw.lines(surface, (200, 0, 0), False, points, 6)
            pygame.draw.circle(surface, (255, 60, 60), points[0], 8)
            pygame.draw.circle(surface, BLACK, points[0], 8, 2)

    def draw(self, surface, snakes, ladders, offset=(0, 0)):
        self.draw_grid(surface, offset)
        self.draw_finish(surface)
        self.draw_ladders(surface, ladders)
        self.draw_snakes(surface, snakes)
