import pygame
import random
import settings
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
        # roll cooldown (milliseconds) and last roll timestamp
        self.roll_cooldown_ms = 2200
        self._last_roll_time = 0
        # snow particles for Christmas overlay (initialized on demand)
        self.snow_particles = None
        self._snow_last_time = pygame.time.get_ticks()
        
        self.back_btn = Button( self.UI_X,             # X position (ปรับได้)
        self.UI_Y+550,     # Y position (ขยับไม่ให้ทับปุ่มอื่น)
        140,                   # width
        44,                    # height
        "Back",                # text
        self.font,
        bg_color=(50,50,50),  # สีแดงเข้ม
        text_color=WHITE )

       #rint("POPUP on start:", self.win_popup)

        
        try:
            self.bg_image = pygame.image.load("assets/background/game_background.jpg").convert()
            self.bg_image = pygame.transform.scale(self.bg_image, screen.get_size())
            print("BACKGROUND LOADED SUCCESS!")
        except Exception:
            print("BACKGROUND LOAD FAILED:", e)
            self.bg_image = None
            

    def next_turn(self):
        self.turn_index = (self.turn_index + 1) % len(self.players)

    def screen_update(self, draw_temp=None):
        # ถ้ามี popup ชนะ → วาด popup แล้ว return เลย
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(WHITE)
        
        if not self.win_popup:
            self.back_btn.draw(self.screen)
            
        if self.win_popup:
            self.win_popup.draw()
            pygame.display.flip()
            return
        
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

        # ROLL DICE button (shows disabled state + cooldown)
        if not self.winner and not self.selecting:
            now = pygame.time.get_ticks()
            cooldown_left = max(0, self.roll_cooldown_ms - (now - getattr(self, "_last_roll_time", 0)))
            # cannot roll while dice animating or cooldown not finished
            can_roll = (cooldown_left == 0) and (not self.dice.rolling)
            if can_roll:
                btn_color = (0,150,0)
            else:
                btn_color = (160,160,160)

            pygame.draw.rect(self.screen, btn_color, self.roll_button)
            pygame.draw.rect(self.screen, BLACK, self.roll_button, 2)
            if self.dice.rolling:
                draw_text(self.screen, "Rolling...", (self.roll_button.x +12 , self.roll_button.y +20 ), self.font, WHITE)
            elif not can_roll and cooldown_left > 0:
                draw_text(self.screen, f"Wait {cooldown_left/1000:.1f}s", (self.roll_button.x + 8, self.roll_button.y + 14), self.font, WHITE)
            else:
                draw_text(self.screen, "ROLL DICE", (self.roll_button.x + 20, self.roll_button.y + 20), self.font, WHITE)

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
        bold_font = pygame.font.SysFont("Consolas", 18, bold=True)
        draw_text(self.screen, f"Player {self.turn_index + 1}'s turn", (self.UI_X, self.UI_Y+100) ,bold_font,color=(255,255,255))
        if self.dice_value:
            draw_text(self.screen, f"Dice: {self.dice_value}", (self.UI_X, self.UI_Y +40 ), self.big_font)

        # Dice animation
        self.dice.update()
        self.dice.draw(self.screen, self.UI_X, self.UI_Y + 220)

        # Christmas snow overlay (top of screen) - initialize on demand when theme enabled
        if getattr(settings, "CHRISTMAS_THEME", False):
            self._ensure_snow()
            now = pygame.time.get_ticks()
            dt = now - getattr(self, "_snow_last_time", now)
            self._snow_last_time = now
            self._update_snow(dt)
            self._draw_snow()

        pygame.display.flip()

    def _ensure_snow(self):
        if self.snow_particles is None:
            # create a small field of snowflakes
            sw, sh = self.screen.get_size()
            count = max(24, sw // 30)
            import random
            self.snow_particles = []
            for i in range(count):
                x = random.uniform(0, sw)
                y = random.uniform(0, sh)
                vy = random.uniform(20.0, 80.0)  # pixels per second
                vx = random.uniform(-10.0, 10.0)
                size = random.uniform(1.5, 4.0)
                self.snow_particles.append({"x": x, "y": y, "vx": vx, "vy": vy, "size": size})

    def _update_snow(self, dt_ms):
        if not self.snow_particles:
            return
        sw, sh = self.screen.get_size()
        dt = dt_ms / 1000.0
        for p in self.snow_particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            # tiny horizontal sway
            p["vx"] += (0.5 - random.random()) * 5.0 * dt
            if p["y"] > sh + 8:
                # respawn at top
                p["y"] = -4
                p["x"] = random.uniform(0, sw)
                p["vy"] = random.uniform(20.0, 80.0)

    def _draw_snow(self):
        if not self.snow_particles:
            return
        # draw simple white circles with low alpha
        for p in self.snow_particles:
            s = int(max(1, round(p["size"])))
            surf = pygame.Surface((s, s), flags=pygame.SRCALPHA)
            surf.fill((255,255,255,180))
            self.screen.blit(surf, (int(p["x"]), int(p["y"])))

    def handle_click(self, pos):
        evt = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1})
        if self.back_btn.is_clicked(evt):
            if callable(self.on_go_home):
                self.on_go_home()
            return
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
            # only allow roll if not in cooldown and dice not already rolling
            now = pygame.time.get_ticks()
            can_roll = (now - getattr(self, "_last_roll_time", 0)) >= getattr(self, "roll_cooldown_ms", 0)
            if can_roll and not self.dice.rolling and not self.winner and not self.selecting:
                self.roll_action()
            else:
                # ignore click while on cooldown or while dice animating
                pass

    def roll_action(self):
        self.dice.roll()
        self.dice_value = 0
        # mark last roll time for cooldown
        self._last_roll_time = pygame.time.get_ticks()

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
            # Pass the original dice `total` (positive steps) so Animation.walk
            # can internally handle overshoot/bounce per-step and animate it.
            self.anim.walk(self.screen, self.board, current, total, self.snakes, self.ladders, self.players, self.screen_update)

            # Ensure logical position matches the resolved final position after animation
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
                # create popup with callbacks wired to game so it can clear popup and
                # either go home or enter selecting mode (play again)
                self.win_popup = WinPopup(self.screen, f"Player {current.id + 1}", home_callback=self._popup_home, play_again_callback=self._popup_play_again)

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

    def _popup_home(self):
        # clear popup then call external home callback if present
        self.win_popup = None
        if callable(self.on_go_home):
            self.on_go_home()

    def _popup_play_again(self):
        # clear popup and enter selecting mode to choose number of players
        self.win_popup = None
        self.selecting = True



# ---------------------------------------------------------
# WIN POPUP WITH BUTTON + SOUND
# ---------------------------------------------------------
class WinPopup:
    def __init__(self, screen, winner_name="Player", home_callback=None, play_again_callback=None):
        self.screen = screen
        self.winner = winner_name
        self.home_callback = home_callback
        self.play_again_callback = play_again_callback

        # Sound
        try:
            self.sound = pygame.mixer.Sound("assets/sound/s_congratulations.mp3")
            self.sound.play()
            self.bg_popup = pygame.image.load("assets/background/image_background1.png").convert()
            self.bg_popup = pygame.transform.scale(self.bg_popup, screen.get_size())
        except Exception:
            # don't spam the console if missing
            self.bg_popup = None
            pass

        # Fonts
        self.font_big = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 28)

        # center popup based on current screen size (not hardcoded)
        sw, sh = self.screen.get_size()
        self.width = min(600, sw - 120)
        self.height = min(300, sh - 120)
        self.rect = pygame.Rect(
            (sw - self.width) // 2,
            (sh - self.height) // 2,
            self.width,
            self.height
        )

        # two buttons: Play Again (left) and Home (right)
        btn_w = 180
        btn_h = 50
        gap = 24
        total_w = btn_w * 2 + gap
        left_x = self.rect.centerx - total_w // 2
        self.play_btn_rect = pygame.Rect(left_x, self.rect.y + self.height - 80, btn_w, btn_h)
        self.home_btn_rect = pygame.Rect(left_x + btn_w + gap, self.rect.y + self.height - 80, btn_w, btn_h)

        # confetti particles: lightweight particle list
        self._create_confetti()
        # timing for particle updates
        self._last_time = pygame.time.get_ticks()

    def _create_confetti(self, count=48):
        self.particles = []
        # choose palette based on settings (Christmas theme uses red/green/gold)
        if getattr(settings, "CHRISTMAS_THEME", False):
            palette = getattr(settings, "CHRISTMAS_PALETTE", [(220,20,60),(34,139,34),(255,215,0)])
        else:
            palette = [
                (235, 59, 90),  # pink/red
                (250, 130, 49), # orange
                (32, 191, 107), # green
                (69, 170, 242), # blue
                (155, 89, 182), # purple
                (245, 230, 89), # yellow
            ]
        for i in range(count):
            px = self.rect.centerx + random.uniform(-self.width * 0.4, self.width * 0.4)
            py = self.rect.y + random.uniform(10, 40)
            vx = random.uniform(-0.8, 0.8)
            vy = random.uniform(-3.0, -1.0)
            size = random.randint(4, 10)
            life = random.uniform(800, 1600)  # milliseconds
            color = random.choice(palette)
            self.particles.append({
                "x": px,
                "y": py,
                "vx": vx,
                "vy": vy,
                "size": size,
                "life": life,
                "age": 0,
                "color": color,
            })

    def draw(self):
        if hasattr(self, "bg_popup") and self.bg_popup:
             self.screen.blit(self.bg_popup, (0, 0))
        else:
        # fallback background (ถ้าไม่มีไฟล์ภาพ)
            self.screen.fill((20, 20, 20))
        # dim the game behind the popup
        overlay = pygame.Surface(self.screen.get_size(), flags=pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        pygame.draw.rect(self.screen, (255, 255, 255), self.rect, border_radius=16)
        pygame.draw.rect(self.screen, (0, 0, 0), self.rect, 3, border_radius=16)

        title = self.font_big.render(" Congratulations ", True, (0, 150, 0))
        winner_text = self.font_big.render(self.winner, True, (200, 0, 0))

        self.screen.blit(title, (self.rect.centerx - title.get_width() // 2,
                                 self.rect.y + 28))
        self.screen.blit(winner_text, (self.rect.centerx - winner_text.get_width() // 2,
                                       self.rect.y + 100))

        # draw Play Again button
        pygame.draw.rect(self.screen, (0, 150, 0), self.play_btn_rect, border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), self.play_btn_rect, 2, border_radius=10)
        play_text = self.font_small.render("Play Again", True, (255, 255, 255))
        self.screen.blit(play_text, (self.play_btn_rect.centerx - play_text.get_width() // 2,
                                     self.play_btn_rect.centery - play_text.get_height() // 2))

        # draw Home button
        pygame.draw.rect(self.screen, (240, 240, 240), self.home_btn_rect, border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), self.home_btn_rect, 2, border_radius=10)
        home_text = self.font_small.render("Home", True, (0, 0, 0))
        self.screen.blit(home_text, (self.home_btn_rect.centerx - home_text.get_width() // 2,
                                     self.home_btn_rect.centery - home_text.get_height() // 2))

        # update and draw confetti particles
        now = pygame.time.get_ticks()
        dt = now - getattr(self, "_last_time", now)
        self._last_time = now
        if hasattr(self, "particles") and self.particles:
            # gravity and damping constants (tuned for pleasant look)
            gravity = 0.0045  # pixels per ms^2
            damp = 0.995
            for p in list(self.particles):
                p["age"] += dt
                # integrate velocity
                p["vy"] += gravity * dt
                p["vx"] *= damp
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt

                alpha = max(0, 255 * (1.0 - p["age"] / p["life"]))
                if alpha <= 0:
                    try:
                        self.particles.remove(p)
                    except ValueError:
                        pass
                    continue

                # draw small rotated rectangle as confetti using an alpha surface
                s = pygame.Surface((p["size"], p["size"]), flags=pygame.SRCALPHA)
                col = p["color"] + (int(alpha),)
                s.fill(col)
                # center draw
                self.screen.blit(s, (int(p["x"] - p["size"] // 2), int(p["y"] - p["size"] // 2)))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # play again clicked
            if self.play_btn_rect.collidepoint(event.pos):
                if callable(self.play_again_callback):
                    self.play_again_callback()
                return
            # home clicked
            if self.home_btn_rect.collidepoint(event.pos):
                if callable(self.home_callback):
                    self.home_callback()
                return
