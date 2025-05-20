import pygame

def load_player_assets():
    run_frames = []
    for i in range(0, 6):
        img = pygame.image.load(f"assets/run/run{i}.png").convert_alpha()
        run_frames.append(pygame.transform.scale(img, (55, 60)))
    jump_up = pygame.image.load("assets/jump_up.png").convert_alpha()
    jump_up = pygame.transform.scale(jump_up, (55, 60))
    jump_down = pygame.image.load("assets/jump_down.png").convert_alpha()
    jump_down = pygame.transform.scale(jump_down, (55, 60))
    flame_img = pygame.image.load("assets/flame.png").convert_alpha()
    flame_img = pygame.transform.scale(flame_img, (20, 30))
    return run_frames, jump_up, jump_down, flame_img

def draw_player(screen, player_y, init_y, y_velocity, booster, counter, run_frames, jump_up_img, jump_down_img, flame_img):
    play_rect = pygame.Rect(120, player_y + 10, 55, 60)
    if player_y < init_y:
        if y_velocity < 0:
            if booster:
                screen.blit(flame_img, (135, player_y + 60))
            screen.blit(jump_up_img, (120, player_y))
        else:
            screen.blit(jump_down_img, (120, player_y))
    else:
        frame_index = (counter // 6) % len(run_frames)
        screen.blit(run_frames[frame_index], (120, player_y))
    return play_rect