import random
import pygame

pygame.init()

WIDTH = 1000
HEIGHT = 600
screen = pygame.display.set_mode([WIDTH, HEIGHT])
surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption("Ayo's Pygame Joyride")
fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 32)
bg_color = (128, 128, 128)
lines = [0, WIDTH/4, 2*WIDTH/4, 3*WIDTH/4]
game_speed = 3
pause = False
init_y = HEIGHT - 130
player_y = init_y
booster = False
counter = 0
y_velocity = 0
gravity = 0.4
new_laser = True
laser = []
distance = 0
high_score = 0


# all code to move lines accross screen and draw bg images
def draw_screen(line_list, lase):
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

# draw player including animated states
def draw_payer():
    play = pygame.rect.Rect((120, player_y + 10), (25, 60))
    # pygame.draw.rect(screen, 'green', play, 5) # hittbox
    if player_y < init_y or pause:
        if booster:
            pygame.draw.ellipse(screen, 'red', [100, player_y + 50, 20, 30])
            pygame.draw.ellipse(screen, 'orange', [105, player_y + 50, 10, 30])
            pygame.draw.ellipse(screen, 'yellow', [110, player_y + 50, 5, 30])
        pygame.draw.rect(screen, 'yellow', [128, player_y + 60, 10, 20], 0, 3)
        pygame.draw.rect(screen, 'orange', [130, player_y + 60, 10, 20], 0, 3)
    else:
        if counter < 10:
            pygame.draw.line(screen, 'yellow', (128, player_y + 60), (140, player_y + 80), 10)
            pygame.draw.line(screen, 'orange', (130, player_y + 60), (120, player_y + 80), 10)
        elif 10 <= counter < 20: 
            pygame.draw.rect(screen, 'yellow', [128, player_y + 60, 10, 20], 0, 3)
            pygame.draw.rect(screen, 'orange', [130, player_y + 60, 10, 20], 0, 3)
        elif 20 <= counter < 30:
            pygame.draw.line(screen, 'yellow', (128, player_y + 60), (120, player_y + 80), 10)
            pygame.draw.line(screen, 'orange', (130, player_y + 60), (140, player_y + 80), 10)
        else:
            pygame.draw.rect(screen, 'yellow', [128, player_y + 60, 10, 20], 0, 3)
            pygame.draw.rect(screen, 'orange', [130, player_y + 60, 10, 20], 0, 3)
    # jetpack, body and head
    pygame.draw.rect(screen, 'white', [100, player_y + 20, 20, 30], 0, 5)
    pygame.draw.ellipse(screen, 'orange', [120, player_y + 20, 30, 50])
    pygame.draw.circle(screen, 'orange', (135, player_y + 15), 10)
    pygame.draw.circle(screen, 'black', (138, player_y + 12), 3)
    return play

def check_colliding():
    coll = [False, False]
    if player.colliderect(bot_plat):
        coll[0] = True
    elif player.colliderect(top_plat):
        coll[1] = True
    return coll

def generate_laser():
    # 0 - horiz, 1 - vert
    laser_type = random.randint(0, 1)
    offset = random.randint(10, 300)
    match laser_type:
        case 0:
            laser_width = random.randint(100, 300)
            laser_y = random.randint(100, HEIGHT - 100)
            new_laser = [[WIDTH + offset, laser_y], [WIDTH + offset + laser_width, laser_y]]
        case 1:
            laser_height = random.randint(100, 300)
            laser_y = random.randint(100, HEIGHT - 400)
            new_laser = [[WIDTH + offset, laser_y], [WIDTH + offset + laser_height, laser_y]]
    return new_laser



run = True
while run:
    timer.tick(fps)
    if counter < 40:
        counter += 1
    else:
        counter = 0
    if new_laser:
        laser = generate_laser()
        new_laser = False
    linse, top_plat, bot_plat, laser, laser_line = draw_screen(lines, laser)
    player = draw_payer()
    colliding = check_colliding()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not pause:
                booster = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                booster = False
    
    if not pause:
        distance += game_speed
        if booster:
            y_velocity -= gravity
        else:
            y_velocity += gravity
        if (colliding[0] and y_velocity > 0) or (colliding[1] and y_velocity < 0):
            y_velocity = 0
        player_y += y_velocity 

    # progressive speed increases
    if distance < 50000:
        game_speed = 1 + (distance // 500) / 10
    else:
        game_speed = 11

    if laser[0][0] < 0 and laser[1][0] < 0:
        new_laser = True

    if distance > high_score:
        high_score = int(distance)


    pygame.display.flip()
pygame.quit()