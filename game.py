import pygame
from settings import WIDTH, HEIGHT, WHITE, BLACK, BOARD_OFFSET_X, CELL_SIZE, COLS
from board import Board, get_pos
from player import Player
from dice import Dice
from snakes_ladders import SnakeLadderGenerator
from animation import Animation
from utils import draw_text
from button import Button


class Game:
    def __init__(self, screen, on_go_home=None):
        self.screen = screen
        self.font = pygame.font.SysFont("Consolas", 18)
        self.big_font = pygame.font.SysFont("Consolas", 28, bold=True)
        self.board = Board(self.font)
        self.dice = Dice()
        self.anim = Animation()

        self.num_players = 2
        self.players = [Player(i) for i in range(self.num_players)]
        self.turn_index = 0
        self.snakes, self.ladders = SnakeLadderGenerator().generate()

        self.UI_X = BOARD_OFFSET_X + CELL_SIZE * COLS + 40
        self.UI_Y = 120
        self.roll_button = pygame.Rect(self.UI_X, self.UI_Y + 160, 140, 50)

        self.play_again_btn = Button(self.UI_X, self.UI_Y + 160, 140, 50, "Play Again",self.font, bg_color=(50,160,50), text_color=WHITE)
        self.minus_btn = Button(self.UI_X, self.UI_Y + 30, 44, 36, "-", self.font)
        self.plus_btn = Button(self.UI_X + 96, self.UI_Y + 30, 44, 36, "+", self.font)
        self.restart_btn = Button(self.UI_X, self.UI_Y + 80, 140, 44, "Start New Game", self.font)

        self.dice_value = None
        self.winner = None
        self.selecting = False
        self.new_players_count = self.num_players

        self.win_popup = None  # <-- NEW popup holder
        self.on_go_home = on_go_home

    def next_turn(self):
        self.turn_index = (self.turn_index + 1) % len(self.players)

    def screen_update(self, draw_temp=None):
        # ถ้ามี popup ชนะ → วาด popup แล้ว return เลย
        if self.win_popup:
            self.board.draw(self.screen, self.snakes, self.ladders)
            for p in self.players:
                p.draw(self.screen, self.players)
            self.win_popup.draw()
            pygame.display.flip()
            return

        self.screen.fill(WHITE)
        self.board.draw(self.screen, self.snakes, self.ladders)

        # วาดผู้เล่น
        for p in self.players:
            if draw_temp and draw_temp[0] is p:
                continue
            p.draw(self.screen, self.players)

        if draw_temp:
            _, tx, ty = draw_temp
            pygame.draw.circle(self.screen, (255,0,0), (int(tx), int(ty)), 16)
            pygame.draw.circle(self.screen, (0,0,0), (int(tx), int(ty)), 16, 2)

        # ROLL DICE button
        if not self.winner and not self.selecting:
            pygame.draw.rect(self.screen, (0,150,0), self.roll_button)
            pygame.draw.rect(self.screen, BLACK, self.roll_button, 2)
            draw_text(self.screen, "ROLL DICE", (self.roll_button.x + 20, self.roll_button.y + 14), self.font, WHITE)

        elif self.winner and not self.selecting:
            self.play_again_btn.draw(self.screen)

        # Selecting mode
        if self.selecting:
            draw_text(self.screen, "Choose players (2-6):", (self.UI_X, self.UI_Y), self.font)
            cnt_text = self.big_font.render(str(self.new_players_count), True, BLACK)
            self.screen.blit(cnt_text, cnt_text.get_rect(center=(self.UI_X + 70, self.UI_Y + 52)))
            self.minus_btn.draw(self.screen)
            self.plus_btn.draw(self.screen)
            self.restart_btn.draw(self.screen)

        draw_text(self.screen, f"Player {self.turn_index + 1}'s turn", (self.UI_X, self.UI_Y - 40), self.font)
        if self.dice_value:
            draw_text(self.screen, f"Dice: {self.dice_value}", (self.UI_X, self.UI_Y + 40), self.big_font)

        # Dice animation
        self.dice.update()
        self.dice.draw(self.screen, self.UI_X, self.UI_Y + 220)

        pygame.display.flip()

    def handle_click(self, pos):

        # ถ้ามี POPUP ชนะ → ให้ส่ง event ไปที่ popup
        if self.win_popup:
            evt = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1})
            self.win_popup.handle_event(evt)
            return

        if self.selecting:
            evt = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1})
            if self.minus_btn.is_clicked(evt):
                self.new_players_count = max(2, self.new_players_count - 1)
                return
            if self.plus_btn.is_clicked(evt):
                self.new_players_count = min(6, self.new_players_count + 1)
                return
            if self.restart_btn.is_clicked(evt):
                self.start_new_game(self.new_players_count)
                return
            return

        if self.winner:
            evt = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1})
            if self.play_again_btn.is_clicked(evt):
                if callable(self.on_go_home):
                    self.on_go_home()
                else:
                    self.selecting = True
            return

        if self.roll_button.collidepoint(pos):
            self.roll_action()

    def roll_action(self):
        self.dice.roll()
        self.dice_value = 0

    def update_logic(self):
        if self.dice_value is not None and not self.dice.rolling: 
            total = self.dice.get_total()
            self.dice_value = None

            current = self.players[self.turn_index]
            start_pos = current.position
            intended = start_pos + total

        # --------------------------
        #   BOUNCE BACK RULE
        # --------------------------
            if intended > 99:
                overflow = intended - 99
                final_pos = 99 - overflow
            else:
                final_pos = intended

        # เดินไปตำแหน่งใหม่แบบอนิเมชัน
            self.anim.walk(self.screen, self.board, current,final_pos - start_pos,self.snakes, self.ladders,self.players, self.screen_update)

            current.position = final_pos

        # เช็คงู/บันได
            pos = current.position
            if pos in self.ladders:
                target = self.ladders[pos]
                self.anim.climb_ladder(self.screen, self.board, current, target,self.snakes, self.ladders,self.players, self.screen_update)

            elif pos in self.snakes:
                target = self.snakes[pos]
                self.anim.slide_snake(self.screen, self.board, current, target,self.snakes, self.ladders,self.players, self.screen_update)

        # ชนะ
            if current.position == 99:
                self.winner = current
                self.win_popup = WinPopup(self.screen, f"Player {current.id + 1}", home_callback=self.on_go_home)

            else:
                self.next_turn()


    def start_new_game(self, num_players):
        self.num_players = num_players
        self.players = [Player(i) for i in range(self.num_players)]
        self.turn_index = 0
        self.snakes, self.ladders = SnakeLadderGenerator().generate()
        self.dice_value = None
        self.winner = None
        self.win_popup = None
        self.selecting = False
        self.new_players_count = self.num_players



# ---------------------------------------------------------
# WIN POPUP WITH BUTTON + SOUND
# ---------------------------------------------------------
class WinPopup:
    def __init__(self, screen, winner_name="Player", home_callback=None):
        self.screen = screen
        self.winner = winner_name
        self.home_callback = home_callback

        # Sound
        try:
            self.sound = pygame.mixer.Sound("assets/sound/s_congratulations.mp3")
            self.sound.play()
        except:
            print("Win sound not found")

        # Fonts
        self.font_big = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 28)

        self.width = 500
        self.height = 260
        self.rect = pygame.Rect(
            (1280 - self.width) // 2,
            (720 - self.height) // 2,
            self.width,
            self.height
        )

        self.btn_rect = pygame.Rect(
            self.rect.centerx - 100,
            self.rect.y + self.height - 70,
            200, 50
        )

    def draw(self):
        pygame.draw.rect(self.screen, (255, 255, 255), self.rect, border_radius=20)
        pygame.draw.rect(self.screen, (0, 0, 0), self.rect, 4, border_radius=20)

        title = self.font_big.render("🎉 Congratulations 🎉", True, (0, 150, 0))
        winner_text = self.font_big.render(self.winner, True, (200, 0, 0))

        self.screen.blit(title, (self.rect.centerx - title.get_width() // 2,
                                 self.rect.y + 25))
        self.screen.blit(winner_text, (self.rect.centerx - winner_text.get_width() // 2,
                                       self.rect.y + 100))

        pygame.draw.rect(self.screen, (240, 240, 240), self.btn_rect, border_radius=12)
        pygame.draw.rect(self.screen, (0, 0, 0), self.btn_rect, 3, border_radius=12)

        btn_text = self.font_small.render("Home", True, (0, 0, 0))
        self.screen.blit(btn_text, (
            self.btn_rect.centerx - btn_text.get_width() // 2,
            self.btn_rect.centery - btn_text.get_height() // 2
        ))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_rect.collidepoint(event.pos):
                if self.home_callback:
                    self.home_callback()
