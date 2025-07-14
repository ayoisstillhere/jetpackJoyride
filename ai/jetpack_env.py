import gymnasium as gym
from gymnasium import spaces
import numpy as np
from core.game import Game, GameStates
from config.settings import WIDTH, HEIGHT

class JetpackEnv(gym.Env):
    def __init__(self, render=False, curriculum_stage=3):
        super(JetpackEnv, self).__init__()
        self.curriculum_stage = curriculum_stage
        self.render = render
        self.game = Game(render=render)

        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(29,), dtype=np.float32)

        # actions: [前进, 后退, 跳, 射击]，可组合，0/1分别表示不激活/激活
        self.action_space = spaces.MultiBinary(4)

        self.frames_without_coin = 0
        self.max_frames_without_coin = 500
        self.last_distance = 0  # 新增：记录上一次距离
        self.frames_not_on_ground = 0  # 连续不在地面帧数
        self.frames_not_on_ceiling = 0  # 连续不在顶部帧数

    def reset(self, *, seed=None, options=None):
        if seed is not None:
            self.np_random, _ = gym.utils.seeding.np_random(seed)
        self.game._start_new_game()
        # 新增：设置课程阶段
        if hasattr(self.game, 'set_curriculum_stage'):
            self.game.set_curriculum_stage(self.curriculum_stage)
        self.last_distance = 0  # 重置距离
        self.frames_not_on_ground = 0
        self.frames_not_on_ceiling = 0
        obs = self._get_obs()
        info = {}
        return obs, info

    def step(self, action):
        self.game.player.controlled_by_ai = True
        # 先重置所有动作
        self.game.player.move_left = False
        self.game.player.move_right = False
        self.game.player.booster = False
        self.fired_this_step = False # 是否发射子弹

        # 解析组合动作
        move_right, move_left, booster, shoot = action
        # 判断玩家是否在地面和顶部
        on_ground = getattr(self.game, 'bot_hit', False)
        on_ceiling = getattr(self.game, 'top_hit', False)
        # 统计连续不在地面/顶部的帧数
        if on_ground:
            self.frames_not_on_ground = 0
        else:
            self.frames_not_on_ground += 1
        if on_ceiling:
            self.frames_not_on_ceiling = 0
        else:
            self.frames_not_on_ceiling += 1
        # 只有在地面时才能前后移动
        if on_ground:
            if move_right:
                self.game.player.move_right = True
            if move_left:
                self.game.player.move_left = True
        # 跳（喷气）任何时候都可
        if booster:
            self.game.player.booster = True
            self.game.player.booster_duration = 2  # 每次只持续1个step
        # 射击任何时候都可
        if shoot:
            projectile = self.game.player.shoot()
            if projectile:
                self.game.state.projectiles.append(projectile)
                self.fired_this_step = True

        coin_count_before = self.game.state.coin_count

        # 训练时自动渲染，便于调试（提前到逻辑更新前）
        if self.game.render:
            self.game._draw_game_screen()
            if self.game.screen:
                import pygame
                pygame.display.flip()

        self.game._update_game_logic()

        # 计算本帧走过的距离
        distance_delta = self.game.state.distance - self.last_distance
        self.last_distance = self.game.state.distance
        obs = self._get_obs(on_ground=on_ground, on_ceiling=on_ceiling)
        reward = self._get_reward(coin_count_before, distance_delta, shoot)
        terminated = self.game.game_state == GameStates.GAME_OVER
        truncated = False  # 可根据需要设置截断条件
        info = {}

        return obs, reward, terminated, truncated, info

    def render(self, mode="human"):
        if self.game.render:
            self.game._draw_game_screen()

    def _get_obs(self, on_ground=None, on_ceiling=None):
        obs = np.zeros(29, dtype=np.float32)
        if on_ground is None:
            on_ground = getattr(self.game, 'bot_hit', False)
        if on_ceiling is None:
            on_ceiling = getattr(self.game, 'top_hit', False)
        if self.game.render and hasattr(self.game, 'screen') and self.game.screen:
            width = self.game.screen.get_width()
            height = self.game.screen.get_height()
        else:
            from config.settings import WIDTH as width, HEIGHT as height

        # 玩家
        player = getattr(self.game, 'player', None)
        obs[0] = player.x / width if player else 0.0
        obs[1] = player.y / height if player else 0.0
        obs[2] = np.clip(player.velocity_y / 20.0, -1.0, 1.0) * 0.5 + 0.5 if player else 0.0
        # 玩家hitbox
        player_box = player.get_hitbox() if player and hasattr(player, 'get_hitbox') else None
        if player_box:
            obs[23] = player_box.left / width
            obs[24] = player_box.right / width
            obs[25] = player_box.top / height
            obs[26] = player_box.bottom / height
        else:
            obs[23:27] = 0.0

        # 火箭
        rocket = getattr(self.game, 'rocket', None)
        rocket_box = rocket.get_hitbox() if rocket and hasattr(rocket, 'get_hitbox') else None
        if rocket_box:
            obs[3] = rocket_box.left / width
            obs[4] = rocket_box.right / width
            obs[5] = rocket_box.top / height
            obs[6] = rocket_box.bottom / height
        else:
            obs[3:7] = 0.0

        # 激光
        laser = getattr(self.game, 'laser', None)
        laser_box = laser.get_hitbox() if laser and hasattr(laser, 'get_hitbox') else None
        if laser_box:
            obs[7] = laser_box.left / width
            obs[8] = laser_box.right / width
            obs[9] = laser_box.top / height
            obs[10] = laser_box.bottom / height
        else:
            obs[7:11] = 0.0

        # 最近金币
        coins = getattr(self.game, 'coins', [])
        nearest_coin = None
        if coins and player:
            for coin in coins:
                if coin.rect.x > player.x:
                    nearest_coin = coin
                    break
        if nearest_coin:
            obs[11] = nearest_coin.rect.left / width
            obs[12] = nearest_coin.rect.right / width
            obs[13] = nearest_coin.rect.top / height
            obs[14] = nearest_coin.rect.bottom / height
        else:
            obs[11:15] = 0.0

        # 游戏速度
        speed = self.game._get_speed() if hasattr(self.game, "_get_speed") else self.game.difficulty_system.game_speed
        obs[15] = min(speed / 13.0, 1.0)

        # 没捡到金币的归一化帧数
        obs[16] = min(self.frames_without_coin / self.max_frames_without_coin, 1.0)

        # 火箭预警信息
        rocket_obj = rocket
        obs[17] = 1.0 if rocket_obj and rocket_obj.active and getattr(rocket_obj, 'mode', 1) == 0 else 0.0
        obs[18] = (rocket_obj.y / height) if (rocket_obj and rocket_obj.active and getattr(rocket_obj, 'mode', 1) == 0) else 0.0

        # 陨石
        meteor_system = getattr(self.game, 'meteor_system', None)
        meteor_obj = meteor_system.meteors[0] if meteor_system and hasattr(meteor_system, 'meteors') and meteor_system.meteors else None
        meteor_box = meteor_obj.get_hitbox() if meteor_obj and hasattr(meteor_obj, 'get_hitbox') else None
        if meteor_box:
            obs[19] = meteor_box.left / width
            obs[20] = meteor_box.right / width
            obs[21] = meteor_box.top / height
            obs[22] = meteor_box.bottom / height
        else:
            obs[19:23] = 0.0

        # obs[27]: 是否在地面, obs[28]: 是否在顶部
        obs[27] = float(on_ground)
        obs[28] = float(on_ceiling)
        return obs

    def _get_reward(self, coin_count_before, distance_delta, shoot):
        reward = 0.0

        # 1. 金币奖励（最高权重）
        if self.game.state.coin_count > coin_count_before:
            reward += 2.0
            self.frames_without_coin = 0
        else:
            self.frames_without_coin += 1

        # 2. 生存奖励（每帧少量）
        reward += 0.05

        # 3. 距离奖励（每前进一步有微小奖励）
        reward += distance_delta * 0.005

        # 4. 太久没捡到金币惩罚
        if self.frames_without_coin >= self.max_frames_without_coin:
            reward -= 0.5

        # 5. 命中火箭奖励（适中）
        if self.fired_this_step:
            reward += 0.5
        # 6. 射击但没命中惩罚（较大）
        elif shoot:
            reward -= 0.2

        # 7. 死亡大惩罚
        if self.game.game_state == GameStates.GAME_OVER:
            reward -= 2.0

        # 8. 归一化奖励（限制在[-2, 2]）
        reward = max(min(reward, 2.0), -2.0)
        return reward