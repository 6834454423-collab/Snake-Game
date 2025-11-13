import pygame
import sys
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

        hint = small.render("Use ←/→, +/- buttons, or mouse. Click Start.", True, (80,80,80))
        screen.blit(hint, hint.get_rect(center=(cx, cy + 90)))

        minus.draw(screen)
        plus.draw(screen)
        start.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    return None

def main():
    running = True
    while running:
        # show home screen and get selection
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

            game.screen_update()
            clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
