import pygame
import random
from settings import *
from player import load_player_assets, draw_player
from coin import Coin, spawn_coins, update_coins, draw_coins, draw_coin_counter
from laser import generate_laser
from rocket import draw_rocket
from ui import draw_screen, draw_pause, draw_start_screen, draw_gameover_screen
from storage import load_player_info, save_player_info

pygame.init()
screen = pygame.display.set_mode([WIDTH, HEIGHT])
surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption("Pygame Joyride")
timer = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 32)

lines = [0, WIDTH/4, 2*WIDTH/4, 3*WIDTH/4]
game_speed = 3
pause = False
player_y = INIT_Y
booster = False
counter = 0
y_velocity = 0
new_laser = True
laser = []
distance = 0
restart_cmd = False
new_bg = 0

rocket_counter = 0
rocket_active = False
rocket_delay = 0
rocket_coords = []

high_score, lifetime = load_player_info()

coins = []
coin_count = 0
last_coin_spawn = 0

run_frames, jump_up_img, jump_down_img, flame_img = load_player_assets()

# Game states
STATE_START = 0
STATE_PLAYING = 1
STATE_PAUSED = 2
STATE_GAMEOVER = 3
game_state = STATE_START

run = True
while run:
    timer.tick(FPS)
    if game_state == STATE_START:
        start_btn = draw_start_screen(screen, font)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(event.pos):
                    # Reset all variables for a new game
                    distance = 0
                    rocket_active = False
                    rocket_counter = 0
                    pause = False
                    player_y = INIT_Y
                    y_velocity = 0
                    new_laser = True
                    coins.clear()
                    coin_count = 0
                    last_coin_spawn = 0
                    lines = [0, WIDTH/4, 2*WIDTH/4, 3*WIDTH/4]
                    game_speed = 3
                    new_bg = 0
                    BG_COLOR = (128, 128, 128)
                    game_state = STATE_PLAYING

    elif game_state == STATE_PLAYING:
        if not pause:
            if counter < 40:
                counter += 1
            else:
                counter = 0

        # Laser generation
        if new_laser:
            laser = generate_laser()
            new_laser = False

        # Draw background, lines, and laser
        lines, top_plat, bot_plat, laser, laser_line = draw_screen(
            screen, surface, font, BG_COLOR, lines, laser, pause, game_speed, distance, high_score
        )

        # Coin spawning
        if not pause and distance - last_coin_spawn > COIN_SPAWN_DISTANCE:
            spawn_coins(coins)
            last_coin_spawn = distance

        # Coin update and draw
        coin_count = update_coins(coins, coin_count, pause, game_speed, pygame.Rect(120, player_y + 10, 55, 60))
        draw_coins(coins, screen)
        draw_coin_counter(screen, font, coin_count)

        # Rocket logic
        if not rocket_active and not pause:
            rocket_counter += 1
        if rocket_counter > 180:
            rocket_counter = 0
            rocket_active = True
            rocket_delay = 0
            rocket_coords = [WIDTH, HEIGHT // 2]
        if rocket_active:
            if rocket_delay < 90:
                if not pause:
                    rocket_delay += 1
                rocket_coords, rocket = draw_rocket(screen, font, rocket_coords, 0, pause, player_y, game_speed)
            else:
                rocket_coords, rocket = draw_rocket(screen, font, rocket_coords, 1, pause, player_y, game_speed)
            if rocket_coords[0] < -50:
                rocket_active = False

        # Draw player and get rect
        player = draw_player(
            screen, player_y, INIT_Y, y_velocity, booster, counter,
            run_frames, jump_up_img, jump_down_img, flame_img
        )

        # Collision checks
        colliding_top = player.colliderect(top_plat)
        colliding_bot = player.colliderect(bot_plat)
        if laser_line.colliderect(player):
            game_state = STATE_GAMEOVER
        # Rocket collision
        if rocket_active:
            if 'rocket' in locals() and rocket.colliderect(player):
                game_state = STATE_GAMEOVER

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_player_info(high_score, lifetime)
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause = not pause
                if event.key == pygame.K_SPACE and not pause:
                    booster = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    booster = False
            if event.type == pygame.MOUSEBUTTONDOWN and pause:
                restart, quits = draw_pause(surface, font, lifetime, screen)
                if restart.collidepoint(event.pos):
                    # Restart game from pause
                    distance = 0
                    rocket_active = False
                    rocket_counter = 0
                    pause = False
                    player_y = INIT_Y
                    y_velocity = 0
                    new_laser = True
                    coins.clear()
                    coin_count = 0
                    last_coin_spawn = 0
                    lines = [0, WIDTH/4, 2*WIDTH/4, 3*WIDTH/4]
                    game_speed = 3
                    new_bg = 0
                if quits.collidepoint(event.pos):
                    save_player_info(high_score, lifetime)
                    run = False

        # Physics and game state updates
        if not pause:
            distance += game_speed
            if booster:
                y_velocity -= GRAVITY
            else:
                y_velocity += GRAVITY
            if (colliding_bot and y_velocity > 0) or (colliding_top and y_velocity < 0):
                y_velocity = 0
            player_y += y_velocity

        # Progressive speed
        if distance < 50000:
            game_speed = 1 + (distance // 500) / 10
        else:
            game_speed = 11

        # Laser reset
        if laser[0][0] < 0 and laser[1][0] < 0:
            new_laser = True

        # Background color change
        if distance - new_bg > 500:
            new_bg = distance
            BG_COLOR = (random.randint(0,255), random.randint(0,255), random.randint(0,255))

        # High score update
        if distance > high_score:
            high_score = int(distance)

        # Pause menu
        if pause:
            restart, quits = draw_pause(surface, font, lifetime, screen)

        pygame.display.flip()

    elif game_state == STATE_GAMEOVER:
        restart_btn = draw_gameover_screen(screen, font, distance, high_score, lifetime)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_player_info(high_score, lifetime)
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_btn.collidepoint(event.pos):
                    if distance > high_score:
                        high_score = int(distance)
                    lifetime += int(distance)
                    save_player_info(high_score, lifetime)
                    # Reset all variables for a new game
                    distance = 0
                    rocket_active = False
                    rocket_counter = 0
                    pause = False
                    player_y = INIT_Y
                    y_velocity = 0
                    new_laser = True
                    coins.clear()
                    coin_count = 0
                    last_coin_spawn = 0
                    lines = [0, WIDTH/4, 2*WIDTH/4, 3*WIDTH/4]
                    game_speed = 3
                    new_bg = 0
                    BG_COLOR = (128, 128, 128)
                    game_state = STATE_PLAYING

pygame.quit()