import pygame
import random
import math
from config.settings import WIDTH, HEIGHT

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

def spawn_coins(coins, pattern=None):
    y_min, y_max = 80, HEIGHT - 80
    x = WIDTH + 40
    if pattern is None:
        pattern = random.choice(['single', 'horiz', 'vert', 'diag_up', 'diag_down', 'circle', 'cluster'])
    if pattern == 'single':
        y = random.randint(y_min, y_max)
        coins.append(Coin(x, y))
    elif pattern == 'horiz':
        y = random.randint(y_min, y_max)
        n = random.randint(3, 8)
        for i in range(n):
            coins.append(Coin(x + i*40, y))
    elif pattern == 'vert':
        y = random.randint(y_min+100, y_max-100)
        n = random.randint(3, 8)
        for i in range(n):
            coins.append(Coin(x, y + i*40))
    elif pattern == 'diag_up':
        y = random.randint(y_min+100, y_max-100)
        n = random.randint(3, 7)
        for i in range(n):
            coins.append(Coin(x + i*35, y - i*35))
    elif pattern == 'diag_down':
        y = random.randint(y_min+100, y_max-100)
        n = random.randint(3, 7)
        for i in range(n):
            coins.append(Coin(x + i*35, y + i*35))
    elif pattern == 'circle':
        n = random.randint(6, 10)
        radius = random.randint(40, 70)
        center_y = random.randint(y_min+radius, y_max-radius)
        center_x = x + 60
        for i in range(n):
            angle = 2 * 3.14159 * i / n
            cx = center_x + int(radius * math.cos(angle))
            cy = center_y + int(radius * math.sin(angle))
            coins.append(Coin(cx, cy))
    elif pattern == 'cluster':
        rows = random.randint(2, 4)
        cols = random.randint(3, 6)
        grid_spacing_x = 32
        grid_spacing_y = 32
        total_height = (rows - 1) * grid_spacing_y
        total_width = (cols - 1) * grid_spacing_x
        # Center the grid vertically and horizontally within the allowed area
        center_y = random.randint(y_min + total_height // 2, y_max - total_height // 2)
        center_x = x + 40 + total_width // 2
        for row in range(rows):
            for col in range(cols):
                coin_x = center_x + (col - (cols - 1) / 2) * grid_spacing_x
                coin_y = center_y + (row - (rows - 1) / 2) * grid_spacing_y
                coins.append(Coin(int(coin_x), int(coin_y)))


def update_coins(coins, coin_count, pause, game_speed, player):
    remove_list = []
    for coin in coins:
        if not pause:
            coin.move(game_speed)
        if coin.x < -coin.radius:
            remove_list.append(coin)
        elif player.colliderect(coin.rect):
            coin_count += coin.value
            remove_list.append(coin)
    for coin in remove_list:
        coins.remove(coin)
    return coin_count

def draw_coins(coins, screen):
    for coin in coins:
        coin.draw(screen)

def draw_coin_counter(screen, font, coin_count):
    from config.settings import WIDTH
    coin_icon_x = WIDTH - 180
    coin_icon_y = 10
    pygame.draw.circle(screen, (255, 215, 0), (coin_icon_x, coin_icon_y+20), 15)
    pygame.draw.circle(screen, (255, 255, 255), (coin_icon_x, coin_icon_y+20), 9)
    screen.blit(font.render(f"x {coin_count}", True, 'white'), (coin_icon_x+30, coin_icon_y+5))