import pygame
import sys
from background_system import BackgroundSystem

# 初始化Pygame
pygame.init()

# 设置窗口
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("背景系统测试")

# 创建背景系统
bg_system = BackgroundSystem(WINDOW_WIDTH, WINDOW_HEIGHT)

# 创建时钟对象
clock = pygame.time.Clock()

# 游戏变量
distance = 0  # 当前行进距离（米）
speed = 100  # 行进速度（米/秒）

# 显示当前信息的函数
def draw_info():
    font = pygame.font.Font(None, 36)
    theme_text = font.render(f"主题: {bg_system.current_theme}", True, (255, 255, 255))
    type_text = font.render(f"背景类型: {bg_system.current_background_type}", True, (255, 255, 255))
    distance_text = font.render(f"距离: {distance:.0f}m", True, (255, 255, 255))
    help_text = font.render("按键: Space-暂停 ESC-退出", True, (255, 255, 255))
    
    screen.blit(theme_text, (10, 10))
    screen.blit(type_text, (10, 50))
    screen.blit(distance_text, (10, 90))
    screen.blit(help_text, (10, WINDOW_HEIGHT - 40))

# 主游戏循环
running = True
paused = False
while running:
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                paused = not paused

    # 更新游戏状态
    if not paused:
        # 更新距离
        distance += speed * (1/60)  # 假设60FPS

    # 更新背景
    bg_system.update(pause=paused, distance=distance)

    # 绘制背景
    bg_system.draw_background(screen, pause=paused)
    
    # 显示信息
    draw_info()

    # 更新显示
    pygame.display.flip()

    # 控制帧率
    clock.tick(60)

# 退出游戏
pygame.quit()
sys.exit() 