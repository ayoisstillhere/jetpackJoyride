import pygame
from config.settings import PLAYER_INIT_Y

class Player:
    def __init__(self, start_x=120, start_y=PLAYER_INIT_Y):
        self.x = start_x
        self.y = start_y
        self.width = 55
        self.height = 60
        self.velocity_y = 0
        self.gravity = 0.8
        self.counter = 0  # frame index control
        self.booster = False
        self.controlled_by_ai = False
        self.booster_duration = 0  # holding the space bar to jump
        self.max_booster_duration = 5

        # Carrega assets
        self.run_frames = [pygame.transform.scale(
            pygame.image.load(f"assets/run/run{i}.png").convert_alpha(), (self.width, self.height))
            for i in range(6)
        ]
        self.jump_up_img = pygame.transform.scale(
            pygame.image.load("assets/jump_up.png").convert_alpha(), (self.width, self.height)
        )
        self.jump_down_img = pygame.transform.scale(
            pygame.image.load("assets/jump_down.png").convert_alpha(), (self.width, self.height)
        )
        self.flame_img = pygame.transform.scale(
            pygame.image.load("assets/flame.png").convert_alpha(), (20, 30)
        )

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y + 10, self.width, self.height)

    def draw(self, screen):
        if self.y < PLAYER_INIT_Y:  # in the air
            if self.velocity_y < 0:  # going up
                if self.booster:
                    screen.blit(self.flame_img, (self.x + 15, self.y + self.height))
                screen.blit(self.jump_up_img, (self.x, self.y))
            else:  # falling
                screen.blit(self.jump_down_img, (self.x, self.y))
        else:  # running
            frame_index = (self.counter // 6) % len(self.run_frames)
            screen.blit(self.run_frames[frame_index], (self.x, self.y))

        return self.get_hitbox()

    def update_animation(self):
        self.counter = (self.counter + 1) % (6 * len(self.run_frames))

    def apply_gravity(self, boosting):
        self.booster = boosting
        if boosting:
            self.velocity_y -= self.gravity
        else:
            self.velocity_y += self.gravity

    def update_position(self, colliding_top, colliding_bottom):
        if (colliding_bottom and self.velocity_y > 0) or (colliding_top and self.velocity_y < 0):
            self.velocity_y = 0
        self.y += self.velocity_y

    def reset(self):
        self.y = PLAYER_INIT_Y
        self.velocity_y = 0
        self.counter = 0
        self.booster = False
        self.booster_duration = 0
