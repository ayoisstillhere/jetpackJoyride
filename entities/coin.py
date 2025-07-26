from config.settings import HEIGHT, WIDTH
import random, math
import pygame

class Coin:
    def __init__(self, x, y, value=1, render=True):
        self.x = x
        self.y = y
        self.radius = 20
        self.value = value
        self.render = render
        
        if self.render:
            self.image = pygame.transform.scale(pygame.image.load("assets/coin.png").convert_alpha(), (40, 40))
            self.rect = self.image.get_rect(center=(x, y))
        else:
            self.image = None
            # Create a simple rect for collision detection even when not rendering
            self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)

    def move(self, speed):
        self.x -= speed
        self.rect.x = self.x - self.radius

    def draw(self, surface):
        if self.render and self.image:
            surface.blit(self.image, self.rect)

def spawn_coins(coins, render=True, spacing=150, initial_spawn=False):
    """
    Generate only one coin each time, with random y value and x value determined by mode.
    spacing parameter controls the distance between coins.
    initial_spawn: If True, generate coins evenly spaced within the visible screen range
    """
    y_min, y_max = 80, HEIGHT - 80
    
    if initial_spawn:
        if len(coins) == 0:
            x = WIDTH - 100
        else:
            last_coin_x = min(coin.x for coin in coins)
            x = last_coin_x - spacing
    else:
        if len(coins) == 0:
            x = WIDTH + 40
        else:
            max_x = max(coin.x for coin in coins) if coins else WIDTH
            x = max(WIDTH + 40, max_x + spacing)
    
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