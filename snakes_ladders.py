# snakes_ladders.py
import random

class SnakeLadderGenerator:
    def __init__(self, num_snakes=5, num_ladders=5):
        self.num_snakes = num_snakes
        self.num_ladders = num_ladders

    def generate(self):
        snakes = {}
        ladders = {}
        used = set([0, 100]) # 🛑 START (0) และ FINISH (100) ห้ามใช้

        # 🔹 สร้างบันได
        count = 0
        while count < self.num_ladders:
            start = random.randint(2, 80)
            end = start + random.randint(10, 18)
            
            # ✅ ตรวจสอบเงื่อนไขการสร้างบันได
            if end >= 99 or start in used or end in used:
                continue
                
            ladders[start] = end
            used.add(start)
            used.add(end) # ✅ เพิ่มช่องปลายทางของบันไดไม่ให้ทับซ้อนกับช่องอื่น
            count += 1

        # 🔹 สร้างงู
        count = 0
        while count < self.num_snakes:
            start = random.randint(15, 95)
            end = start - random.randint(8, 20)
            
            # ✅ ตรวจสอบเงื่อนไขการสร้างงู
            if end <= 1 or start in used or end in used:
                continue
                
            snakes[start] = end
            used.add(start)
            used.add(end) # ✅ เพิ่มช่องปลายทางของงูไม่ให้ทับซ้อนกับช่องอื่น
            count += 1

        return snakes, ladders