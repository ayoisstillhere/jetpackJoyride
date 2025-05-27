import pygame
import random
from background_system import BackgroundSystem
from difficulty_system import DifficultySystem

# 初始化Pygame
pygame.init()

# 游戏窗口设置
WIDTH = 1000
HEIGHT = 600
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Jetpack Joyride")
fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 32)

# 初始化系统
background_system = BackgroundSystem(WIDTH, HEIGHT)
difficulty_system = DifficultySystem()

# 游戏状态变量
distance = 0
pause = False
game_time = 0
start_time = pygame.time.get_ticks()
high_score = 0
lifetime = 0

# 玩家相关变量
init_y = HEIGHT - 130
player_y = init_y
y_velocity = 0
gravity = 0.4
booster = False
counter = 0

# 障碍物相关变量
new_laser = True
laser = []
rocket_counter = 0
rocket_active = False
rocket_delay = 0
rocket_coords = []
spike_active = False
spike_coords = []
spike_counter = 0
spike_pattern = 0

# 加载玩家信息
try:
    with open('player_info.txt', 'r') as file:
        read = file.readlines()
        high_score = int(read[0])
        lifetime = int(read[1])
except FileNotFoundError:
    high_score = 0
    lifetime = 0
    with open('player_info.txt', 'w') as file:
        file.write("0\n0")
    print("Created new player_info.txt file")

def save_player_info():
    global high_score, lifetime
    if distance > high_score:
        high_score = distance
    lifetime += distance
    with open('player_info.txt', 'w') as file:
        file.write(f"{int(high_score)}\n{int(lifetime)}")

def draw_player():
    play = pygame.rect.Rect((120, player_y + 10), (25, 60))
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
    
    pygame.draw.rect(screen, 'white', [100, player_y + 20, 20, 30], 0, 5)
    pygame.draw.ellipse(screen, 'orange', [120, player_y + 20, 30, 50])
    pygame.draw.circle(screen, 'orange', (135, player_y + 15), 10)
    pygame.draw.circle(screen, 'black', (138, player_y + 12), 3)
    return play

def generate_laser():
    laser_type = random.randint(0, 1)
    offset = random.randint(10, 300)
    if laser_type == 0:
            laser_width = random.randint(100, 300)
            laser_y = random.randint(100, HEIGHT - 100)
            new_laser = [[WIDTH + offset, laser_y], [WIDTH + offset + laser_width, laser_y]]
    else:
            laser_height = random.randint(100, 300)
            laser_y = random.randint(100, HEIGHT - 400)
            new_laser = [[WIDTH + offset, laser_y], [WIDTH + offset + laser_height, laser_y]]
    return new_laser

def draw_rocket(coords, mode):
    if mode == 0:
        rock = pygame.draw.rect(screen, 'dark red', [coords[0] - 60, coords[1] - 25, 50, 50], 0, 5)
        screen.blit(font.render('!', True, 'black'), (coords[0] - 40, coords[1] - 20))
        if not pause:
            if coords[1] > player_y + 10:
                coords[1] -= 3
            else:
                coords[1] += 3
    else:
        rock = pygame.draw.rect(screen, 'red', [coords[0], coords[1] - 10, 50, 20], 0, 5)
        pygame.draw.ellipse(screen, 'orange', [coords[0] + 50, coords[1] - 10, 50, 20], 7)
        if not pause:
            coords[0] -= 10 + difficulty_system.game_speed
    return coords, rock

def draw_spike(coords, pattern):
    spikes = []
    if pattern == 0:  # 单个尖刺
        spike = pygame.draw.polygon(screen, 'gray', [
            (coords[0], coords[1]),
            (coords[0] - 20, coords[1] + 40),
            (coords[0] + 20, coords[1] + 40)
        ])
        spikes.append(spike)
    elif pattern == 1:  # 连续尖刺
        for i in range(3):
            x_offset = i * 50
            spike = pygame.draw.polygon(screen, 'gray', [
                (coords[0] + x_offset, coords[1]),
                (coords[0] - 20 + x_offset, coords[1] + 40),
                (coords[0] + 20 + x_offset, coords[1] + 40)
            ])
            spikes.append(spike)
    else:  # 交错尖刺
        heights = [0, 40, 0]
        for i in range(3):
            x_offset = i * 50
            y_offset = heights[i]
            spike = pygame.draw.polygon(screen, 'gray', [
                (coords[0] + x_offset, coords[1] + y_offset),
                (coords[0] - 20 + x_offset, coords[1] + 40 + y_offset),
                (coords[0] + 20 + x_offset, coords[1] + 40 + y_offset)
            ])
            spikes.append(spike)
    
    if not pause:
        coords[0] -= difficulty_system.game_speed
    return coords, spikes

def draw_hud():
    info_surface = pygame.Surface((250, 110), pygame.SRCALPHA)
    info_surface.fill((0, 0, 0, 150))
    screen.blit(info_surface, (5, 5))

    screen.blit(font.render(f'Distance: {int(distance)} m', True, 'white'), (10, 10))
    screen.blit(font.render(f'High Score: {int(high_score)} m', True, 'white'), (10, 60))

    minutes = int(game_time) // 60
    seconds = int(game_time) % 60
    time_surface = pygame.Surface((130, 40), pygame.SRCALPHA)
    time_surface.fill((0, 0, 0, 150))
    screen.blit(time_surface, (WIDTH - 140, 5))
    time_text = f'{minutes:02d}:{seconds:02d}'
    screen.blit(font.render(time_text, True, 'white'), (WIDTH - 120, 10))

def draw_pause_menu():
    pause_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(pause_surface, (0, 0, 0, 180), [0, 0, WIDTH, HEIGHT])
    
    pygame.draw.rect(pause_surface, 'dark gray', [210, 80, 580, 50], 0, 10)
    pause_surface.blit(font.render('Game Paused. ESC to Resume', True, 'white'), (290, 90))

    restart_btn = pygame.draw.rect(pause_surface, 'white', [210, 150, 580, 50], 0, 10)
    pause_surface.blit(font.render('Restart', True, 'black'), (450, 160))

    quit_btn = pygame.draw.rect(pause_surface, 'white', [210, 430, 580, 50], 0, 10)
    pause_surface.blit(font.render('Quit', True, 'black'), (450, 440))

    pygame.draw.rect(pause_surface, 'dark gray', [210, 500, 580, 50], 0, 10)
    pause_surface.blit(font.render(f'Lifetime Distance: {int(lifetime)} m', True, 'white'), (330, 510))

    screen.blit(pause_surface, (0, 0))
    return restart_btn, quit_btn

def check_collisions(player, laser_line):
    global rocket_active, rocket, spike_coords, spike_active, spike_pattern
    coll = [False, False]
    restart_cmd = False
    
    # 检查与上下边界的碰撞
    if player.colliderect(pygame.Rect(0, HEIGHT - 50, WIDTH, 50)):
        coll[0] = True
    elif player.colliderect(pygame.Rect(0, 0, WIDTH, 50)):
        coll[1] = True
        
    # 检查与激光的碰撞
    if laser_line.colliderect(player):
        restart_cmd = True
        
    # 检查与火箭的碰撞
    if rocket_active and 'rocket' in locals():
        if rocket.colliderect(player):
            restart_cmd = True
            
    # 检查与尖刺的碰撞
    if spike_active and spike_coords and len(spike_coords) > 0:
        spike_coords, spikes = draw_spike(spike_coords, spike_pattern)
        for spike in spikes:
            if spike.colliderect(player):
                restart_cmd = True
                
    return coll, restart_cmd

def reset_game():
    global distance, player_y, y_velocity, booster, counter, new_laser
    global rocket_active, rocket_counter, rocket_delay, rocket_coords
    global spike_active, spike_coords, spike_counter, spike_pattern
    global game_time, start_time
    
    save_player_info()
    distance = 0
    player_y = init_y
    y_velocity = 0
    booster = False
    counter = 0
    new_laser = True
    
    rocket_active = False
    rocket_counter = 0
    rocket_delay = 0
    rocket_coords = []
    
    spike_active = False
    spike_coords = []
    spike_counter = 0
    spike_pattern = 0
    
    difficulty_system.reset()
    start_time = pygame.time.get_ticks()
    game_time = 0

# 游戏主循环
running = True
while running:
    # 处理暂停菜单
    if pause:
        restart_btn, quit_btn = draw_pause_menu()
    
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            save_player_info()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pause = not pause
                if not pause:
                    start_time = pygame.time.get_ticks() - int(game_time * 1000)
            if event.key == pygame.K_SPACE and not pause:
                booster = True
                
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                booster = False
                
        if event.type == pygame.MOUSEBUTTONDOWN and pause:
            pos = pygame.mouse.get_pos()
            if restart_btn.collidepoint(pos):
                reset_game()
            elif quit_btn.collidepoint(pos):
                save_player_info()
                running = False

    if not pause:
        # 更新游戏时间
        game_time = (pygame.time.get_ticks() - start_time) / 1000
        
        # 更新距离
        distance += difficulty_system.game_speed / 10
        
        # 更新背景
        background_system.update(pause=pause, distance=distance)
        
        # 更新难度
        difficulty_system.update(distance)
        
        # 更新玩家位置
        if booster and player_y > 50:
            y_velocity = -6
        elif not booster and player_y < init_y:
            y_velocity = 6
        
        player_y += y_velocity
        if player_y >= init_y:
            player_y = init_y
            y_velocity = 0
        
        # 更新计数器
        counter = (counter + 1) % 40
        
        # 生成和更新激光
        if new_laser:
            laser = generate_laser()
            new_laser = False
        
        if not new_laser:
            laser[0][0] -= difficulty_system.game_speed
            laser[1][0] -= difficulty_system.game_speed
            if laser[0][0] <= 0:
                new_laser = True
        
        # 生成和更新火箭
        if not rocket_active:
            rocket_counter += 1
            if rocket_counter > rocket_delay:
                rocket_active = True
                rocket_coords = [WIDTH, player_y + 40]
                rocket_counter = 0
                rocket_delay = random.randint(120, 240)
        
        # 生成和更新尖刺
        if not spike_active:
            spike_counter += 1
            if spike_counter > 180:
                spike_active = True
                spike_coords = [WIDTH, HEIGHT - 90]
                spike_pattern = random.randint(0, 2)
                spike_counter = 0

    # 绘制背景
    background_system.draw_background(screen, pause=pause)
    
    # 绘制地面和天花板
    pygame.draw.rect(screen, 'dark gray', [0, 0, WIDTH, 50])
    pygame.draw.rect(screen, 'dark gray', [0, HEIGHT - 50, WIDTH, 50])
    
    # 绘制激光
    if not new_laser:
        laser_rect = pygame.draw.line(screen, 'red', laser[0], laser[1], 4)
        pygame.draw.circle(screen, 'white', (laser[0]), 10)
        pygame.draw.circle(screen, 'white', (laser[1]), 10)
    
    # 绘制火箭
    if rocket_active:
        rocket_coords, rocket = draw_rocket(rocket_coords, 1)
        if rocket_coords[0] < -50:
            rocket_active = False
    
    # 绘制尖刺
    if spike_active and spike_coords:
        spike_coords, spikes = draw_spike(spike_coords, spike_pattern)
        if spike_coords[0] < -100:
            spike_active = False
    
    # 绘制玩家
    player = draw_player()
    
    # 检查碰撞
    collisions, restart = check_collisions(player, laser_rect if not new_laser else pygame.Rect(0, 0, 0, 0))
    if restart:
        reset_game()
    
    # 绘制HUD
    draw_hud()
    
    # 更新显示
    pygame.display.flip()
    timer.tick(fps)

pygame.quit()