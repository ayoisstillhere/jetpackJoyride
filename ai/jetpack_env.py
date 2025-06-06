import gym
from gym import spaces
import numpy as np
from core.game import Game, GameStates
from config.settings import WIDTH, HEIGHT

class JetpackEnv(gym.Env):
    def __init__(self, render=False):
        super(JetpackEnv, self).__init__()
        self.game = Game(render=render)

        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(10,), dtype=np.float32)

        # actions: 0 = wait, 1 = short jump, 2 = long jump
        self.action_space = spaces.Discrete(3)

    def reset(self):
        self.game._start_new_game()
        return self._get_obs()

    def step(self, action):
        self.game.player.controlled_by_ai = True
        self.game.player.booster = (action == 1)
        if action == 1:
            self.game.player.booster_duration = self.game.player.max_booster_duration

        coin_count_before = self.game.state.coin_count

        self.game._update_game_logic()

        obs = self._get_obs()
        reward = self._get_reward(coin_count_before)
        done = self.game.game_state == GameStates.GAME_OVER
        info = {}

        return obs, reward, done, info

    def render(self, mode="human"):
        if self.game.render:
            self.game._draw_game_screen()

    def _get_obs(self):
        player = self.game.player
        rocket = self.game.rocket.get_hitbox()
        laser = self.game.laser_rect
        coins = self.game.coins

        # closest coin
        nearest_coin = None
        for coin in coins:
            if coin.rect.x > player.x:
                nearest_coin = coin
                break

        obs = np.zeros(10, dtype=np.float32)

        # 0: vertical player position
        obs[0] = player.y / HEIGHT

        # 1: vertical player velocity
        obs[1] = np.clip(player.velocity_y / 20.0, -1.0, 1.0) * 0.5 + 0.5

        # 2–3: Rocket x, y
        if rocket:
            obs[2] = rocket.centerx / WIDTH
            obs[3] = rocket.centery / HEIGHT

        # 4–5: Laser x, y
        if laser:
            obs[4] = laser.centerx / WIDTH
            obs[5] = laser.centery / HEIGHT

        # 6–7: Coin x, y
        if nearest_coin:
            obs[6] = nearest_coin.rect.centerx / WIDTH
            obs[7] = nearest_coin.rect.centery / HEIGHT
        else:
            obs[6] = 0.0
            obs[7] = 0.0

        # 8: Game speed
        speed = self.game._get_speed() if hasattr(self.game, "_get_speed") else self.game.difficulty_system.game_speed
        obs[8] = min(speed / 13.0, 1.0)

        # 9: time without collecting coins
        obs[9] = min(self.frames_without_coin / self.max_frames_without_coin, 1.0)

        return obs

    def _get_reward(self, coin_count_before):
        reward = 1.0 # basic survival

        if self.game.state.coin_count > coin_count_before:
            reward += 5.0
            self.frames_without_coin = 0
        else:
            self.frames_without_coin += 1

        # penalization for inaction
        if self.frames_without_coin >= self.max_frames_without_coin:
            reward -= 2.0

        return reward