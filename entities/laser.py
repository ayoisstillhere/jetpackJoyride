import random
from config.settings import WIDTH, HEIGHT

def generate_laser():
    laser_type = random.randint(0, 1)
    offset = random.randint(10, 300)
    if laser_type == 0:
        laser_width = random.randint(100, 300)
        laser_y = random.randint(100, HEIGHT - 100)
        new_laser = [[WIDTH + offset, laser_y], [WIDTH + offset + laser_width, laser_y]]
    else:
        laser_height = random.randint(100, 300)
        laser_y = random.randint(100, HEIGHT - 400)
        new_laser = [[WIDTH + offset, laser_y], [WIDTH + offset + laser_height, laser_y]]
    return new_laser