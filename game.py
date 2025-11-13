# game.py
import pygame
from settings import WIDTH, HEIGHT, WHITE, BLACK, BOARD_OFFSET_X, CELL_SIZE, COLS
from board import Board, get_pos
from player import Player
from dice import Dice
from snakes_ladders import SnakeLadderGenerator
from animation import Animation
from utils import draw_text
from button import Button  # added

class Game:
    def __init__(self, screen, on_go_home=None):
        self.screen = screen
        self.font = pygame.font.SysFont("Consolas", 18)
        self.big_font = pygame.font.SysFont("Consolas", 28, bold=True)
        self.board = Board(self.font)
        self.dice = Dice()
        self.anim = Animation()

        # players (ใช้ 2 players เป็น default) — ปรับได้ตามต้องการ
        self.num_players = 2
        self.players = [Player(i) for i in range(self.num_players)]
        self.turn_index = 0
        self.snakes, self.ladders = SnakeLadderGenerator().generate()

        # UI area (ขวาของกระดาน) — roll button area (kept as rect for legacy drawing)
        self.UI_X = BOARD_OFFSET_X + CELL_SIZE * COLS + 40
        self.UI_Y = 120
        self.roll_button = pygame.Rect(self.UI_X, self.UI_Y + 160, 140, 50)

        # Buttons (pygame Button helper)
        self.play_again_btn = Button(self.UI_X, self.UI_Y + 160, 140, 50, "Play Again", self.font, bg_color=(50,160,50), text_color=WHITE)
        self.minus_btn = Button(self.UI_X, self.UI_Y + 30, 44, 36, "-", self.font)
        self.plus_btn = Button(self.UI_X + 96, self.UI_Y + 30, 44, 36, "+", self.font)
        self.restart_btn = Button(self.UI_X, self.UI_Y + 80, 140, 44, "Start New Game", self.font)

        self.dice_value = None
        self.winner = None

        # selection state for restarting / choosing players
        self.selecting = False
        self.new_players_count = self.num_players

        # callback to go back to home screen
        self.on_go_home = on_go_home

    def next_turn(self):
        self.turn_index = (self.turn_index + 1) % len(self.players)

    def screen_update(self, draw_temp=None):
        """
        ฟังก์ชันให้เรียกเพื่อวาดหน้าจอทั้งหมด
        ถ้า draw_temp ถูกส่งมาเป็น (player_obj, x, y) จะวาด player ชั่วคราวที่พิกัดนั้น
        """
        self.screen.fill(WHITE)
        self.board.draw(self.screen, self.snakes, self.ladders)
        # วาดผู้เล่น (ยกเว้นตัวที่กำลังถูกวาดชั่วคราว)
        for p in self.players:
            if draw_temp and draw_temp[0] is p:
                continue
            p.draw(self.screen, self.players)

        # วาด temp player ถ้ามี
        if draw_temp:
            _, tx, ty = draw_temp
            pygame.draw.circle(self.screen, (0,0,0), (0,0), 0)  # noop to avoid flake
            player_temp = draw_temp[0]
            pygame.draw.circle(self.screen, (255,0,0), (int(tx), int(ty)), 16)  # simple color (will be drawn over)
            # better: draw player color
            pygame.draw.circle(self.screen, (0,0,0), (int(tx), int(ty)), 16, 2)

        # UI
        if not self.winner and not self.selecting:
            # draw roll button (legacy styling)
            pygame.draw.rect(self.screen, (0,150,0), self.roll_button)
            pygame.draw.rect(self.screen, BLACK, self.roll_button, 2)
            draw_text(self.screen, "ROLL DICE", (self.roll_button.x + 20, self.roll_button.y + 14), self.font, WHITE)
        elif self.winner and not self.selecting:
            # show Play Again button in the same place as roll
            self.play_again_btn.draw(self.screen)

        # If selecting new game / players, draw selection UI (replaces roll area)
        if self.selecting:
            draw_text(self.screen, "Choose players (2-6):", (self.UI_X, self.UI_Y), self.font)
            # current count
            cnt_text = self.big_font.render(str(self.new_players_count), True, BLACK)
            self.screen.blit(cnt_text, cnt_text.get_rect(center=(self.UI_X + 70, self.UI_Y + 52)))
            # draw minus / plus / start buttons
            self.minus_btn.draw(self.screen)
            self.plus_btn.draw(self.screen)
            self.restart_btn.draw(self.screen)

        # status
        draw_text(self.screen, f"Player {self.turn_index + 1}'s turn", (self.UI_X, self.UI_Y - 40), self.font)
        if self.dice_value:
            draw_text(self.screen, f"Dice: {self.dice_value}", (self.UI_X, self.UI_Y + 40), self.big_font)

        if self.winner:
            draw_text(self.screen, f"Player {self.winner.id + 1} wins!", (self.UI_X, self.UI_Y + 100), self.big_font)

        pygame.display.flip()

    def handle_click(self, pos):
        # If currently selecting players for a new game, route clicks to those buttons
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

        # Normal gameplay handling
        if self.winner:
            # If game finished, clicking Play Again should go back to the home screen
            evt = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1})
            if self.play_again_btn.is_clicked(evt):
                if callable(self.on_go_home):
                    # notify caller (main.py) to show home screen / selection
                    self.on_go_home()
                else:
                    # fallback: open the in-game selection UI
                    self.selecting = True
            return

        # roll button as before
        if self.roll_button.collidepoint(pos):
            self.roll_action()

    def roll_action(self):
        current = self.players[self.turn_index]
        val = self.dice.roll()
        self.dice_value = val

        # animate walking
        self.anim.walk(self.screen, self.board, current, val, self.snakes, self.ladders, self.players, self.screen_update)

        # after walking check ladders / snakes
        pos = current.position
        if pos in self.ladders:
            target = self.ladders[pos]
            self.anim.climb_ladder(self.screen, self.board, current, target, self.snakes, self.ladders, self.players, self.screen_update)
        elif pos in self.snakes:
            target = self.snakes[pos]
            self.anim.slide_snake(self.screen, self.board, current, target, self.snakes, self.ladders, self.players, self.screen_update)

        # check win
        if current.position == 100:
            self.winner = current
        else:
            self.next_turn()
            # clear dice value for next player (optional)
            # self.dice_value = None

    def start_new_game(self, num_players):
        """Reset game state with chosen number of players and return to play."""
        self.num_players = num_players
        self.players = [Player(i) for i in range(self.num_players)]
        self.turn_index = 0
        self.snakes, self.ladders = SnakeLadderGenerator().generate()
        self.dice_value = None
        self.winner = None
        self.selecting = False
        self.new_players_count = self.num_players
