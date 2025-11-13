# player.py
from settings import PLAYER_COLORS, CELL_SIZE
from board import get_pos, get_cell_center
import colorsys
import pygame

class Player:
    def __init__(self, pid, radius=16):
        self.id = pid
        self.position = 0
        self.radius = radius

        # choose a color from PLAYER_COLORS; if we run out, generate distinct hues
        try:
            base_colors = list(PLAYER_COLORS)
        except Exception:
            base_colors = [
                (200, 30, 30),   # red
                (30, 160, 30),   # green
                (30, 60, 200),   # blue
                (220, 180, 30),  # yellow
                (180, 30, 180),  # magenta
                (30, 180, 180),  # cyan
            ]

        if pid < len(base_colors):
            self.color = base_colors[pid]
        else:
            # generate a visually distinct color using HSV spread
            h = (pid * 0.618033988749895) % 1.0  # golden ratio fraction for distribution
            r, g, b = colorsys.hsv_to_rgb(h, 0.7, 0.9)
            self.color = (int(r * 255), int(g * 255), int(b * 255))

    def _get_draw_coords(self, all_players=None, offset=(0,0)):
        """
        Compute draw coordinates for this player. If multiple players share the same
        cell, offset them so they don't overlap.
        """
        cx, cy = get_cell_center(self.position)
        ox, oy = offset

        if not all_players:
            return (cx + ox, cy + oy)

        # players in same cell
        same = [p for p in all_players if getattr(p, "position", None) == self.position]
        if len(same) == 1:
            return (cx + ox, cy + oy)

        index = same.index(self)
        # placement offsets for up to 6 players; will wrap for more
        placements = [
            (-self.radius - 4, -self.radius - 4),
            ( self.radius + 4, -self.radius - 4),
            (-self.radius - 4,  self.radius + 4),
            ( self.radius + 4,  self.radius + 4),
            (0, - (self.radius + 8)),
            (0,  (self.radius + 8)),
        ]
        px, py = placements[index % len(placements)]
        return (cx + px + ox, cy + py + oy)

    def draw(self, surface, all_players=None, offset=(0,0)):
        x, y = self._get_draw_coords(all_players=all_players, offset=offset)
        pygame.draw.circle(surface, self.color, (int(x), int(y)), self.radius)
        pygame.draw.circle(surface, (0,0,0), (int(x), int(y)), self.radius, 2)

    def animate_move(self, surface, board, steps, snakes, ladders, players, screen_update_fn, delay=120):
        """เดินทีละช่อง (ใช้ screen_update_fn เพื่อให้ caller วาด UI ที่เหลือ)"""
        for _ in range(steps):
            # เพิ่มตำแหน่งทีละ 1 (ฉีกเพดานไว้ไม่ให้เกิน 100)
            self.position += 1
            if self.position > 100:
                # bounce back
                self.position = 100 - (self.position - 100)
            # เรียก callback ให้วาดหน้าจอ (board, players ฯลฯ)
            screen_update_fn()
            pygame.time.delay(delay)

    def move_to(self, target):
        self.position = target
