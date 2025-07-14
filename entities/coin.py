from config.settings import HEIGHT, WIDTH
import random, math
import pygame

class Coin:
    def __init__(self, x, y, render=True):
        self.x = x
        self.y = y
        self.radius = 10
        import pygame
        if render:
            self.image = pygame.transform.scale(
                pygame.image.load("assets/coin.png").convert_alpha(),
                (2*self.radius, 2*self.radius)
            )
            self.rect = self.image.get_rect(center=(x, y))
        else:
            self.image = None
            self.rect = pygame.Rect(x - self.radius, y - self.radius, 2*self.radius, 2*self.radius)
        self.value = 1

    def move(self, speed):
        self.x -= speed
        self.rect.x = self.x - self.radius

    def draw(self, surface):
        surface.blit(self.image, self.rect)

def spawn_coins(coins, pattern=None, render=False):
    """
    每200像素生成一个金币，y坐标随机。
    """
    y_min, y_max = 80, HEIGHT - 80
    x = WIDTH + 40
    y = random.randint(y_min, y_max)
    coins.append(Coin(x, y, render=render))

def update_coins(coins, state, player_hitbox, paused, speed):
    """
    Move and check collision for each coin.
    """
    to_remove = []
    for coin in coins:
        if not paused:
            coin.move(speed)

        if coin.x < -coin.radius:
            to_remove.append(coin)
        elif player_hitbox.colliderect(coin.rect):
            state.coin_count += coin.value
            to_remove.append(coin)

    for coin in to_remove:
        coins.remove(coin)


def draw_coins(coins, screen):
    """
    Render all coins on screen.
    """
    for coin in coins:
        coin.draw(screen)


def draw_coin_counter(screen, font, coin_count):
    """
    Render the coin counter UI (top right).
    """
    icon_x = WIDTH - 180
    icon_y = 10
    pygame.draw.circle(screen, (255, 215, 0), (icon_x, icon_y + 20), 15)
    pygame.draw.circle(screen, (255, 255, 255), (icon_x, icon_y + 20), 9)
    screen.blit(font.render(f"x {coin_count}", True, 'white'), (icon_x + 30, icon_y + 5))