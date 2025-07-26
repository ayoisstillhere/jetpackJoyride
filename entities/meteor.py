import pygame
import random
from config.settings import WIDTH, HEIGHT

class Meteor:
    def __init__(self, x=None, y=None, player_x=None):
        # Position - if player_x is specified, spawn near the player's overhead
        if player_x is not None:
            offset_range = 100  # Left and right offset range
            self.x = player_x + random.randint(-offset_range, offset_range)
            # Ensure it doesn't exceed screen boundaries
            self.x = max(50, min(WIDTH - 50, self.x))
        else:
            self.x = x if x is not None else random.randint(50, WIDTH - 50)
        
        self.y = y if y is not None else -50  # Start above screen

        # Physics
        self.fall_speed = random.uniform(2, 4)
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5) 

        # Visual properties
        self.size = random.randint(30, 60)  # Random size for variety
        self.color = random.choice([
            (101, 67, 33),   # Brown
            (139, 69, 19),   # Saddle brown
            (160, 82, 45),   # Saddle brown lighter
            (105, 105, 105), # Dim gray
            (128, 128, 128)  # Gray
        ])

        # Collision
        self.rect = pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)

        # Status
        self.active = True

        # Trail effect (optional)
        self.trail_positions = []
        self.max_trail_length = 5

    def update(self, paused=False, game_speed=1):
        """Update meteor position and rotation"""
        if paused:
            return

        # Update position
        self.y += self.fall_speed * game_speed

        # Update rotation for tumbling effect
        self.rotation += self.rotation_speed
        if self.rotation >= 360:
            self.rotation -= 360
        elif self.rotation < 0:
            self.rotation += 360

        # Update collision rect
        self.rect.x = self.x - self.size//2
        self.rect.y = self.y - self.size//2

        # Update trail
        self.trail_positions.append((self.x, self.y))
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)

        # Check if meteor is off-screen
        if self.y > HEIGHT + 100:
            self.active = False

    def draw(self, screen):
        """Draw the meteor with visual effects"""
        if not self.active:
            return

        # Draw trail (fading effect)
        for i, (trail_x, trail_y) in enumerate(self.trail_positions[:-1]):
            alpha = int(255 * (i + 1) / len(self.trail_positions) * 0.3)
            trail_size = int(self.size * 0.7 * (i + 1) / len(self.trail_positions))
            trail_color = (*self.color, alpha)

            # Create surface for alpha blending
            trail_surface = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, trail_color, (trail_size, trail_size), trail_size)
            screen.blit(trail_surface, (trail_x - trail_size, trail_y - trail_size))

        # Draw main meteor body
        meteor_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)

        # Draw meteor layers for depth
        # Outer shadow
        pygame.draw.circle(meteor_surface, (50, 50, 50), (self.size, self.size), self.size)
        # Main body
        pygame.draw.circle(meteor_surface, self.color, (self.size, self.size), self.size - 2)
        # Highlight
        highlight_color = tuple(min(255, c + 40) for c in self.color)
        pygame.draw.circle(meteor_surface, highlight_color, (self.size - 8, self.size - 8), self.size // 3)

        # Add cracks/texture
        self._draw_cracks(meteor_surface)

        # Rotate the meteor surface
        if self.rotation != 0:
            meteor_surface = pygame.transform.rotate(meteor_surface, self.rotation)

        # Get the rect of the rotated surface and center it
        rotated_rect = meteor_surface.get_rect(center=(self.x, self.y))
        screen.blit(meteor_surface, rotated_rect)

        # Optional: Draw collision rect for debugging
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

    def _draw_cracks(self, surface):
        """Draw cracks on the meteor for realistic appearance"""
        crack_color = tuple(max(0, c - 30) for c in self.color)

        # Draw some random cracks
        for _ in range(3):
            start_x = random.randint(self.size//4, 3*self.size//4)
            start_y = random.randint(self.size//4, 3*self.size//4)
            end_x = start_x + random.randint(-self.size//3, self.size//3)
            end_y = start_y + random.randint(-self.size//3, self.size//3)

            pygame.draw.line(surface, crack_color, (start_x, start_y), (end_x, end_y), 2)

    def get_hitbox(self):
        """Return collision rectangle"""
        return self.rect

    def collides_with(self, other_rect):
        """Check collision with another rectangle"""
        return self.rect.colliderect(other_rect)

    def is_offscreen(self):
        """Check if meteor is completely off-screen"""
        return self.y > HEIGHT + 100