# main.py
import pygame
import sys
from settings import WIDTH, HEIGHT, WHITE, BLACK, BOARD_OFFSET_X, CELL_SIZE, COLS
from board import Board
from player import Player
from dice import Dice
from snakes_ladders import SnakeLadderGenerator

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🐍 Snakes and Ladders - Pixel Edition 🪜")

font = pygame.font.SysFont("Consolas", 20)
big_font = pygame.font.SysFont("Consolas", 36, bold=True)

# ✅ ให้ไฟล์อื่นเรียกใช้งาน board.redraw_all()
game_instance = None


class Game:
    def __init__(self):
        global game_instance
        game_instance = self      # ✅ บอกว่า instance นี้คือของเกมจริง

        self.board = Board(font)
        self.dice = Dice()
        self.players = [Player(i) for i in range(4)]
        self.turn_index = 0

        self.generator = SnakeLadderGenerator()
        self.snakes, self.ladders = self.generator.generate()

        self.dice_result = None
        self.winner = None

        # 🔹 พื้นที่ UI ด้านขวา
        self.UI_AREA_X = BOARD_OFFSET_X + (CELL_SIZE * COLS) + 300
        self.UI_AREA_Y = HEIGHT // 2 - 100

        # 🔹 ปุ่ม
        self.roll_button = pygame.Rect(self.UI_AREA_X, self.UI_AREA_Y + 200, 150, 60)
        self.play_again_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 60)

    def reset(self):
        self.__init__()

    def handle_roll(self):
        if self.winner:
            return

        dice1, dice2 = self.dice.roll()
        self.dice_result = (dice1, dice2)
        steps = dice1 + dice2

        current_player = self.players[self.turn_index]

        # ✅ อนิเมชันเดินปกติ (รวม Logic เด้งกลับแล้ว)
        current_player.animate_move(
            screen, self.board, steps, 
            self.snakes, self.ladders, self.players
        )

        pos = current_player.position

        # 🛑 การเช็คชัยชนะ
        if pos == 100:
            self.winner = current_player
            return 

        # ✅ อนิเมชันบันได (ใช้ animate_jump)
        if pos in self.ladders:
            target = self.ladders[pos]
            current_player.animate_jump(
                screen, self.board, target, 
                self.snakes, self.ladders, self.players
            )

        # ✅ อนิเมชันงู (เปลี่ยนมาใช้ animate_snake_slide เพื่อเลื่อนตามเส้นโค้ง)
        elif pos in self.snakes:
            target = self.snakes[pos]
            current_player.animate_snake_slide( # ⬅️ แก้ไขตรงนี้
                screen, self.board, target, 
                self.snakes, self.ladders, self.players
            )

        # ✅ เปลี่ยนเทิร์น 
        self.turn_index = (self.turn_index + 1) % len(self.players)

    def draw_ui(self):
        if not self.winner:
            # ปุ่มทอยลูกเต๋า
            pygame.draw.rect(screen, (0, 180, 0), self.roll_button)
            pygame.draw.rect(screen, BLACK, self.roll_button, 3)
            txt = font.render("ROLL DICE", True, WHITE)
            screen.blit(txt, (self.roll_button.x + 20, self.roll_button.y + 15))

            # ชื่อผู้เล่น
            turn_text = font.render(f"Player {self.turn_index + 1}'s Turn", True, BLACK)
            screen.blit(turn_text, (self.UI_AREA_X, self.UI_AREA_Y - 40))

            # ผลลูกเต๋า
            if self.dice_result:
                dice_sum = sum(self.dice_result)
                dtext = big_font.render(
                    f"{self.dice_result[0]} + {self.dice_result[1]} = {dice_sum}",
                    True, BLACK
                )
                screen.blit(dtext, (self.UI_AREA_X, self.UI_AREA_Y + 120))

        else:
            # ผู้ชนะ
            win_text = big_font.render(f"🎉 Player {self.winner.id + 1} Wins! 🎉",
                                             True, (255, 100, 0))
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 60))

            # ปุ่มเล่นอีกครั้ง
            pygame.draw.rect(screen, (0, 120, 255), self.play_again_button)
            pygame.draw.rect(screen, BLACK, self.play_again_button, 4)
            again = font.render("PLAY AGAIN", True, WHITE)
            screen.blit(again, (self.play_again_button.x + 45, self.play_again_button.y + 20))

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            screen.fill(WHITE)

            # วาดกระดาน
            self.board.draw(screen, self.snakes, self.ladders)

            # วาดผู้เล่น
            for p in self.players:
                # ⚠️ ใน player.py เราแก้ไข p.draw ให้รับ players ด้วย
                p.draw(screen, self.players) 

            # วาด UI
            self.draw_ui()

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.winner and self.roll_button.collidepoint(event.pos):
                        self.handle_roll()

                    elif self.winner and self.play_again_button.collidepoint(event.pos):
                        self.reset()

            clock.tick(30)


if __name__ == "__main__":
    game = Game()
    game.run()