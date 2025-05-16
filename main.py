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
restart_cmd = False
new_bg = 0

# rocket variables
rocket_counter = 0
rocket_active = False
rocket_delay = 0
rocket_coords = []

# load in player info in beginning
file = open('player_info.txt', 'r')
read = file.readlines()
high_score = int(read[0])
lifetime = int(read[1])
file.close()


# --- Coin System Variables ---
class Coin:
    def __init__(self, x, y, value=1):
        self.x = x
        self.y = y
        self.radius = 15
        self.value = value
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)
    def move(self, speed):
        self.x -= speed
        self.rect.x = self.x - self.radius
    def draw(self, surf):
        pygame.draw.circle(surf, (255, 215, 0), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, (255, 255, 255), (int(self.x), int(self.y)), self.radius-6)

coins = []
coin_count = 0
coin_spawn_distance = 400  # Distance between coin spawns
last_coin_spawn = 0


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
    rstrt = False
    if player.colliderect(bot_plat):
        coll[0] = True
    elif player.colliderect(top_plat):
        coll[1] = True
    if laser_line.colliderect(player):
        rstrt = True
    if rocket_active:
        if rocket.colliderect(player):
            rstrt = True
    return coll, rstrt

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

def draw_rocket(coords, mode):
    if mode == 0:
        rock = pygame.draw.rect(screen, 'dark red', [coords[0] - 60, coords[1] - 25, 50, 50], 0, 5)
        screen.blit(font.render('!', True, 'black'), (coords[0] - 40, coords[1]-20))
        if not pause:
            if coords[1] > player_y + 10:
                coords[1] -= 3
            else:
                coords[1] += 3
    else:
        rock = pygame.draw.rect(screen, 'red', [coords[0], coords[1] - 10, 50, 20], 0, 5)
        pygame.draw.ellipse(screen, 'orange', [coords[0] + 50, coords[1] - 10, 50, 20], 7)
        if not pause:
            coords[0] -= 10 + game_speed


    return coords, rock

def draw_pause():
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

def modify_player_info():
    global high_score, lifetime
    if distance > high_score:
        high_score = distance
    lifetime += distance
    file = open('player_info.txt', 'w')
    file.write(str(int(high_score)) + '\n')
    file.write(str(int(lifetime)))
    file.close

def spawn_coins(pattern=None):
    global coins
    y_min, y_max = 80, HEIGHT - 80
    x = WIDTH + 40
    if pattern is None:
        pattern = random.choice(['single', 'horiz', 'vert'])
    if pattern == 'single':
        y = random.randint(y_min, y_max)
        coins.append(Coin(x, y))
    elif pattern == 'horiz':
        y = random.randint(y_min, y_max)
        for i in range(5):
            coins.append(Coin(x + i*40, y))
    elif pattern == 'vert':
        y = random.randint(y_min+100, y_max-100)
        for i in range(5):
            coins.append(Coin(x, y + i*40))
    # Optional: add more patterns

def update_coins():
    global coins, coin_count
    remove_list = []
    for coin in coins:
        coin.move(game_speed)
        if coin.x < -coin.radius:
            remove_list.append(coin)
        elif player.colliderect(coin.rect):
            coin_count += coin.value
            remove_list.append(coin)
            # Optional: play sound here
    for coin in remove_list:
        coins.remove(coin)

def draw_coins():
    for coin in coins:
        coin.draw(screen)

def draw_coin_counter():
    coin_icon_x = WIDTH - 180
    coin_icon_y = 10
    pygame.draw.circle(screen, (255, 215, 0), (coin_icon_x, coin_icon_y+20), 15)
    pygame.draw.circle(screen, (255, 255, 255), (coin_icon_x, coin_icon_y+20), 9)
    screen.blit(font.render(f"x {coin_count}", True, 'white'), (coin_icon_x+30, coin_icon_y+5))


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
    if pause:
        restart, quits = draw_pause()

    # --- COIN SYSTEM: Spawning ---
    if not pause and distance - last_coin_spawn > coin_spawn_distance:
        spawn_coins()
        last_coin_spawn = distance

    # --- COIN SYSTEM: Update and Draw ---
    update_coins()
    draw_coins()
    draw_coin_counter()

    if not rocket_active and not pause:
        rocket_counter += 1
    if rocket_counter > 180:
        rocket_counter = 0
        rocket_active = True
        rocket_delay = 0
        rocket_coords = [WIDTH, HEIGHT/2]
    if rocket_active:
        if rocket_delay < 90:
            if not pause:
                rocket_delay += 1
            rocket_coords, rocket = draw_rocket(rocket_coords, 0)
        else:
            rocket_coords, rocket = draw_rocket(rocket_coords, 1)
        if rocket_coords[0] < -50:
            rocket_active = False

    player = draw_payer()
    colliding, restart_cmd = check_colliding()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            modify_player_info()
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if pause:
                    pause = False
                else:
                    pause = True
            if event.key == pygame.K_SPACE and not pause:
                booster = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                booster = False
        if event.type == pygame.MOUSEBUTTONDOWN and pause:
            if restart.collidepoint(event.pos):
                restart_cmd = True
            if quits.collidepoint(event.pos):
                modify_player_info()
                run = False
    
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

    if distance - new_bg > 500:
        new_bg = distance
        bg_color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))

    if restart_cmd:
        modify_player_info()
        distance = 0
        rocket_active = False
        rocket_counter = 0
        pause = False
        player_y = init_y
        y_velocity = 0
        restart_cmd = 0
        new_laser = True
        coins.clear()
        coin_count = 0
        last_coin_spawn = 0


    if distance > high_score:
        high_score = int(distance)


    pygame.display.flip()
pygame.quit()