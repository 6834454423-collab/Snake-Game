# player.py
import pygame
from settings import PLAYER_COLORS, CELL_SIZE # ✅ เพิ่ม CELL_SIZE
from board import get_pos
import time
import math # ✅ เพิ่มการ import math

# เราไม่สามารถ import game_instance ตรงนี้ได้ เนื่องจากจะเกิด Circular Import
# ข้อมูลที่จำเป็น (snakes, ladders, players) จะถูกส่งผ่านเข้ามาในเมธอดแทน

class Player:
    def __init__(self, pid):
        self.id = pid
        self.position = 0

    def draw(self, screen, all_players_data=None):
        """วาดผู้เล่นที่ตำแหน่งช่อง (self.position) พร้อม Logic จัดวาง"""
        x, y = get_pos(self.position)
        
        # Logic จัดวางผู้เล่นให้ไม่ซ้อนทับกัน (ใช้แค่ถ้ามีมากกว่า 1 คน)
        offset_x, offset_y = 0, 0
        if all_players_data and len(all_players_data) > 1:
            pid = self.id
            offset_x = (pid % 2) * 10 - 5
            offset_y = (pid // 2) * 10 - 5
            
        pygame.draw.circle(screen, PLAYER_COLORS[self.id], 
                           (x + 25 + offset_x, y + 25 + offset_y), 18)
        pygame.draw.circle(screen, (0, 0, 0), 
                           (x + 25 + offset_x, y + 25 + offset_y), 18, 3)

    # ✅ เมธอดช่วยวาดผู้เล่นที่พิกัด X, Y ชั่วคราว (ใช้ตอนเลื่อนงู)
    def _draw_at_pos(self, screen, all_players_data, current_x, current_y):
        """ใช้สำหรับวาดผู้เล่นคนอื่นในตำแหน่งปกติ และวาดผู้เล่นปัจจุบันในพิกัดชั่วคราว"""
        # วาดผู้เล่นคนอื่น (ที่ไม่ได้เลื่อนอยู่)
        for p in all_players_data:
            if p.id != self.id:
                p.draw(screen, all_players_data)

        # Logic จัดวางผู้เล่นคนปัจจุบันในพิกัดชั่วคราว
        offset_x, offset_y = 0, 0
        if all_players_data and len(all_players_data) > 1:
            pid = self.id
            offset_x = (pid % 2) * 10 - 5
            offset_y = (pid // 2) * 10 - 5
            
        pygame.draw.circle(screen, PLAYER_COLORS[self.id], 
                           (current_x + offset_x, current_y + offset_y), 18)
        pygame.draw.circle(screen, (0, 0, 0), 
                           (current_x + offset_x, current_y + offset_y), 18, 3)


    def animate_move(self, screen, board, steps, snakes, ladders, players):
        """เดินทีละช่อง พร้อม redraw ทั้งหมด (ใช้สำหรับเดินปกติ)"""

        for _ in range(steps):
            if self.position < 100:
                self.position += 1
            
            # ✅ Logic การเด้งกลับ (Bounce Back)
            elif self.position > 100:
                 self.position = 100 - (self.position - 100)
            
            # ✅ วาดใหม่ทั้งกระดาน + ผู้เล่นทั้งหมด
            board.redraw_all(
                screen,
                snakes,
                ladders,
                players
            )

            pygame.display.flip()
            pygame.time.delay(150)


    # ✅ เมธอดใหม่: ใช้สำหรับขึ้นบันไดเท่านั้น (เดินทีละช่อง)
    def animate_jump(self, screen, board, target, snakes, ladders, players):
        """กระโดดขึ้นบันได (เดินทีละช่อง)"""

        start = self.position
        direction = 1 if target > start else -1

        while self.position != target:
            self.position += direction

            board.redraw_all(
                screen,
                snakes,
                ladders,
                players
            )

            pygame.display.flip()
            pygame.time.delay(120)

    
    # ✅ เมธอดใหม่: สำหรับการเลื่อนลงตามตัวงู (ใช้พิกัด X, Y)
    def animate_snake_slide(self, screen, board, target, snakes, ladders, players):
        """เลื่อนลงตามเส้นโค้งของงู"""
        start_cell = self.position
        
        sx, sy = get_pos(start_cell) # พิกัดช่องเริ่มต้น
        ex, ey = get_pos(target)     # พิกัดช่องปลายทาง

        # จุดศูนย์กลางของช่อง
        x1, y1 = sx + CELL_SIZE//2, sy + CELL_SIZE//2
        x2, y2 = ex + CELL_SIZE//2, ey + CELL_SIZE//2

        num_points = 50 # จำนวนจุดตลอดเส้นทาง
        
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        if length == 0: 
            self.position = target
            return

        # เวกเตอร์ตั้งฉาก (ใช้ในการสร้างคลื่น)
        nx = -dy / length
        ny = dx / length

        # ลูปเพื่อขยับผู้เล่นไปตามเส้นคลื่น
        for i in range(1, num_points + 1):
            t = i / num_points
            
            # คำนวณตำแหน่งบนเส้นตรง
            x = x1 + (dx * t)
            y = y1 + (dy * t)
            
            # คำนวณส่วนโค้ง (คล้ายกับ logic วาดงูใน board.py)
            wave = math.sin(t * math.pi * 6) * 15 
            x += nx * wave
            y += ny * wave

            # ✅ วาดกระดานใหม่ (เพื่อลบภาพเก่าของกระดานและงู/บันได)
            board.draw(screen, snakes, ladders) 
            
            # ✅ วาดผู้เล่นในตำแหน่ง X, Y ชั่วคราว (ใช้เมธอดช่วย)
            self._draw_at_pos(screen, players, x, y) 
            
            pygame.display.flip()
            pygame.time.delay(10)

        # เมื่ออนิเมชันจบ ให้กำหนดตำแหน่งผู้เล่นใหม่
        self.position = target