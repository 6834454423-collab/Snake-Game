import pygame
import sys
import settings
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK
from game import Game
from button import Button

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snakes and Ladders")

def show_home(screen):
    """Simple selection UI (2-6 players). Returns chosen count or None if user quits."""
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    small = pygame.font.SysFont(None, 20)
    players = 2

    # buttons
    cx = SCREEN_WIDTH // 2
    cy = SCREEN_HEIGHT // 2
    minus = Button(cx - 110, cy - 10, 44, 36, "-", font)
    plus = Button(cx + 66, cy - 10, 44, 36, "+", font)
    start = Button(cx - 70, cy + 50, 140, 44, "Start Game", font, bg_color=(0,150,0), text_color=WHITE)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if minus.is_clicked(event):
                    players = max(2, players - 1)
                elif plus.is_clicked(event):
                    players = min(6, players + 1)
                elif start.is_clicked(event):
                    return players
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RIGHT, pygame.K_UP, pygame.K_PLUS, pygame.K_EQUALS):
                    players = min(6, players + 1)
                elif event.key in (pygame.K_LEFT, pygame.K_DOWN, pygame.K_MINUS):
                    players = max(2, players - 1)

        screen.fill(WHITE)
        title = font.render("Select number of players (2-6)", True, BLACK)
        screen.blit(title, title.get_rect(center=(cx, cy - 60)))

        cnt = font.render(str(players), True, BLACK)
        screen.blit(cnt, cnt.get_rect(center=(cx, cy)))

        hint = small.render("Use +/- buttons, or mouse. Click Start.", True, (80,80,80))
        screen.blit(hint, hint.get_rect(center=(cx, cy + 120)))

        minus.draw(screen)
        plus.draw(screen)
        start.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    return None

def show_main_menu(screen):
    """Display the main menu. Returns one of: 'play', 'settings', 'quit' or None on quit."""
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont(None, 72)
    font = pygame.font.SysFont(None, 36)

    cx = SCREEN_WIDTH // 2
    cy = SCREEN_HEIGHT // 2

    play = Button(cx - 100, cy - 60, 200, 50, "Play", font, bg_color=(100,149,237), text_color=WHITE)
    settings = Button(cx - 100, cy + 10, 200, 50, "Settings", font)
    quit_btn = Button(cx - 100, cy + 80, 200, 50, "Quit", font, bg_color=(220,20,60), text_color=WHITE)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play.is_clicked(event):
                    return 'play'
                elif settings.is_clicked(event):
                    return 'settings'
                elif quit_btn.is_clicked(event):
                    return 'quit'

        screen.fill(WHITE)
        title = title_font.render("Snakes & Ladders", True, BLACK)
        screen.blit(title, title.get_rect(center=(cx, cy - 160)))

        play.draw(screen)
        settings.draw(screen)
        quit_btn.draw(screen)

        hint = pygame.font.SysFont(None, 18).render("Use mouse to choose an option.", True, (80,80,80))
        screen.blit(hint, hint.get_rect(center=(cx, cy + 150)))

        pygame.display.flip()
        clock.tick(60)


def show_settings(screen):
    """A very small settings screen with a Back button (placeholder)."""
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    cx = SCREEN_WIDTH // 2
    cy = SCREEN_HEIGHT // 2

    back = Button(cx - 70, cy + 140, 140, 44, "Back", font)

    # prepare color swatches from settings
    swatches = settings.BOARD_COLOR_OPTIONS
    # include a special 'christmas' swatch so it looks like the other color tiles
    swatches_ext = list(swatches) + [("christmas", "Christmas")]
    sw_w = 80
    sw_h = 48
    gap = 18
    total_w = len(swatches_ext) * sw_w + (len(swatches_ext) - 1) * gap
    sw_start_x = cx - total_w // 2
    sw_y = cy - 10

    # confirmation UI
    pending = None  # (col, name) waiting for confirmation
    # separate confirm and cancel more for clarity
    confirm_btn = Button(cx - 160, cy + 60, 120, 44, "Confirm", font, bg_color=(0,150,0), text_color=WHITE)
    cancel_btn = Button(cx + 40, cy + 60, 120, 44, "Cancel", font, bg_color=(200,0,0), text_color=WHITE)

    small = pygame.font.SysFont(None, 24)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # if we have a pending selection, check confirm/cancel first
                if pending is not None:
                    if confirm_btn.is_clicked(event):
                        # apply selection and signal to go directly to player selection
                        if pending[0] == "christmas":
                            # enable christmas theme
                            settings.CHRISTMAS_THEME = True
                        else:
                            settings.BOARD_COLOR = pending[0]
                        return 'apply_and_play'
                    elif cancel_btn.is_clicked(event):
                        pending = None
                    # swallow other clicks while pending
                    continue

                # check swatch clicks (including the special christmas swatch)
                for i, (col, name) in enumerate(swatches_ext):
                    r = pygame.Rect(sw_start_x + i * (sw_w + gap), sw_y, sw_w, sw_h)
                    if r.collidepoint((mx, my)):
                        # set pending selection; confirmation will be requested
                        pending = (col, name)
                        break

                if pending is None:
                    # back button
                    if back.is_clicked(event):
                        return 'back'

        screen.fill(WHITE)
        title = font.render("Settings", True, BLACK)
        screen.blit(title, title.get_rect(center=(cx, cy - 120)))

        info = small.render("Choose board color (cells):", True, (90,90,90))
        screen.blit(info, info.get_rect(center=(cx, cy - 60)))

        # draw swatches (including special christmas swatch)
        for i, (col, name) in enumerate(swatches_ext):
            rx = sw_start_x + i * (sw_w + gap)
            r = pygame.Rect(rx, sw_y, sw_w, sw_h)
            if col == "christmas":
                # draw split red/green tile for Christmas
                left = pygame.Rect(rx, sw_y, sw_w // 2, sw_h)
                right = pygame.Rect(rx + sw_w // 2, sw_y, sw_w - sw_w // 2, sw_h)
                pygame.draw.rect(screen, (200,30,60), left)
                pygame.draw.rect(screen, (30,140,60), right)
                # indicate pending or enabled state with border
                if pending is not None and pending[0] == "christmas":
                    pygame.draw.rect(screen, (255, 215, 0), r, 4)
                elif getattr(settings, "CHRISTMAS_THEME", False):
                    pygame.draw.rect(screen, (255, 215, 0), r, 4)
                else:
                    pygame.draw.rect(screen, BLACK, r, 2)
            else:
                pygame.draw.rect(screen, col, r)
                # highlight current selection and pending differently
                if col == settings.BOARD_COLOR:
                    pygame.draw.rect(screen, BLACK, r, 4)
                elif pending is not None and col == pending[0]:
                    pygame.draw.rect(screen, (255, 215, 0), r, 4)
                else:
                    pygame.draw.rect(screen, BLACK, r, 2)

            lbl = small.render(name, True, BLACK)
            screen.blit(lbl, lbl.get_rect(center=(rx + sw_w // 2, sw_y + sw_h + 14)))

        # draw confirmation overlay if needed
        if pending is not None:
            overlay_rect = pygame.Rect(cx - 220, cy - 10, 440, 140)
            pygame.draw.rect(screen, (245,245,245), overlay_rect)
            pygame.draw.rect(screen, BLACK, overlay_rect, 2)
            msg = small.render(f"Apply: {pending[1]}?", True, BLACK)
            screen.blit(msg, msg.get_rect(center=(cx, cy + 10)))
            confirm_btn.draw(screen)
            cancel_btn.draw(screen)

        # (Christmas option is rendered as a swatch tile above)

        back.draw(screen)

        pygame.display.flip()
        clock.tick(60)

def main():
    pygame.mixer.music.load("assets\sound\s_backgroundSong.mp3")  # Make sure this file exists in your folder
    pygame.mixer.music.play(-1)
    running = True
    while running:
        # show main menu first
        menu_choice = show_main_menu(screen)
        if menu_choice is None or menu_choice == 'quit':
            running = False
            break
        if menu_choice == 'settings':
            # show settings until user goes back, quits, or confirms-and-wants-to-play
            res = show_settings(screen)
            if res is None:
                running = False
                break
            if res == 'apply_and_play':
                chosen = show_home(screen)
                if chosen is None:
                    running = False
                    break
            else:
                # user pressed Back -> return to main menu
                continue

        else:
            # menu_choice == 'play' -> proceed to player selection
            chosen = show_home(screen)
            if chosen is None:
                running = False
                break

        # flag object to let Game signal return-to-home
        class Flag: pass
        flag = Flag()
        flag.go_home = False
        def go_home_callback():
            flag.go_home = True

        game = Game(screen, on_go_home=go_home_callback)

        # set chosen players on game and reset as necessary
        game.start_new_game(chosen)

        # game main loop
        clock = pygame.time.Clock()
        while not flag.go_home and running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    game.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    # optional: forward keys to game
                    pass
            
            game.update_logic()


            game.screen_update()
            clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
