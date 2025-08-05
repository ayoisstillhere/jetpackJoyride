import pygame
from config.settings import WIDTH

class Projectile:
    def __init__(self, x, y):
        # Store projectile position as float for smooth motion
        self.x = float(x)
        self.y = float(y)

        # Speed of projectile (pixels per frame)
        self.speed = 10

        # Status flag: True = active, False = should be removed
        self.active = True

    def update(self):
        """Move the projectile horizontally and deactivate if off-screen."""
        if self.active:
            self.x += self.speed
            # Deactivate projectile if it leaves the screen
            if self.x > WIDTH:
                self.active = False

    def draw(self, surface):
        """Draw the projectile as a small red rectangle."""
        if self.active:
            # Convert float to int to avoid pygame Surface.blit/draw errors
            pygame.draw.rect(surface, (255, 0, 0),
                             pygame.Rect(int(self.x), int(self.y), 10, 5))

    def get_hitbox(self):
        """Return a pygame.Rect representing the projectile's collision box."""
        return pygame.Rect(int(self.x), int(self.y), 10, 5)

    def collides_with(self, other):
        """
        Check collision with another object that implements get_hitbox().
        Returns True if the projectile collides with the other object.
        """
        projectile_rect = self.get_hitbox()
        other_rect = other.get_hitbox()
        return projectile_rect.colliderect(other_rect)
