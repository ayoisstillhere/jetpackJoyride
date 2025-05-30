import pygame
import random
from config.settings import WIDTH, HEIGHT

class Laser:
    def __init__(self):
        self.points = self._generate()

    def _generate(self):
        laser_type = random.randint(0, 1)
        offset = random.randint(10, 300)

        if laser_type == 0:  # horizontal
            laser_width = random.randint(100, 300)
            y = random.randint(100, HEIGHT - 100)
            return [[WIDTH + offset, y], [WIDTH + offset + laser_width, y]]

        else:  # vertical
            laser_height = random.randint(100, 300)
            y = random.randint(100, HEIGHT - 400)
            return [[WIDTH + offset, y], [WIDTH + offset + laser_height, y]]

    def update(self, speed):
        self.points[0][0] -= speed
        self.points[1][0] -= speed

    def is_offscreen(self):
        return self.points[0][0] < 0 and self.points[1][0] < 0

    def draw(self, screen):
        pygame.draw.line(screen, 'yellow', self.points[0], self.points[1], 10)
        pygame.draw.circle(screen, 'yellow', self.points[0], 12)
        pygame.draw.circle(screen, 'yellow', self.points[1], 12)
        return pygame.Rect(
            min(self.points[0][0], self.points[1][0]),
            min(self.points[0][1], self.points[1][1]),
            abs(self.points[1][0] - self.points[0][0]),
            10  # height
        )

    def reset(self):
        """重置激光的位置和状态"""
        self.points = self._generate()
