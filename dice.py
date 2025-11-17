import pygame
import random
import time

class Dice:
    def __init__(self, red_path="assets/dice_red", white_path="assets/dice_white"):
        # โหลดภาพลูกเต๋าสีแดง
        self.faces_red = []
        for i in range(1, 7):
            img = pygame.image.load(f"{red_path}/{i}.png").convert_alpha()
            self.faces_red.append(img)

        # โหลดภาพลูกเต๋าสีขาว
        self.faces_white = []
        for i in range(1, 7):
            img = pygame.image.load(f"{white_path}/{i}.png").convert_alpha()
            self.faces_white.append(img)

        # ค่าหน้าลูกเต๋าปัจจุบัน
        self.value1 = 1  # แดง
        self.value2 = 1  # ขาว

        # ระบบหมุน
        self.rolling = False
        self.roll_start_time = 0
        self.roll_duration = 0.6

    def roll(self):
        self.rolling = True
        self.roll_start_time = time.time()

    def update(self):
        if self.rolling:
            # เปลี่ยนภาพเร็วๆ
            self.value1 = random.randint(1, 6)
            self.value2 = random.randint(1, 6)

            # หมุนครบเวลา → จบ
            if time.time() - self.roll_start_time >= self.roll_duration:
                self.rolling = False
                self.value1 = random.randint(1, 6)
                self.value2 = random.randint(1, 6)

    def draw(self, screen, x, y):
        # ลูกเต๋าแดง
        img1 = self.faces_red[self.value1 - 1]
        # ลูกเต๋าฟ้า
        img2 = self.faces_white[self.value2 - 1]

        screen.blit(img1, (x, y))
        screen.blit(img2, (x + 100, y))  # วางห่าง 100px

    def get_total(self):
        return self.value1 + self.value2
