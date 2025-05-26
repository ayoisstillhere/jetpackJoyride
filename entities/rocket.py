import pygame

missile_sprite = None

def load_rocket_assets():
    global missile_sprite
    missile_sprite = pygame.image.load("assets/rocket.png").convert_alpha()
    missile_sprite = pygame.transform.scale(missile_sprite, (150, 60))  # 4 times bigger
    missile_sprite = pygame.transform.flip(missile_sprite, True, False)  # Flip horizontally

def draw_rocket(screen, font, coords, mode, pause, player_y, game_speed):
    global missile_sprite
    if missile_sprite is None:
        load_rocket_assets()
    
    if mode == 0:
        rock = pygame.draw.rect(screen, 'dark red', [coords[0] - 60, coords[1] - 25, 50, 50], 0, 5)
        screen.blit(font.render('!', True, 'black'), (coords[0] - 40, coords[1]-20))
        if not pause:
            if coords[1] > player_y + 10:
                coords[1] -= 3
            else:
                coords[1] += 3
    else:
        rock = screen.blit(missile_sprite, (coords[0] - 200, coords[1] - 40))  # Adjust position for larger sprite
        if not pause:
            coords[0] -= 10 + game_speed
    return coords, rock