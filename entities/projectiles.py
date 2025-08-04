import pygame
from config.settings import WIDTH

class Projectile:
    def __init__(self, x, y, direction=1, speed=12):
        import pygame
        self.x = x
        self.y = y
        self.width = 10
        self.height = 5
        self.direction = direction
        self.speed = speed
        self.active = True
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.x += self.speed * self.direction
        self.rect.x = self.x
        self.rect.y = self.y
        # 失效判定等其它逻辑...

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(self.x, self.y, 10, 5))  # simple red rectangle as a projectile


    def collides_with(self, other):
        import pygame
        if hasattr(other, 'get_hitbox'):
            other_rect = other.get_hitbox()
        elif isinstance(other, pygame.Rect):
            other_rect = other
        else:
            raise ValueError(f"collides_with: invalid type {type(other)}")
        return self.rect.colliderect(other_rect)