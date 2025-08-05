import pygame
import random
from config.settings import WIDTH, HEIGHT

class Laser:
    LASER_WIDTH = 200      # Width for horizontal lasers
    LASER_HEIGHT = 200     # Height for vertical lasers
    LASER_THICKNESS = 50   # Thickness of the laser beam

    def __init__(self, render=True):
        # Use floats
        self.points = self._generate()
        self.render = render

        if self.render:
            self.image = pygame.image.load('assets/Zapper1.png').convert_alpha()
            self.original_image = self.image.copy()
        else:
            self.image = None
            self.original_image = None

    def _generate(self):
        laser_type = random.randint(0, 1)
        offset = random.randint(10, 300)

        if laser_type == 0:  # horizontal
            y = random.randint(100, HEIGHT - 100)
            return [[float(WIDTH + offset), float(y)],
                    [float(WIDTH + offset + self.LASER_WIDTH), float(y)]]

        else:  # vertical
            y = random.randint(100, HEIGHT - 400)
            return [[float(WIDTH + offset), float(y)],
                    [float(WIDTH + offset), float(y + self.LASER_HEIGHT)]]

    def update(self, speed):
        self.points[0][0] -= speed
        self.points[1][0] -= speed

    def is_offscreen(self):
        return self.points[0][0] < 0 and self.points[1][0] < 0

    def _is_vertical(self):
        return self.points[0][1] != self.points[1][1]

    def get_hitbox(self):
        # Convert to int before creating the rectangle
        start_x = int(min(self.points[0][0], self.points[1][0]))
        start_y = int(min(self.points[0][1], self.points[1][1]))

        if self._is_vertical():
            return pygame.Rect(start_x, start_y, self.LASER_THICKNESS, self.LASER_HEIGHT)
        else:
            return pygame.Rect(start_x, start_y, self.LASER_WIDTH, self.LASER_THICKNESS)

    def draw(self, screen):
        if not self.render or not self.image:
            return

        # Ensure integer coordinates when drawing
        start_x = int(min(self.points[0][0], self.points[1][0]))
        start_y = int(min(self.points[0][1], self.points[1][1]))

        is_vertical = self._is_vertical()

        if is_vertical:
            scaled_image = pygame.transform.scale(
                self.original_image, (self.LASER_THICKNESS, self.LASER_HEIGHT))
            collision_rect = pygame.Rect(start_x, start_y,
                                         self.LASER_THICKNESS, self.LASER_HEIGHT)
        else:
            rotated_image = pygame.transform.rotate(self.original_image, 90)
            scaled_image = pygame.transform.scale(
                rotated_image, (self.LASER_WIDTH, self.LASER_THICKNESS))
            collision_rect = pygame.Rect(start_x, start_y,
                                         self.LASER_WIDTH, self.LASER_THICKNESS)

        screen.blit(scaled_image, (start_x, start_y))
        return collision_rect

    def reset(self):
        self.points = self._generate()
