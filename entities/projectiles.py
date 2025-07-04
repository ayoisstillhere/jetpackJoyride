import pygame
from config.settings import WIDTH

class Projectile:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.speed = 10
        self.active = True

    def update(self):
        if self.active:
            self.x += self.speed
            if self.x > WIDTH:
                self.active = False

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(int(self.x), int(self.y), 10, 5))

    def get_hitbox(self):
        return pygame.Rect(int(self.x), int(self.y), 10, 5)

    def collides_with(self, other):
        projectile_rect = self.get_hitbox()
        other_rect = other.get_hitbox()
        return projectile_rect.colliderect(other_rect)