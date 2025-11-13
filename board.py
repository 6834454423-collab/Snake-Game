# board.py
import pygame
import math
from settings import ROWS, COLS, CELL_SIZE, BLACK, GREEN, RED, BOARD_OFFSET_X, BOARD_OFFSET_Y


def get_pos(cell):
    """แปลงหมายเลขช่อง (0–100) เป็นพิกัดบนกระดาน"""
    # 0 ถึง 99
    if 0 <= cell <= 99:
        row = cell // 10
        col = cell % 10
        # การสลับคอลัมน์ในแถวเลขคี่ (Boustrophedon)
        if row % 2 == 1:
            col = 9 - col
        # คำนวณพิกัด x และ y
        x = BOARD_OFFSET_X + col * CELL_SIZE
        # การวาดจากล่างขึ้นบน (แถว 0 คือล่างสุด)
        y = BOARD_OFFSET_Y + (ROWS - 1 - row) * CELL_SIZE
        return x, y
        
    # ช่อง FINISH (100)
    elif cell == 100: 
        # ตำแหน่งของช่อง 99 (ใช้คำนวณตำแหน่ง Finish ที่อยู่ข้างๆ)
        last_row = 99 // 10
        last_col = 99 % 10
        if last_row % 2 == 1:
            last_col = 9 - last_col
            
        last_x = BOARD_OFFSET_X + last_col * CELL_SIZE
        last_y = BOARD_OFFSET_Y + (ROWS - 1 - last_row) * CELL_SIZE
        
        # Finish อยู่ทางซ้ายของช่อง 99
        return last_x - CELL_SIZE, last_y
    
    return -1, -1 # ตำแหน่งไม่ถูกต้อง


class Board:
    def __init__(self, font):
        self.font = font

    def draw(self, screen, snakes, ladders):
        screen.fill((220, 220, 220)) # สีพื้นหลัง

        # 🔹 วาดช่อง 0–99
        for row in range(ROWS):
            for col in range(COLS):
                x = BOARD_OFFSET_X + col * CELL_SIZE
                y = BOARD_OFFSET_Y + (ROWS - 1 - row) * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                
                # วาดกรอบช่อง
                pygame.draw.rect(screen, BLACK, rect, 2)

                # คำนวณ cell number (Boustrophedon numbering)
                cell_num = row * 10 + col
                if row % 2 == 1:
                    cell_num = row * 10 + (9 - col)

                # กำหนดข้อความในช่อง
                if cell_num == 0:
                    label = "START"
                elif cell_num == 99:
                    label = "99"
                else:
                    label = str(cell_num)

                text = self.font.render(label, True, BLACK)
                screen.blit(text, (x + 5, y + 5))

        # 🔹 ช่อง FINISH (100)
        finish_x, finish_y = get_pos(100)
        f_rect = pygame.Rect(finish_x, finish_y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, (255,215,0), f_rect) # สีทอง
        pygame.draw.rect(screen, BLACK, f_rect, 3)
        f_txt = self.font.render("FINISH", True, BLACK)
        screen.blit(f_txt, (finish_x + 5, finish_y + 15))

        # 🔹 วาดบันได (ปรับให้ดูมีมิติ/หนาขึ้น)
        for start, end in ladders.items():
            sx, sy = get_pos(start)
            ex, ey = get_pos(end)
            
            # จุดศูนย์กลางของช่อง
            center1 = (sx + CELL_SIZE//2, sy + CELL_SIZE//2)
            center2 = (ex + CELL_SIZE//2, ey + CELL_SIZE//2)

            # วาดเส้นหลักสองเส้นให้ดูเหมือน "เสา" ของบันได
            # คำนวณทิศทางของบันได
            dx_unit = (center2[0] - center1[0])
            dy_unit = (center2[1] - center1[1])
            length = math.hypot(dx_unit, dy_unit)
            if length == 0: continue
                
            # เวกเตอร์ตั้งฉาก (ใช้ในการเยื้องเพื่อวาดเส้นขนาน)
            nx = -dy_unit / length
            ny = dx_unit / length
            
            offset = 5 # ระยะห่างระหว่างเส้น
            
            # เส้นที่ 1
            p1_start = (center1[0] - nx * offset, center1[1] - ny * offset)
            p1_end = (center2[0] - nx * offset, center2[1] - ny * offset)
            pygame.draw.line(screen, (139, 69, 19), p1_start, p1_end, 5) # Brown
            
            # เส้นที่ 2
            p2_start = (center1[0] + nx * offset, center1[1] + ny * offset)
            p2_end = (center2[0] + nx * offset, center2[1] + ny * offset)
            pygame.draw.line(screen, (160, 82, 45), p2_start, p2_end, 5) # Sienna (สีน้ำตาลเข้มขึ้น)
            
            # วาดขอบเพื่อให้ดูชัด
            pygame.draw.line(screen, BLACK, p1_start, p1_end, 1)
            pygame.draw.line(screen, BLACK, p2_start, p2_end, 1)


        # 🔹 วาดงูลักษณะเป็นคลื่น (ใช้โค้ดเดิมของคุณซึ่งดีอยู่แล้ว)
        for start, end in snakes.items():
            sx, sy = get_pos(start)
            ex, ey = get_pos(end)

            x1, y1 = sx + CELL_SIZE//2, sy + CELL_SIZE//2
            x2, y2 = ex + CELL_SIZE//2, ey + CELL_SIZE//2

            num_points = 30
            snake_points = []

            dx = x2 - x1
            dy = y2 - y1
            length = math.hypot(dx, dy)
            if length == 0:
                continue

            # เวกเตอร์ตั้งฉาก (ใช้ในการสร้างคลื่น)
            nx = -dy / length
            ny = dx / length

            for i in range(num_points + 1):
                t = i / num_points
                x = x1 + (dx * t)
                y = y1 + (dy * t)
                # สร้างคลื่น Sine
                wave = math.sin(t * math.pi * 6) * 15 
                x += nx * wave
                y += ny * wave
                snake_points.append((x, y))

            pygame.draw.lines(screen, (200, 0, 0), False, snake_points, 5)
            # วาดหัวงู
            pygame.draw.circle(screen, (255, 50, 50), snake_points[0], 8)
            pygame.draw.circle(screen, (0, 0, 0), snake_points[0], 8, 2)

    # ✅ ฟังก์ชันนี้ใช้ใน animate_move และ animate_jump (จาก player.py)
    def redraw_all(self, screen, snakes, ladders, players):
        self.draw(screen, snakes, ladders)

        for p in players:
            # ✅ แก้ไข: ส่งผ่าน players เข้าไปใน draw เพื่อให้ Player สามารถจัดการการจัดวางได้
            p.draw(screen, players)