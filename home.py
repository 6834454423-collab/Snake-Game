import pygame
import sys
from button import Button, create_play_again_button  # expects button.py in workspace

WIDTH, HEIGHT = 640, 360
BG = (30, 30, 30)
TEXT_COLOR = (230, 230, 230)

def clamp(v, a, b):
    return max(a, min(b, v))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Select Players")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 36)
    small = pygame.font.SysFont(None, 20)

    state = "home"    # "home" or "game"
    players = 2

    # Buttons: minus, plus, start, play again (for game state)
    btn_w, btn_h = 44, 36
    minus_btn = Button(rect=(WIDTH//2 - 110, HEIGHT//2 - 10, btn_w, btn_h),
                       text="-", callback=lambda: none())
    plus_btn = Button(rect=(WIDTH//2 + 66, HEIGHT//2 - 10, btn_w, btn_h),
                      text="+", callback=lambda: none())
    start_btn = Button(rect=(WIDTH//2 - 70, HEIGHT//2 + 50, 140, 44),
                       text="Start Game", callback=lambda: none())
    play_again_btn = create_play_again_button(rect=(WIDTH//2 - 70, HEIGHT//2 + 40, 140, 44),
                                              callback=lambda: none(),
                                              text="Play Again")

    # Assign real callbacks that modify outer-scope variables via mutable container
    state_holder = {"state": state, "players": players}

    def none():
        # placeholder so Button can be created before callbacks are defined
        return

    def do_minus():
        state_holder["players"] = clamp(state_holder["players"] - 1, 2, 6)

    def do_plus():
        state_holder["players"] = clamp(state_holder["players"] + 1, 2, 6)

    def do_start():
        state_holder["state"] = "game"

    def do_play_again():
        state_holder["state"] = "home"

    # attach callbacks and fonts
    minus_btn.callback = do_minus
    plus_btn.callback = do_plus
    start_btn.callback = do_start
    play_again_btn.callback = do_play_again

    minus_btn.font = font
    plus_btn.font = font
    start_btn.font = font
    play_again_btn.font = font

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # keyboard controls on home screen
            if state_holder["state"] == "home":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RIGHT, pygame.K_UP, pygame.K_EQUALS, pygame.K_PLUS):
                        state_holder["players"] = clamp(state_holder["players"] + 1, 2, 6)
                    elif event.key in (pygame.K_LEFT, pygame.K_DOWN, pygame.K_MINUS):
                        state_holder["players"] = clamp(state_holder["players"] - 1, 2, 6)
                # mouse wheel to change players
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # wheel up
                        state_holder["players"] = clamp(state_holder["players"] + 1, 2, 6)
                    elif event.button == 5:  # wheel down
                        state_holder["players"] = clamp(state_holder["players"] - 1, 2, 6)

            # delegate events to the buttons relevant for the current state
            if state_holder["state"] == "home":
                minus_btn.handle_event(event)
                plus_btn.handle_event(event)
                start_btn.handle_event(event)
            else:
                play_again_btn.handle_event(event)
                # allow ESC to return to home
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state_holder["state"] = "home"

        # draw
        screen.fill(BG)
        if state_holder["state"] == "home":
            # display player selection
            player_text = font.render(f"Players: {state_holder['players']}", True, TEXT_COLOR)
            screen.blit(player_text, (WIDTH//2 - player_text.get_width()//2, HEIGHT//2 - 100))

            # draw buttons
            minus_btn.draw(screen)
            plus_btn.draw(screen)
            start_btn.draw(screen)
        else:
            # game state: show "Playing..." message and play again button
            title = font.render("Playing...", True, TEXT_COLOR)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
            play_again_btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)


    pygame.quit()
    sys.exit()
