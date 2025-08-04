import pygame
from config.settings import WIDTH, HEIGHT

class Rocket:
    def __init__(self, render=True):
        self.reset()
        self.render = render

        if render:
            self.image = pygame.image.load('assets/rocket.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (100, 30))  # 缩放到100x30像素
            self.rect = self.image.get_rect()
        else:
            self.image = None
            self.rect = pygame.Rect(0, 0, 60, 20)  # 设定一个默认hitbox

    def reset(self):
        self.x = WIDTH
        self.y = HEIGHT // 2
        self.active = False
        self.counter = 0
        self.delay = 0
        self.mode = 0  # 0 = warning, 1 = attack

    def activate(self):
        self.active = True
        self.counter = 0
        self.delay = 0
        self.x = WIDTH
        self.y = HEIGHT // 2
        self.mode = 0

    def update(self, player_y, paused, game_speed):
        if not self.active or paused:
            return

        if self.delay < 90:
            self.mode = 0
            self.delay += 1
            if self.y > player_y + 10:
                self.y -= 3
            else:
                self.y += 3
        else:
            self.mode = 1
            self.x -= 10 + game_speed

        if self.x < -50:
            self.reset()

    def draw(self, screen, font):
        if not self.active or not self.render or not self.image:
            return

        if self.mode == 0:
            pygame.draw.rect(screen, 'dark red', [self.x - 60, self.y - 25, 50, 50], 0, 5)
            screen.blit(font.render('!', True, 'black'), (self.x - 40, self.y - 20))
        else:
            screen.blit(self.image, (self.x, self.y - 10))

    def get_hitbox(self):
        """
        Returns an approximate collision box if active and in attack mode.
        """
        if not self.active or self.mode != 1:
            return None
        return pygame.Rect(self.x, self.y - 10, 100, 30)
