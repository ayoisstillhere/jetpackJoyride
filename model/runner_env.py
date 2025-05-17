import gym
from gym import spaces
import numpy as np
import random

class RunnerEnv(gym.Env):
    def __init__(self):
        super(RunnerEnv, self).__init__()

        # 0: nothing ; 1: jump
        self.action_space = spaces.Discrete(2)

        # [dist_obst, height_obst, dist_coin, height_coin, speed_y, speed_x]
        self.observation_space = spaces.Box(low=-1.0, high=1.0, shape=(6,), dtype=np.float32)

        self.max_velocity = 10.0  # normalize vel_y
        self.max_speed_x = 0.05  # max scroll speed (obstacle speed)

        self.reset()

    def reset(self):
        self.player_y = 0.5
        self.player_vel_y = 0.0

        self.obstacle_x = 1.0
        self.obstacle_height = random.uniform(0.2, 0.8)

        self.coin_x = 1.2
        self.coin_height = random.uniform(0.2, 0.8)

        self.timestep = 0
        self.done = False

        return self._get_obs()

    def _get_obs(self):
        speed = self._get_scroll_speed()
        return np.array([
            self.obstacle_x,
            self.obstacle_height,
            self.coin_x,
            self.coin_height,
            np.clip(self.player_vel_y / self.max_velocity, -1.0, 1.0),
            np.clip(speed / self.max_scroll_speed, 0.0, 1.0)
        ], dtype=np.float32)

    def _get_scroll_speed(self):
        return min(0.02 + self.timestep * 0.00005, self.max_scroll_speed)

    def step(self, action):
        reward = 0.2  # survived one step
        self.timestep += 1

        if action: # jump?
            self.player_vel_y = 5.0
        else:
            reward -= 0.05  # stay quiet without collecting coins

        self.player_vel_y -= 0.5  # gravity
        self.player_y += self.player_vel_y / self.max_velocity
        self.player_y = np.clip(self.player_y, 0.0, 1.0)

        # moving obstacles horizontally
        speed = self._get_scroll_speed()
        self.obstacle_x -= speed
        self.coin_x -= speed

        if 0.0 < self.obstacle_x < 0.05: # collision
            if abs(self.player_y - self.obstacle_height) < 0.1:
                reward = -1.0
                self.done = True

        if 0.0 < self.coin_x < 0.05: # collect coin
            if abs(self.player_y - self.coin_height) < 0.1:
                reward += 1.0

                # change coin position
                self.coin_x = 1.2
                self.coin_height = random.uniform(0.2, 0.8)

        # reset coins/obstacles
        if self.obstacle_x < -0.1:
            self.obstacle_x = 1.0
            self.obstacle_height = random.uniform(0.2, 0.8)

        if self.coin_x < -0.1:
            self.coin_x = 1.2
            self.coin_height = random.uniform(0.2, 0.8)

        obs = self._get_obs()
        return obs, reward, self.done, {}