# main.py
import pygame
import sys
import random

from settings import WIDTH, HEIGHT, WHITE, BLACK
from board import draw_board, draw_snakes_ladders
from players import draw_players
from dice import roll_dice
from snakes_ladders import random_snakes_ladders

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT + 200))  # เพิ่มพื้นที่ด้านล่าง
pygame.display.set_caption("Snakes and Ladders")

font = pygame.font.SysFont("Consolas", 28)
dice_font = pygame.font.SysFont("Consolas", 48)
win_font = pygame.font.SysFont("Consolas", 64, bold=True)

def start_new_game():
    global players, turn_order, current_turn_idx, snakes, ladders, winner, dice_result
    num_players = 4
    players = [0] * num_players
    turn_order = list(range(num_players))
    random.shuffle(turn_order)
    current_turn_idx = 0
    snakes, ladders = random_snakes_ladders()
    winner = None
    dice_result = None

start_new_game()

roll_button_rect = pygame.Rect(WIDTH - 250, HEIGHT + 40, 220, 70)
play_again_rect = pygame.Rect(WIDTH//2 - 125, HEIGHT//2 + 60, 250, 70)

running = True
dice_result = None

while running:
    draw_board(screen, font)
    draw_snakes_ladders(screen, snakes, ladders)
    draw_players(screen, players)

    if not winner:
        text = font.render(f"Player {turn_order[current_turn_idx]+1}'s turn", True, BLACK)
        screen.blit(text, (20, HEIGHT + 20))

        pygame.draw.rect(screen, (0, 200, 0), roll_button_rect)
        pygame.draw.rect(screen, BLACK, roll_button_rect, 4)
        btn_text = font.render("ROLL DICE", True, WHITE)
        screen.blit(btn_text, (roll_button_rect.x + 25, roll_button_rect.y + 20))

        if dice_result:
            dice_text = dice_font.render(f"{dice_result[0]} + {dice_result[1]} = {sum(dice_result)}", True, BLACK)
            screen.blit(dice_text, (WIDTH//2 - 80, HEIGHT + 40))
    else:
        win_text = win_font.render(f"Congratulations Player {winner+1}!", True, (255, 100, 0))
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 50))

        pygame.draw.rect(screen, (0, 100, 255), play_again_rect)
        pygame.draw.rect(screen, BLACK, play_again_rect, 4)
        again_text = font.render("PLAY AGAIN", True, WHITE)
        screen.blit(again_text, (play_again_rect.x + 35, play_again_rect.y + 20))

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not winner and roll_button_rect.collidepoint(event.pos):
                dice1, dice2 = roll_dice()
                dice_result = (dice1, dice2)
                move = dice1 + dice2
                player_idx = turn_order[current_turn_idx]
                players[player_idx] += move

                if players[player_idx] > 99:
                    players[player_idx] = 20
                if players[player_idx] in ladders:
                    players[player_idx] = ladders[players[player_idx]]
                if players[player_idx] in snakes:
                    players[player_idx] = snakes[players[player_idx]]
                if players[player_idx] == 99:
                    winner = player_idx

                current_turn_idx = (current_turn_idx + 1) % len(players)
            elif winner and play_again_rect.collidepoint(event.pos):
                start_new_game()
