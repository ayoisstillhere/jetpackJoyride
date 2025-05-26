import pygame
from config.settings import WIDTH, HEIGHT, BG_COLOR

def draw_screen(screen, surface, font, bg_color, line_list, lase, pause, game_speed, distance, high_score):
    screen.fill('black')
    pygame.draw.rect(surface, (bg_color[0], bg_color[1], bg_color[2], 50), [0,0, WIDTH, HEIGHT])
    screen.blit(surface, (0,0))
    top = pygame.draw.rect(screen, 'gray', [0, 0, WIDTH, 50])
    bot = pygame.draw.rect(screen, 'gray', [0, HEIGHT - 50, WIDTH, 50])
    for i in range(len(line_list)):
        pygame.draw.line(screen, 'black', (line_list[i], 0), (line_list[i], 50), 3)
        pygame.draw.line(screen, 'black', (line_list[i], HEIGHT - 50), (line_list[i], HEIGHT), 3)
        if not pause:
            line_list[i] -= game_speed
            lase[0][0] -= game_speed
            lase[1][0] -= game_speed
        if line_list[i] < -0:
            line_list[i] = WIDTH
    lase_line = pygame.draw.line(screen, 'yellow', (lase[0][0], lase[0][1]), (lase[1][0], lase[1][1]), 10)
    pygame.draw.circle(screen, 'yellow', (lase[0][0], lase[0][1]), 12)
    pygame.draw.circle(screen, 'yellow', (lase[1][0], lase[1][1]), 12)
    screen.blit(font.render(f'Distance: {int(distance)} m', True, 'white'), (10,10))
    screen.blit(font.render(f'High Score: {int(high_score)} m', True, 'white'), (10,70))
    return line_list, top, bot, lase, lase_line

def draw_pause(surface, font, lifetime, screen):
    pygame.draw.rect(surface, (128, 128, 128, 150), [0, 0, WIDTH, HEIGHT])
    pygame.draw.rect(surface, 'dark gray', [200, 150, 600, 50], 0, 10)
    surface.blit(font.render('Game Paused. Escape Btn Resumes', True, 'black'), (220, 160))
    restart_btn = pygame.draw.rect(surface, 'white', [200, 220, 280, 50], 0, 10)
    surface.blit(font.render('Restart', True, 'black'), (220, 230))
    quit_btn = pygame.draw.rect(surface, 'white', [520, 220, 280, 50], 0, 10)
    surface.blit(font.render('Quit', True, 'black'), (540, 230))
    pygame.draw.rect(surface, 'dark gray', [200, 300, 600, 50], 0, 10)
    surface.blit(font.render(f'Lifetime Distance Ran: {int(lifetime)}', True, 'black'), (220, 310))
    screen.blit(surface, (0,0))
    return restart_btn, quit_btn

def draw_start_screen(screen, font):
    screen.fill('black')
    title = font.render("Pygame Joyride", True, 'white')
    start_btn = pygame.draw.rect(screen, 'white', [350, 300, 300, 60], 0, 10)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 180))
    screen.blit(font.render("Start", True, 'black'), (WIDTH//2 - 40, 315))
    pygame.display.flip()
    return start_btn

def draw_gameover_screen(screen, font, distance, high_score, lifetime):
    screen.fill('black')
    over = font.render("Game Over!", True, 'red')
    score = font.render(f"Distance: {int(distance)} m", True, 'white')
    high = font.render(f"High Score: {int(high_score)} m", True, 'white')
    life = font.render(f"Lifetime: {int(lifetime)} m", True, 'white')
    restart_btn = pygame.draw.rect(screen, 'white', [350, 350, 300, 60], 0, 10)
    screen.blit(over, (WIDTH//2 - over.get_width()//2, 150))
    screen.blit(score, (WIDTH//2 - score.get_width()//2, 220))
    screen.blit(high, (WIDTH//2 - high.get_width()//2, 260))
    screen.blit(life, (WIDTH//2 - life.get_width()//2, 300))
    screen.blit(font.render("Restart", True, 'black'), (WIDTH//2 - 55, 365))
    pygame.display.flip()
    return restart_btn