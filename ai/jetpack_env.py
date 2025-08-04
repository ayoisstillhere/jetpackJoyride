import gymnasium as gym
from gymnasium import spaces
import numpy as np
from core.game import Game, GameStates
from config.settings import WIDTH, HEIGHT

class JetpackEnv(gym.Env):
    def __init__(self, render=False, curriculum_stage=0):
        super(JetpackEnv, self).__init__()
        self.render = render
        self.curriculum_stage = curriculum_stage
        self.game = Game(render=render)
        # 观测空间：[玩家车道, 玩家y, 最近金币车道, 最近金币y, 最近陨石车道, 最近陨石y, 火箭x, 火箭y, 子弹x, 子弹y]
        self.observation_space = spaces.Box(low=0, high=1, shape=(10,), dtype=np.float32)
        # 动作空间：[左, 右, 跳, 射击]
        self.action_space = spaces.MultiBinary(4)
        self.last_distance = 0
        self.frames_without_coin = 0
        self.max_frames_without_coin = 300

    def reset(self, *, seed=None, options=None):
        if seed is not None:
            self.np_random, _ = gym.utils.seeding.np_random(seed)
        self.game._start_new_game()
        self.last_distance = 0
        self.frames_without_coin = 0
        obs = self._get_obs()
        info = {}
        return obs, info

    def step(self, action):
        self.game.player.controlled_by_ai = True
        # 先重置所有动作
        self.game.player.move_left = False
        self.game.player.move_right = False
        fired_this_step = False
        left, right, jump, shoot = action
        # 课程训练阶段控制
        # 1=只训练射击，2=只训练躲陨石，3=只训练吃金币，0=全目标
        if self.curriculum_stage == 1:
            # 只允许射击，其他动作全部屏蔽
            left = 0
            right = 0
            jump = 0
            # 只激活火箭
            self.game.rocket.active = True
            self.game.meteor_system.meteors.clear()
            self.game.coins.clear()
        elif self.curriculum_stage == 2:
            # 禁止射击
            shoot = 0
            # 只激活陨石
            self.game.rocket.active = False
            self.game.coins.clear()
        elif self.curriculum_stage == 3:
            # 禁止射击
            shoot = 0
            # 只激活金币
            self.game.rocket.active = False
            self.game.meteor_system.meteors.clear()
        # 左右切换车道
        if left:
            self.game.player.move_left = True
        if right:
            self.game.player.move_right = True
        # 跳跃
        if jump:
            self.game.player.jump()
        # 射击
        if shoot:
            projectile = self.game.player.shoot()
            if projectile:
                self.game.state.projectiles.append(projectile)
                fired_this_step = True
        coin_count_before = self.game.state.coin_count
        if self.game.render:
            self.game._draw_game_screen()
            if self.game.screen:
                import pygame
                pygame.display.flip()
        self.game._update_game_logic()
        obs = self._get_obs()
        reward = self._get_reward(coin_count_before, fired_this_step)
        terminated = self.game.game_state == GameStates.GAME_OVER
        truncated = False
        info = {}
        return obs, reward, terminated, truncated, info

    def render(self, mode="human"):
        if self.game.render:
            self.game._draw_game_screen()

    def _get_obs(self):
        obs = np.zeros(10, dtype=np.float32)
        player = getattr(self.game, 'player', None)
        # 玩家车道（归一化到[0,1,2]->[0,1]）
        obs[0] = player.lane / 2 if player else 0
        obs[1] = np.clip(player.y / HEIGHT, 0, 1) if player else 0
        # 最近金币
        coins = getattr(self.game, 'coins', [])
        nearest_coin = None
        if coins and player:
            min_dist = float('inf')
            for coin in coins:
                dist = abs(coin.y - player.y) + abs(coin.x - player.x)
                if dist < min_dist:
                    min_dist = dist
                    nearest_coin = coin
        if nearest_coin:
            # 车道归一化
            coin_lane = 0
            lane_positions = [int(WIDTH * 0.3), int(WIDTH * 0.5), int(WIDTH * 0.7)]
            for i, pos in enumerate(lane_positions):
                if abs(nearest_coin.x - pos) < 5:
                    coin_lane = i
            obs[2] = coin_lane / 2
            obs[3] = np.clip(nearest_coin.y / HEIGHT, 0, 1)
        # 最近陨石
        meteor_system = getattr(self.game, 'meteor_system', None)
        meteors = meteor_system.meteors if meteor_system and hasattr(meteor_system, 'meteors') else []
        nearest_meteor = None
        if meteors and player:
            min_dist = float('inf')
            for meteor in meteors:
                dist = abs(meteor.y - player.y) + abs(meteor.x - player.x)
                if dist < min_dist:
                    min_dist = dist
                    nearest_meteor = meteor
        if nearest_meteor:
            meteor_lane = 0
            lane_positions = [int(WIDTH * 0.3), int(WIDTH * 0.5), int(WIDTH * 0.7)]
            for i, pos in enumerate(lane_positions):
                if abs(nearest_meteor.x - pos) < 5:
                    meteor_lane = i
            obs[4] = meteor_lane / 2
            obs[5] = np.clip(nearest_meteor.y / HEIGHT, 0, 1)
        # 火箭
        rocket = getattr(self.game, 'rocket', None)
        if rocket and rocket.active:
            obs[6] = np.clip(rocket.x / WIDTH, 0, 1)
            obs[7] = np.clip(rocket.y / HEIGHT, 0, 1)
        # 子弹（只取第一个）
        projectiles = getattr(self.game.state, 'projectiles', [])
        if projectiles:
            obs[8] = np.clip(projectiles[0].x / WIDTH, 0, 1)
            obs[9] = np.clip(projectiles[0].y / HEIGHT, 0, 1)
        return obs

    def _get_reward(self, coin_count_before, fired_this_step):
        reward = 0.0
        # 课程训练阶段控制奖励
        # 1=只训练射击，2=只训练躲陨石，3=只训练吃金币，0=全目标
        if self.curriculum_stage == 1:
            # 只奖励射击火箭
            rocket = getattr(self.game, 'rocket', None)
            rocket_box = rocket.get_hitbox() if rocket and hasattr(rocket, 'get_hitbox') else None
            rocket_hit = False
            if fired_this_step and rocket and rocket.active and rocket_box is not None:
                for projectile in self.game.state.projectiles:
                    if projectile.collides_with(rocket_box):
                        rocket_hit = True
                        break
            if fired_this_step and rocket_hit:
                reward += 5.0
            elif fired_this_step:
                reward -= 1.0
            reward += 0.05  # 存活奖励（提升）
            if self.game.game_state == GameStates.GAME_OVER:
                reward -= 20.0
            reward = np.clip(reward, -20.0, 10.0)
            return reward
        elif self.curriculum_stage == 2:
            # 只奖励存活，死亡惩罚
            reward += 0.1  # 存活奖励（提升）
            if self.game.game_state == GameStates.GAME_OVER:
                reward -= 20.0
            reward = np.clip(reward, -20.0, 10.0)
            return reward
        elif self.curriculum_stage == 3:
            # 只奖励吃金币
            if self.game.state.coin_count > coin_count_before:
                reward += 5.0
                self.frames_without_coin = 0
            else:
                self.frames_without_coin += 1
            reward += 0.05  # 存活奖励（提升）
            if self.frames_without_coin >= self.max_frames_without_coin:
                reward -= 1.0
            if self.game.game_state == GameStates.GAME_OVER:
                reward -= 20.0
            reward = np.clip(reward, -20.0, 10.0)
            return reward
        # 全目标综合奖励
        # 吃到金币奖励
        if self.game.state.coin_count > coin_count_before:
            reward += 5.0
            self.frames_without_coin = 0
        else:
            self.frames_without_coin += 1
        # 存活奖励
        reward += 0.1  # 存活奖励（提升）
        # 太久没吃到金币惩罚
        if self.frames_without_coin >= self.max_frames_without_coin:
            reward -= 1.0
        # 击中火箭奖励/乱射惩罚
        rocket = getattr(self.game, 'rocket', None)
        rocket_box = rocket.get_hitbox() if rocket and hasattr(rocket, 'get_hitbox') else None
        rocket_hit = False
        if fired_this_step and rocket and rocket.active and rocket_box is not None:
            for projectile in self.game.state.projectiles:
                if projectile.collides_with(rocket_box):
                    rocket_hit = True
                    break
        if fired_this_step and rocket_hit:
            reward += 5.0
        elif fired_this_step:
            reward -= 1.0
        # 死亡惩罚
        if self.game.game_state == GameStates.GAME_OVER:
            reward -= 20.0
        # 奖励归一化
        reward = np.clip(reward, -20.0, 10.0)
        return reward