import pygame
from config.settings import WIDTH, HEIGHT

def draw_screen(screen, surface, font, bg_color, lines, laser_obj, distance, high_score, pause, game_speed):
    # no fill black background, because background system has already drawn the background
    pygame.draw.rect(surface, (*bg_color, 50), [0, 0, WIDTH, HEIGHT])
    screen.blit(surface, (0, 0))

    # top and bottom platform
    top = pygame.draw.rect(screen, 'gray', [0, 0, WIDTH, 50])
    bot = pygame.draw.rect(screen, 'gray', [0, HEIGHT - 50, WIDTH, 50])

    # platform
    for i in range(len(lines)):
        pygame.draw.line(screen, 'black', (lines[i], 0), (lines[i], 50), 3)
        pygame.draw.line(screen, 'black', (lines[i], HEIGHT - 50), (lines[i], HEIGHT), 3)

        if not pause:
            lines[i] -= game_speed

        if lines[i] < 0:
            lines[i] = WIDTH

    # Update laser position if not paused
    if not pause:
        laser_obj.update(game_speed)

    # Draw laser using the Laser class method
    laser_rect = laser_obj.draw(screen)

    # print score
    screen.blit(font.render(f'Distance: {int(distance)} m', True, 'white'), (10, 10))
    screen.blit(font.render(f'High Score: {int(high_score)} m', True, 'white'), (10, 70))

    return lines, top, bot, laser_obj.points, laser_rect