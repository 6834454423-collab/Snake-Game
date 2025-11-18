# animation.py
import pygame
import math
from board import get_cell_center

class Animation:
    def __init__(self, step_delay=180):
        """
        step_delay: total milliseconds to animate one cell step (higher => slower).
        """
        self.step_delay = step_delay

    def _lerp(self, a, b, t):
        """Linear interpolation helper: returns a + (b-a)*t for t in [0..1]."""
        return a + (b - a) * t

    def _call_screen_update(self, screen_update_fn, player, x, y):
        # Prefer calling with draw_temp so caller can skip static token
        try:
            screen_update_fn(draw_temp=(player, x, y))
        except TypeError:
            try:
                screen_update_fn()
            except Exception:
                pass

    def _draw_token(self, surface, player, x, y):
        # If the player has an image (preferred), blit it centered at (x,y).
        # Otherwise fall back to drawing a colored circle using player's color/radius.
        img = getattr(player, "image", None)
        if img is not None:
            try:
                rect = img.get_rect(center=(int(x), int(y)))
                surface.blit(img, rect)
            except Exception:
                # fallback to circle if blit fails
                color = getattr(player, "color", (0, 0, 0))
                radius = getattr(player, "radius", 16)
                pygame.draw.circle(surface, color, (int(x), int(y)), radius)
                pygame.draw.circle(surface, (0, 0, 0), (int(x), int(y)), radius, 2)
        else:
            color = getattr(player, "color", (0, 0, 0))
            radius = getattr(player, "radius", 16)
            pygame.draw.circle(surface, color, (int(x), int(y)), radius)
            pygame.draw.circle(surface, (0, 0, 0), (int(x), int(y)), radius, 2)

    def _animate_step_hop(self, surface, player, start_pos, end_pos, duration_ms, screen_update_fn, hop_height=12):
        """
        Animate a single cell 'hop' from start_pos to end_pos.
        Creates a small upward arc so movement looks like jumping between squares.
        """
        sx, sy = start_pos
        ex, ey = end_pos
        if duration_ms <= 0:
            self._call_screen_update(screen_update_fn, player, ex, ey)
            self._draw_token(surface, player, ex, ey)
            pygame.display.flip()
            return

        fps_target = 60.0
        frame_ms = 1000.0 / fps_target
        frames = max(1, int(math.ceil(duration_ms / frame_ms)))
        for f in range(frames):
            t = (f + 1) / frames  # 0..1
            # horizontal/vertical linear interpolation
            x = self._lerp(sx, ex, t)
            y = self._lerp(sy, ey, t)
            # hop offset (sinusoidal) so it goes up then down
            hop = math.sin(math.pi * t) * hop_height
            # subtract hop so it moves up then down
            y -= hop
            # redraw background skipping the static token and draw moving token
            self._call_screen_update(screen_update_fn, player, x, y)
            self._draw_token(surface, player, x, y)
            pygame.display.flip()
            pygame.event.pump()
            pygame.time.delay(int(duration_ms / frames))

    def _animate_curve(self, surface, player, p0, p1, control, duration_ms, screen_update_fn, frames_override=None):
        """
        Animate along a quadratic Bezier (p0 -> control -> p1). Used for snake slides.
        """
        if duration_ms <= 0:
            self._call_screen_update(screen_update_fn, player, p1[0], p1[1])
            self._draw_token(surface, player, p1[0], p1[1])
            pygame.display.flip()
            return

        fps_target = 60.0
        frame_ms = 1000.0 / fps_target
        frames = frames_override if frames_override else max(1, int(math.ceil(duration_ms / frame_ms)))
        for f in range(frames):
            t = (f + 1) / frames
            # quadratic bezier: B(t) = (1-t)^2 p0 + 2(1-t)t c + t^2 p1
            one_minus_t = 1 - t
            x = one_minus_t * one_minus_t * p0[0] + 2 * one_minus_t * t * control[0] + t * t * p1[0]
            y = one_minus_t * one_minus_t * p0[1] + 2 * one_minus_t * t * control[1] + t * t * p1[1]
            self._call_screen_update(screen_update_fn, player, x, y)
            self._draw_token(surface, player, x, y)
            pygame.display.flip()
            pygame.event.pump()
            pygame.time.delay(int(duration_ms / frames))

    def walk(self, surface, board, player, steps, snakes, ladders, players, screen_update_fn):
        start_cell = getattr(player, "position", 0)
        prev_cell = start_cell

        for step in range(1, steps + 1):

        # ตำแหน่งใหม่แบบไม่รวม bounce
            raw_target = start_cell + step

        # ⭐ NEW RULE: bounce-back ถ้าเกิน 99
            if raw_target > 99:
                overflow = raw_target - 99
                target_cell = 99 - overflow
            else:
                target_cell = raw_target

            start_center = get_cell_center(prev_cell)
            target_center = get_cell_center(target_cell)

        # animate hop
            self._animate_step_hop(surface, player,start_center, target_center,self.step_delay, screen_update_fn,hop_height=12)

            prev_cell = target_cell

    # ⭐ อัปเดตตำแหน่งจริงหลัง animation เสร็จ
        player.position = prev_cell

    def climb_ladder(self, surface, board, player, target, snakes, ladders, players, screen_update_fn):
        """
        Animate climbing a ladder as a smooth sequence of short hops along the
        straight line from the start cell center to the target cell center.
        Keeps the player's color unchanged.
        """
        start_cell = getattr(player, "position", 0)
        if target == start_cell:
            return

        # get centers for start and target cells
        start_pos = get_cell_center(start_cell)
        end_pos = get_cell_center(target)

        # number of sub-steps: at least 4, proportional to cell distance for smoothness
        cell_distance = abs(target - start_cell)
        segments = max(4, cell_distance)

        # duration per segment (shorter than normal walk to look like climbing)
        seg_duration = max(30, int(self.step_delay * 0.6))

        prev_pos = start_pos
        for i in range(1, segments + 1):
            t = i / segments
            # linear interpolation between start and end centers
            nx = self._lerp(start_pos[0], end_pos[0], t)
            ny = self._lerp(start_pos[1], end_pos[1], t)
            # smaller hop height as we ascend (subtle)
            hop_h = int(10 * (1.0 - 0.4 * t))
            self._animate_step_hop(surface, player, prev_pos, (nx, ny), seg_duration, screen_update_fn, hop_height=hop_h)
            prev_pos = (nx, ny)

        # finally set logical position
        player.position = target

    def slide_snake(self, surface, board, player, target, snakes, ladders, players, screen_update_fn):
        """
        Animate sliding down a snake using multiple curved segments that follow
        a swerving path (approximating the snake's body). Slower overall than
        before and preserves player's color.
        """
        start = getattr(player, "position", 0)
        if target == start:
            return

        p0 = get_cell_center(start)
        p1 = get_cell_center(target)

        # total distance (pixel) and cell distance
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        dist = math.hypot(dx, dy)
        cell_distance = abs(target - start)

        # number of segments: proportional to distance/cell distance for smooth curve
        segments = max(6, int(cell_distance * 2))
        # total duration scaled so snake slide is noticeably slower
        total_duration = max(500, int(self.step_delay * 2.5 * max(1, cell_distance)))
        seg_duration = max(40, total_duration // segments)

        # compute a perpendicular vector to the main direction for swerves
        if dist == 0:
            perp = (0.0, 0.0)
        else:
            nx = dx / dist
            ny = dy / dist
            perp = (-ny, nx)

        # amplitude of swerves (clamped)
        amp = min(max(40.0, dist * 0.18), 140.0)

        # number of wiggles along the slide (more cells -> more wiggles)
        wiggles = max(2, cell_distance // 2 + 1)

        # create segment endpoints along the line p0 -> p1 and animate each with a control offset
        def lerp(a, b, t):
            return a + (b - a) * t

        prev_pt = p0
        for i in range(segments):
            a = i / segments
            b = (i + 1) / segments
            seg_start = (lerp(p0[0], p1[0], a), lerp(p0[1], p1[1], a))
            seg_end = (lerp(p0[0], p1[0], b), lerp(p0[1], p1[1], b))
            # control point near the middle of the segment
            mid_t = (a + b) / 2.0
            mid = (lerp(seg_start[0], seg_end[0], 0.5), lerp(seg_start[1], seg_end[1], 0.5))
            # sine-based offset to create swerves; sign alternates with index for natural look
            s = math.sin(2.0 * math.pi * wiggles * mid_t)
            # taper amplitude slightly towards the end so it settles
            taper = 1.0 - (mid_t ** 1.2)
            offset = amp * s * taper
            control = (mid[0] + perp[0] * offset, mid[1] + perp[1] * offset)

            # animate this curved segment
            self._animate_curve(surface, player, seg_start, seg_end, control, seg_duration, screen_update_fn,
                                frames_override=max(6, int(seg_duration / (1000.0 / 60.0))))
            prev_pt = seg_end

        # finally set logical position
        player.position = target
