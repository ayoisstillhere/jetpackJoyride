import pygame
from config.settings import WIDTH, HEIGHT

def draw_screen(screen, surface, font, bg_color, lines, laser, distance, high_score, pause, game_speed):
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
            laser[0][0] -= game_speed
            laser[1][0] -= game_speed

        if lines[i] < 0:
            lines[i] = WIDTH

    # laser
    start = laser[0]
    end = laser[1]
    pygame.draw.line(screen, 'yellow', start, end, 10)
    pygame.draw.circle(screen, 'yellow', start, 12)
    pygame.draw.circle(screen, 'yellow', end, 12)

    laser_rect = pygame.Rect(
        min(start[0], end[0]),
        min(start[1], end[1]) - 5,
        abs(end[0] - start[0]),
        10  # laser thickness
    )

    # pint score
    screen.blit(font.render(f'Distance: {int(distance)} m', True, 'white'), (10, 10))
    screen.blit(font.render(f'High Score: {int(high_score)} m', True, 'white'), (10, 70))

    return lines, top, bot, laser, laser_rect
