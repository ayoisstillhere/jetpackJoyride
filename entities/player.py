import pygame
import time
from config.settings import PLAYER_INIT_Y, WIDTH
from entities.projectiles import Projectile

class Player:
    def __init__(self, start_x=120, start_y=PLAYER_INIT_Y, character_type="boy", render=True):
        self.x = start_x
        self.y = start_y
        self.width = 48
        self.height = 60
        self.velocity_y = 0
        self.gravity = 0.4
        self.counter = 0  # frame index control

        # Continuous control variables
        self.booster_power = 0.0   # 0.0 to 1.0
        self.move_speed = 0.0      # -1.0 (left) to 1.0 (right)

        self.booster_strength = 2.0          # Tunable: controls vertical boost force
        self.max_horizontal_speed = 5.0      # Tunable: max horizontal speed

        self.controlled_by_ai = False

        self.character_type = character_type
        self.can_shoot = True
        self.shoot_cooldown = 0.5
        self.last_shot_time = 0

        if render:
            self.run_frames = [
                pygame.transform.scale(
                    pygame.image.load(f"assets/{character_type}/run/{i}.PNG").convert_alpha(),
                    (self.width, self.height)
                )
                for i in range(1, 7)
            ]
            self.jump_up_img = pygame.transform.scale(
                pygame.image.load(f"assets/{character_type}/jump_up.PNG").convert_alpha(),
                (self.width, self.height)
            )
            self.jump_down_img = pygame.transform.scale(
                pygame.image.load(f"assets/{character_type}/jump_down.PNG").convert_alpha(),
                (self.width, self.height)
            )
            self.flame_img = pygame.transform.scale(
                pygame.image.load("assets/flame.png").convert_alpha(), (20, 30)
            )
        else:
            self.run_frames = [None] * 6
            self.jump_up_img = None
            self.jump_down_img = None
            self.flame_img = None

    def shoot(self):
        current_time = time.time()
        if self.can_shoot and current_time - self.last_shot_time > self.shoot_cooldown:
            self.last_shot_time = current_time
            return Projectile(self.x, self.y)
        return None

    def change_character(self, character_type):
        self.character_type = character_type
        self.run_frames = [
            pygame.transform.scale(
                pygame.image.load(f"assets/{character_type}/run/{i}.PNG").convert_alpha(),
                (self.width, self.height)
            )
            for i in range(1, 7)
        ]
        self.jump_up_img = pygame.transform.scale(
            pygame.image.load(f"assets/{character_type}/jump_up.PNG").convert_alpha(), (self.width, self.height)
        )
        self.jump_down_img = pygame.transform.scale(
            pygame.image.load(f"assets/{character_type}/jump_down.PNG").convert_alpha(), (self.width, self.height)
        )

    def get_hitbox(self):
        return pygame.Rect(int(self.x), int(self.y + 5), int(self.width), int(self.height))

    def draw(self, screen, paused=False):
        if paused:
            img = self.jump_up_img if self.velocity_y < 0 else self.jump_down_img
            screen.blit(img, (self.x, self.y))
        else:
            if self.y < PLAYER_INIT_Y:
                if self.velocity_y < 0:
                    if self.booster_power > 0.05:
                        screen.blit(self.flame_img, (self.x + 15, self.y + self.height))
                    screen.blit(self.jump_up_img, (self.x, self.y))
                else:
                    screen.blit(self.jump_down_img, (self.x, self.y))
            else:
                frame_index = (self.counter // 6) % len(self.run_frames)
                screen.blit(self.run_frames[frame_index], (self.x, self.y))

        return self.get_hitbox()

    def update_animation(self):
        self.counter = (self.counter + 1) % (6 * len(self.run_frames))

    def update_position(self, colliding_top, colliding_bottom):
        # --- Vertical boost ---
        if self.booster_power > 0.05:
            self.velocity_y -= self.booster_power * self.booster_strength

        # Apply gravity
        self.velocity_y += self.gravity

        # Clamp vertical speed (optional)
        self.velocity_y = max(min(self.velocity_y, 10), -10)

        # Apply vertical position
        if (colliding_bottom and self.velocity_y > 0) or (colliding_top and self.velocity_y < 0):
            self.velocity_y = 0
        self.y += self.velocity_y

        # --- Horizontal movement ---
        self.x += self.move_speed * self.max_horizontal_speed

        # Clamp horizontal boundaries
        if self.x < 0:
            self.x = 0
        elif self.x > WIDTH - self.width:
            self.x = WIDTH - self.width

    def reset(self):
        self.y = PLAYER_INIT_Y
        self.velocity_y = 0
        self.counter = 0
        self.booster_power = 0.0
        self.move_speed = 0.0
