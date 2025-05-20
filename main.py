import random
import pygame
import os
from PIL import Image
import io
import base64

pygame.init()

WIDTH = 1000
HEIGHT = 600
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Ayo's Pygame Joyride")
fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 32)
bg_color = (128, 128, 128)
lines = [0, WIDTH / 4, 2 * WIDTH / 4, 3 * WIDTH / 4]
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

# 背景相关变量
bg_mode = 4  # 默认使用图片背景: 0-纯色, 1-星空, 2-渐变, 3-网格, 4-图片背景
max_bg_modes = 5
bg_stars = []  # 星空背景的星星
gradient_colors = [(0, 0, 0), (0, 0, 0)]  # 渐变背景的颜色
grid_size = 50  # 网格大小

# 图片背景相关变量
background_images = []  # 存储背景图片列表
current_bg_image = 0  # 当前显示的背景图片索引
transition_alpha = 0  # 用于背景过渡的透明度
transition_active = False  # 是否正在过渡中
next_bg_image = 0  # 下一个要显示的背景图片
transition_speed = 3  # 过渡速度（降低了速度以使过渡更平滑）
forest_sequence_mode = True  # 启用森林场景序列模式
auto_transition_timer = 0  # 自动过渡计时器
auto_transition_delay = 180  # 自动过渡延迟（帧数，约3秒）

# 时钟相关变量
game_time = 0  # 游戏时间（秒）
start_time = 0  # 游戏开始时间

# rocket variables
rocket_counter = 0
rocket_active = False
rocket_delay = 0
rocket_coords = []

# load in player info in beginning
try:
    file = open('player_info.txt', 'r')
    read = file.readlines()
    high_score = int(read[0])
    lifetime = int(read[1])
    file.close()
except FileNotFoundError:
    # 如果文件不存在，创建它
    high_score = 0
    lifetime = 0
    file = open('player_info.txt', 'w')
    file.write("0\n0")
    file.close()
    print("Created new player_info.txt file")


# 内置森林场景图片（Base64编码）
def get_forest_images():
    # 这里存储四个森林场景的Base64编码
    forest_img_data = [
        # 图片1 - 棕色森林背景
        """图片1的base64编码会在这里""",

        # 图片2 - 两棵黑树
        """图片2的base64编码会在这里""",

        # 图片3 - 黄色光线
        """图片3的base64编码会在这里""",

        # 图片4 - 棕色树木剪影
        """图片4的base64编码会在这里"""
    ]

    # 将图片加载到Pygame surfaces
    forest_images = []
    for img_data in forest_img_data:
        try:
            # 由于这部分代码依赖于真实图片文件，此处省略了Base64解码部分
            # 实际中需要从文件加载
            pass
        except Exception as e:
            print(f"Error loading embedded image: {e}")

    return forest_images


# 加载背景图片
def load_background_images():
    images = []
    bg_folder = "backgrounds"  # 背景图片文件夹

    # 检查文件夹是否存在
    if not os.path.exists(bg_folder):
        os.makedirs(bg_folder)
        print(f"Created {bg_folder} folder. Please add your background images there.")

    # 首先尝试从文件夹加载图片
    image_files = []
    for filename in sorted(os.listdir(bg_folder)):  # 排序以确保顺序一致
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            image_files.append(os.path.join(bg_folder, filename))

    # 按名称顺序加载图片（确保森林场景按正确顺序显示）
    for img_path in image_files:
        try:
            # 加载图片并调整大小以匹配屏幕
            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.scale(img, (WIDTH, HEIGHT))
            images.append(img)
            print(f"Loaded background: {os.path.basename(img_path)}")
        except pygame.error as e:
            print(f"Could not load image {img_path}: {e}")

    # 如果没有从文件夹加载到图片，尝试使用内置图片
    if not images:
        print("No background images found in folder. Using default forest images.")
        # 在实际代码中，我们会从get_forest_images()获取图片，
        # 但由于我们需要先有真实文件，这里需要用户添加图片到文件夹

    return images


# 初始化星空背景
def init_stars(num_stars=100):
    stars = []
    for _ in range(num_stars):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(1, 3)
        brightness = random.randint(100, 255)
        stars.append([x, y, size, brightness])
    return stars


# 开始背景过渡
def start_transition():
    global transition_active, transition_alpha, next_bg_image

    if len(background_images) < 2:
        return

    transition_active = True
    transition_alpha = 0

    if forest_sequence_mode:
        # 在森林序列模式下，按顺序选择下一个背景
        next_image = (current_bg_image + 1) % len(background_images)
    else:
        # 在随机模式下，选择一个不同的随机背景
        next_image = current_bg_image
        while next_image == current_bg_image and len(background_images) > 1:
            next_image = random.randint(0, len(background_images) - 1)

    next_bg_image = next_image


# 绘制不同类型的背景
def draw_background(mode, star_list, grad_colors, grid_sz):
    # 总是先清除屏幕
    screen.fill('black')

    if mode == 0:  # 纯色背景
        screen.fill(bg_color)

    elif mode == 1:  # 星空背景
        screen.fill((0, 0, 0))
        for star in star_list:
            pygame.draw.circle(screen, (star[3], star[3], star[3]), (star[0], star[1]), star[2])
            if not pause:
                star[0] -= game_speed / 2  # 星星缓慢移动
                if star[0] < 0:
                    star[0] = WIDTH
                    star[1] = random.randint(0, HEIGHT)

    elif mode == 2:  # 渐变背景
        for y in range(0, HEIGHT, 2):
            r = int(grad_colors[0][0] + (grad_colors[1][0] - grad_colors[0][0]) * y / HEIGHT)
            g = int(grad_colors[0][1] + (grad_colors[1][1] - grad_colors[0][1]) * y / HEIGHT)
            b = int(grad_colors[0][2] + (grad_colors[1][2] - grad_colors[0][2]) * y / HEIGHT)
            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    elif mode == 3:  # 网格背景
        screen.fill((0, 0, 0))
        for x in range(0, WIDTH, grid_sz):
            pygame.draw.line(screen, (bg_color[0], bg_color[1], bg_color[2]), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, grid_sz):
            pygame.draw.line(screen, (bg_color[0], bg_color[1], bg_color[2]), (0, y), (WIDTH, y))

    elif mode == 4:  # 图片背景
        if background_images:
            if transition_active:
                # 绘制当前背景
                screen.blit(background_images[current_bg_image], (0, 0))

                # 使用透明表面来实现过渡效果
                temp_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                temp_surface.blit(background_images[next_bg_image], (0, 0))
                temp_surface.set_alpha(transition_alpha)
                screen.blit(temp_surface, (0, 0))
            else:
                # 只绘制当前背景
                screen.blit(background_images[current_bg_image], (0, 0))
        else:
            # 如果没有图片，绘制一个简单的灰色背景
            screen.fill((50, 50, 50))
            text = font.render("Add images to the 'backgrounds' folder", True, (200, 200, 200))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))


# 绘制屏幕和游戏界面
def draw_screen(line_list, lase):
    # 首先绘制背景（会清除屏幕）
    draw_background(bg_mode, bg_stars, gradient_colors, grid_size)

    # 绘制游戏元素
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

    # 创建半透明背景提高可读性
    info_surface = pygame.Surface((250, 110), pygame.SRCALPHA)
    info_surface.fill((0, 0, 0, 150))  # 黑色半透明背景
    screen.blit(info_surface, (5, 5))

    # 左上角信息显示
    screen.blit(font.render(f'Distance: {int(distance)} m', True, 'white'), (10, 10))
    screen.blit(font.render(f'High Score: {int(high_score)} m', True, 'white'), (10, 60))

    # 右上角信息显示 - 只保留时间和框
    minutes = int(game_time) // 60
    seconds = int(game_time) % 60

    # 创建一个半透明的背景提高可读性
    time_surface = pygame.Surface((130, 40), pygame.SRCALPHA)
    time_surface.fill((0, 0, 0, 150))  # 黑色半透明背景
    screen.blit(time_surface, (WIDTH - 140, 5))

    # 时间文本 - 使用白色显示
    time_text = f'{minutes:02d}:{seconds:02d}'
    screen.blit(font.render(time_text, True, 'white'), (WIDTH - 120, 10))

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
            coords[0] -= 10 + game_speed

    return coords, rock


def draw_pause():
    pause_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(pause_surface, (0, 0, 0, 180), [0, 0, WIDTH, HEIGHT])  # 更暗的背景
    pygame.draw.rect(pause_surface, 'dark gray', [210, 80, 580, 50], 0, 10)
    pause_surface.blit(font.render('Game Paused. ESC to Resume', True, 'white'), (290, 90))

    # 菜单按钮
    restart_btn = pygame.draw.rect(pause_surface, 'white', [210, 150, 580, 50], 0, 10)
    pause_surface.blit(font.render('Restart', True, 'black'), (450, 160))

    forest_btn = pygame.draw.rect(pause_surface, 'white', [210, 220, 580, 50], 0, 10)
    mode_text = "Sequential" if forest_sequence_mode else "Random"
    pause_surface.blit(font.render(f'Image Transitions: {mode_text}', True, 'black'), (330, 230))

    bg_btn = pygame.draw.rect(pause_surface, 'white', [210, 290, 580, 50], 0, 10)
    pause_surface.blit(font.render(f'Background Mode: {bg_mode}', True, 'black'), (350, 300))

    next_bg_btn = pygame.draw.rect(pause_surface, 'white', [210, 360, 580, 50], 0, 10)
    pause_surface.blit(font.render('Next Background', True, 'black'), (400, 370))

    quit_btn = pygame.draw.rect(pause_surface, 'white', [210, 430, 580, 50], 0, 10)
    pause_surface.blit(font.render('Quit', True, 'black'), (450, 440))

    # 添加显示总行程的信息
    pygame.draw.rect(pause_surface, 'dark gray', [210, 500, 580, 50], 0, 10)
    pause_surface.blit(font.render(f'Lifetime Distance: {int(lifetime)} m', True, 'white'), (330, 510))

    screen.blit(pause_surface, (0, 0))
    return restart_btn, quit_btn, bg_btn, forest_btn, next_bg_btn


def modify_player_info():
    global high_score, lifetime
    if distance > high_score:
        high_score = distance
    lifetime += distance
    file = open('player_info.txt', 'w')
    file.write(str(int(high_score)) + '\n')
    file.write(str(int(lifetime)))
    file.close()


# 生成随机渐变背景颜色
def new_gradient_colors():
    color1 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    color2 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return [color1, color2]


# 初始化星空背景
bg_stars = init_stars(150)
gradient_colors = new_gradient_colors()
start_time = pygame.time.get_ticks()  # 记录游戏开始时间

# 加载背景图片
background_images = load_background_images()

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

    # 绘制背景和游戏界面
    linse, top_plat, bot_plat, laser, laser_line = draw_screen(lines, laser)

    if pause:
        restart, quits, bg_button, forest_button, next_bg_button = draw_pause()

    if not rocket_active and not pause:
        rocket_counter += 1
    if rocket_counter > 180:
        rocket_counter = 0
        rocket_active = True
        rocket_delay = 0
        rocket_coords = [WIDTH, HEIGHT / 2]
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

    # 处理背景过渡
    if transition_active and not pause:
        transition_alpha += transition_speed
        if transition_alpha >= 255:
            transition_active = False
            current_bg_image = next_bg_image
            transition_alpha = 0

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
            # 按B键切换背景模式
            if event.key == pygame.K_b and not pause:
                bg_mode = (bg_mode + 1) % max_bg_modes
                if bg_mode == 1:  # 切换到星空背景
                    bg_stars = init_stars(150)
                elif bg_mode == 2:  # 切换到渐变背景
                    gradient_colors = new_gradient_colors()
                elif bg_mode == 4 and len(background_images) > 0:  # 切换到图片背景
                    current_bg_image = random.randint(0, len(background_images) - 1)
            # 按T键开始背景过渡（仅在图片背景模式下）
            if event.key == pygame.K_t and not pause and bg_mode == 4 and len(background_images) > 1:
                if not transition_active:
                    start_transition()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                booster = False
        if event.type == pygame.MOUSEBUTTONDOWN and pause:
            if restart.collidepoint(event.pos):
                restart_cmd = True
            if quits.collidepoint(event.pos):
                modify_player_info()
                run = False
            if bg_button.collidepoint(event.pos):
                bg_mode = (bg_mode + 1) % max_bg_modes
                if bg_mode == 1:  # 切换到星空背景
                    bg_stars = init_stars(150)
                elif bg_mode == 2:  # 切换到渐变背景
                    gradient_colors = new_gradient_colors()
                elif bg_mode == 4 and len(background_images) > 0:  # 切换到图片背景
                    current_bg_image = random.randint(0, len(background_images) - 1)
            if forest_button.collidepoint(event.pos):
                forest_sequence_mode = not forest_sequence_mode
            if next_bg_button.collidepoint(event.pos) and bg_mode == 4 and len(background_images) > 1:
                if not transition_active:
                    start_transition()

    if not pause:
        distance += game_speed
        # 更新游戏时间
        current_time = pygame.time.get_ticks()
        game_time = (current_time - start_time) / 1000  # 毫秒转秒

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

    # 每500米更新背景或触发背景过渡
    if distance - new_bg > 500:
        new_bg = distance
        bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        # 如果是渐变背景，生成新的渐变颜色
        if bg_mode == 2:
            gradient_colors = new_gradient_colors()

        # 如果是网格背景，更新网格大小
        elif bg_mode == 3:
            grid_size = random.randint(30, 70)

        # 如果是图片背景，随机触发过渡效果
        elif bg_mode == 4 and len(background_images) > 1 and random.random() < 0.5:
            if not transition_active:
                start_transition()

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
        # 重置游戏时间
        start_time = pygame.time.get_ticks()
        game_time = 0

    if distance > high_score:
        high_score = int(distance)

    pygame.display.flip()
pygame.quit()