from config.settings import HEIGHT, WIDTH
import random, math
import pygame

class Coin:
    def __init__(self, x, y, value=1):
        # Use float internally
        self.x = float(x)
        self.y = float(y)
        self.radius = 15
        self.value = value
        self.image = pygame.transform.scale(
            pygame.image.load("assets/coin.png").convert_alpha(),
            (2 * self.radius, 2 * self.radius)
        )
        # Rectangle based on int
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def _update_rect(self):
        """Atualiza self.rect baseado nas coordenadas atuais (convertendo para int)."""
        self.rect.center = (int(self.x), int(self.y))

    def move(self, speed):
        # Update position in float
        self.x -= speed
        self._update_rect()

    def draw(self, surface):
        # Before drawing, ensure rect is coherent
        self._update_rect()
        surface.blit(self.image, self.rect)


def spawn_coins(coins, pattern=None):
    """
    Add coins to the list based on a spawn pattern.
    """
    y_min, y_max = 80, HEIGHT - 80
    x = WIDTH + 40

    if pattern is None:
        pattern = random.choice([
            'single', 'horiz', 'vert', 'cluster', 'diag_up', 'diag_down', 'circle'
        ])

    if pattern == 'single':
        y = random.randint(y_min, y_max)
        coins.append(Coin(x, y))

    elif pattern == 'horiz':
        y = random.randint(y_min, y_max)
        for i in range(random.randint(3, 8)):
            coins.append(Coin(x + i * 40, y))

    elif pattern == 'vert':
        y = random.randint(y_min + 100, y_max - 100)
        for i in range(random.randint(3, 8)):
            coins.append(Coin(x, y + i * 40))

    elif pattern == 'diag_up':
        y = random.randint(y_min + 100, y_max - 100)
        for i in range(random.randint(3, 7)):
            coins.append(Coin(x + i * 35, y - i * 35))

    elif pattern == 'diag_down':
        y = random.randint(y_min + 100, y_max - 100)
        for i in range(random.randint(3, 7)):
            coins.append(Coin(x + i * 35, y + i * 35))

    elif pattern == 'circle':
        n = random.randint(6, 10)
        radius = random.randint(40, 70)
        center_y = random.randint(y_min + radius, y_max - radius)
        center_x = x + 60
        for i in range(n):
            angle = 2 * math.pi * i / n
            cx = center_x + int(radius * math.cos(angle))
            cy = center_y + int(radius * math.sin(angle))
            coins.append(Coin(cx, cy))

    elif pattern == 'cluster':
        rows = random.randint(2, 4)
        cols = random.randint(3, 6)
        spacing_x = 32
        spacing_y = 32
        center_y = random.randint(y_min + spacing_y * rows, y_max - spacing_y * rows)
        center_x = x + 40
        for row in range(rows):
            for col in range(cols):
                coin_x = center_x + col * spacing_x
                coin_y = center_y + row * spacing_y
                coins.append(Coin(coin_x, coin_y))


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
            print(f"------------------- COLLISION! Player: {player_hitbox}, Coin: {coin.rect}")
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