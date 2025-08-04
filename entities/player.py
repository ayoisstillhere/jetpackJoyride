import pygame
import time
from config.settings import PLAYER_INIT_Y, WIDTH
from entities.projectiles import Projectile

class Player:
    def __init__(self, start_x=120, start_y=PLAYER_INIT_Y, character_type="boy", render=True):
        # 三车道x坐标
        from config.settings import WIDTH
        self.lane_positions = [int(WIDTH * 0.3), int(WIDTH * 0.5), int(WIDTH * 0.7)]
        self.lane = 1  # 0=左, 1=中, 2=右
        self.x = self.lane_positions[self.lane]
        self.y = start_y
        self.width = 48
        self.height = 60
        self.velocity_y = 0
        self.gravity = 0.09
        self.counter = 0  # frame index control
        self.booster = False
        self.controlled_by_ai = False
        self.booster_duration = 0  # holding the space bar to jump
        self.max_booster_duration = 5
        self.character_type = character_type
        self.move_left = False
        self.move_right = False
        self.height = 60
        self.horizontal_speed = 5  # 不再直接用
        self.can_shoot = True
        self.velocity_y = 0
        self.jump_count = 0
        self.max_jumps = 2  # 二连跳
        self.jump_power = 8  # 跳跃初速度，降低高度
        self.shoot_cooldown = 0.5  # 0.5 seconds cooldown
        self.last_shot_time = 0

        # Load assets based on character type
        # All characters use the same naming convention (1.PNG, 2.PNG, etc.)
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
            return Projectile(self.x, self.y)  # Adjust starting position as needed
        return None

    def change_character(self, character_type):
        """Change the character type and reload assets"""
        self.character_type = character_type
        # All characters use the same naming convention (1.PNG, 2.PNG, etc.)
        self.run_frames = [pygame.transform.scale(
            pygame.image.load(f"assets/{character_type}/run/{i}.PNG").convert_alpha(), (self.width, self.height))
            for i in range(1, 7)  # Load frames 1 through 6
        ]
        self.jump_up_img = pygame.transform.scale(
            pygame.image.load(f"assets/{character_type}/jump_up.PNG").convert_alpha(), (self.width, self.height)
        )
        self.jump_down_img = pygame.transform.scale(
            pygame.image.load(f"assets/{character_type}/jump_down.PNG").convert_alpha(), (self.width, self.height)
        )

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y + 5, self.width, self.height)

    def draw(self, screen, paused=False):
        if paused:  # When paused, show static image
            if self.y < PLAYER_INIT_Y:  # in the air
                if self.velocity_y < 0:  # going up
                    if self.booster:
                        screen.blit(self.flame_img, (self.x + 15, self.y + self.height))
                    screen.blit(self.jump_up_img, (self.x, self.y))
                else:  # falling
                    screen.blit(self.jump_down_img, (self.x, self.y))
            else:  # on ground
                screen.blit(self.run_frames[0], (self.x, self.y))  # Use first frame
        else:  # Normal animation
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

    def jump(self):
        if self.jump_count < self.max_jumps:
            self.velocity_y = -self.jump_power
            self.jump_count += 1

    def update_position(self, colliding_top, colliding_bottom):
        # 只处理车道切换，y坐标和velocity_y交给物理系统
        if self.move_left:
            if self.lane > 0:
                self.lane -= 1
                self.x = self.lane_positions[self.lane]
            self.move_left = False  # 只切换一次
        if self.move_right:
            if self.lane < 2:
                self.lane += 1
                self.x = self.lane_positions[self.lane]
            self.move_right = False  # 只切换一次
        # 落地时重置跳跃计数
        from config.settings import HEIGHT
        ground_y = HEIGHT - 50 - self.height
        if abs(self.y - ground_y) < 2 and self.velocity_y >= 0:
            self.jump_count = 0

    def reset(self):
        from config.settings import HEIGHT
        self.lane = 1  # 中间
        self.x = self.lane_positions[self.lane]
        self.y = HEIGHT - self.height  # 地面高度
        self.velocity_y = 0
        self.counter = 0
        self.booster = False
        self.booster_duration = 0
        self.move_left = False
        self.move_right = False
