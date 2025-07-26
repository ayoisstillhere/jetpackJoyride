import pygame
import random
from config.settings import WIDTH, HEIGHT

class Laser:
    # Constants for laser dimensions - adjust these to get prefered size
    LASER_WIDTH = 200   # Width for horizontal lasers
    LASER_HEIGHT = 200  # Height for vertical lasers
    LASER_THICKNESS = 50  # Thickness of the laser beam

    def __init__(self, render=True, initial_spawn=False):
        self.initial_spawn = initial_spawn
        self.points = self._generate()
        self.render = render

        # Load the laser image
        if self.render:
            # Load the laser image only when rendering is enabled
            self.image = pygame.image.load('assets/Zapper1.png').convert_alpha()
            self.original_image = self.image.copy()
        else:
            self.image = None
            self.original_image = None

    def _generate(self):
        laser_type = random.randint(0, 1)
        
        if self.initial_spawn:
            offset = random.randint(WIDTH//2, WIDTH - 250) 
        else:
            offset = random.randint(10, 300)
            offset = WIDTH + offset

        if laser_type == 0:  # horizontal
            y = random.randint(100, HEIGHT - 100)
            if self.initial_spawn:
                return [[offset, y], [offset + self.LASER_WIDTH, y]]
            else:
                return [[offset, y], [offset + self.LASER_WIDTH, y]]

        else:  # vertical
            y = random.randint(100, HEIGHT - 400)
            if self.initial_spawn:
                return [[offset, y], [offset, y + self.LASER_HEIGHT]]
            else:
                return [[offset, y], [offset, y + self.LASER_HEIGHT]]

    def update(self, speed):
        self.points[0][0] -= speed
        self.points[1][0] -= speed

    def is_offscreen(self):
        return self.points[0][0] < 0 and self.points[1][0] < 0

    def _is_vertical(self):
        """Check if the laser is vertical based on points"""
        return self.points[0][1] != self.points[1][1]

    def draw(self, screen):
        if not self.render or not self.image:
            return
        # Calculate laser properties
        start_x = min(self.points[0][0], self.points[1][0])
        start_y = min(self.points[0][1], self.points[1][1])

        # Determine if laser is vertical or horizontal
        is_vertical = self._is_vertical()

        if is_vertical:
            scaled_image = pygame.transform.scale(self.original_image, (self.LASER_THICKNESS, self.LASER_HEIGHT))
            collision_rect = pygame.Rect(start_x, start_y, self.LASER_THICKNESS, self.LASER_HEIGHT)
        else:
            rotated_image = pygame.transform.rotate(self.original_image, 90)
            scaled_image = pygame.transform.scale(rotated_image, (self.LASER_WIDTH, self.LASER_THICKNESS))
            collision_rect = pygame.Rect(start_x, start_y, self.LASER_WIDTH, self.LASER_THICKNESS)

        # Draw the scaled image
        screen.blit(scaled_image, (start_x, start_y))

        # Return collision rectangle
        return collision_rect

    def reset(self):
        self.points = self._generate()

    def get_hitbox(self):
        # Calculate current laser collision rectangle
        start_x = min(self.points[0][0], self.points[1][0])
        start_y = min(self.points[0][1], self.points[1][1])
        if self._is_vertical():
            return pygame.Rect(start_x, start_y, self.LASER_THICKNESS, self.LASER_HEIGHT)
        else:
            return pygame.Rect(start_x, start_y, self.LASER_WIDTH, self.LASER_THICKNESS)