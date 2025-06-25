import pygame
from config.settings import WIDTH

class Projectile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 10  # adjust as necessary
        self.active = True

    def update(self):
        if self.active:
            self.x += self.speed
            # Add logic to remove the projectile if it goes off-screen
            if self.x > WIDTH:
                self.active = False

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(self.x, self.y, 10, 5))  # simple red rectangle as a projectile


    def collides_with(self, other):
        # Ensure that self.x and self.y are numeric
        assert isinstance(self.x, (int, float)), f"self.x is not numeric: {self.x}"
        assert isinstance(self.y, (int, float)), f"self.y is not numeric: {self.y}"

        projectile_rect = pygame.Rect(self.x, self.y, 10, 5)  # Ensure that these dimensions are correct
        other_rect = other.get_hitbox()

        # Make sure that other_rect is a pygame.Rect with numeric values
        assert isinstance(other_rect, pygame.Rect), f"other_rect is not a pygame.Rect: {other_rect}"
        assert all(isinstance(value, (int, float)) for value in other_rect), f"other_rect values are not all numeric: {other_rect}"

        return projectile_rect.colliderect(other_rect)