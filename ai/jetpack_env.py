import gymnasium as gym
from gymnasium import spaces
import numpy as np
from core.game import Game, GameStates
from config.settings import WIDTH, HEIGHT

class JetpackEnv(gym.Env):
    def __init__(self, render=False):
        super(JetpackEnv, self).__init__()
        self.game = Game(render=render)

        # Observation space: 16-dimensional vector
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(18,), dtype=np.float32)

        # Action space: y_movement [-1, 1], x_movement [-1, 1], shoot [0, 1]
        self.action_space = spaces.Box(low=np.array([-1.0, -1.0, 0.0]), high=np.array([1.0, 1.0, 1.0]), dtype=np.float32)

        self.frames_without_coin = 0
        self.max_frames_without_coin = 60
        self.total_shots_fired = 0
        self.total_deaths = 0
        self.total_coins = 0


    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.game._start_new_game()
        self.frames_without_coin = 0
        obs = self._get_obs()
        info = {}
        return obs, info


    def step(self, action):
        player = self.game.player
        player.controlled_by_ai = True

        # booster power (vertical)
        player.booster_power = np.clip(action[0], 0.0, 1.0)

        # horizontal movement (-1.0 to 1.0)
        player.move_speed = np.clip(action[1], -1.0, 1.0)

        # shoot
        shoot = action[2] >= 0.5
        shoot_success = False
        if shoot:
            proj = player.shoot()
            if proj:
                self.game.state.projectiles.append(proj)
                shoot_success = True
                self.total_shots_fired += 1

        coin_count_before = self.game.state.coin_count
        rocket_alive_before = self.game.rocket.active
        rocket_hitbox = self.game.rocket.get_hitbox() if self.game.rocket else None

        self.game._update_game_logic()

        obs = self._get_obs()
        reward = 0.0

        # === Coin reward ===
        coins_collected = self.game.state.coin_count - coin_count_before
        reward += coins_collected * 10.0

        # penalize inactivity (too many frames without coins)
        if coins_collected == 0:
            self.frames_without_coin += 1
        else:
            self.frames_without_coin = 0

        if self.frames_without_coin > self.max_frames_without_coin:
            reward -= 0.5
            self.frames_without_coin = 0 # reset after penalty

        # === Rocket shaping reward ===
        shaped_r = 0.0
        rocket_alive_after = self.game.rocket.active
        if rocket_alive_before and not rocket_alive_after:
            reward += 5.0  # destroyed rocket

        elif rocket_hitbox:
            # Incentivar mirar bem: quanto mais perto, maior reward incremental
            dist = np.hypot(rocket_hitbox.centerx - player.x, rocket_hitbox.centery - player.y)
            shaped_r = 0.05 / (dist + 1.0)
            reward += shaped_r

        if shoot_success and rocket_alive_after:
            reward -= 0.1  # penalize if it is shooting randomly

        # === Survival reward ===
        reward += 0.05

        # === Done check ===
        done = self.game.game_state == GameStates.GAME_OVER
        if done:
            reward -= 10.0
            self.total_deaths += 1
            self.total_coins += self.game.state.coin_count

        # === logs ===
        info = {
            "shots_fired": self.total_shots_fired,
            "coins_collected": self.game.state.coin_count,
            "deaths": self.total_deaths,
            "rocket_reward": shaped_r,
            "coins_reward": coins_collected * 10.0,
            "survival_reward": 0.05,
        }
        terminated = done
        truncated = False

        return obs, reward, terminated, truncated, info


    def _get_obs(self):
        player = self.game.player
        rocket_hitbox = self.game.rocket.get_hitbox() if self.game.rocket else None
        laser = self.game.laser_rect if hasattr(self.game, "laser_rect") and self.game.laser_rect else None
        coins = self.game.coins
        meteors = self.game.meteor_system.meteors if hasattr(self.game.meteor_system, "meteors") else []

        # === Find nearest coin by Euclidean distance ===
        nearest_coin = None
        min_dist = float("inf")
        for coin in coins:
            cx, cy = coin.rect.centerx, coin.rect.centery
            dist = np.hypot(cx - player.x, cy - player.y)
            if dist < min_dist:
                min_dist = dist
                nearest_coin = coin

        obs = np.zeros(18, dtype=np.float32)

        # Player y
        obs[0] = np.clip(player.y / HEIGHT, 0.0, 1.0)

        # Player velocity_y (normalized to [0, 1])
        obs[1] = np.clip(player.velocity_y / 20.0, -1.0, 1.0) * 0.5 + 0.5

        # Rocket
        if rocket_hitbox:
            obs[2] = np.clip(rocket_hitbox.centerx / WIDTH, 0.0, 1.0)
            obs[3] = np.clip(rocket_hitbox.centery / HEIGHT, 0.0, 1.0)
        else:
            obs[2] = 0.0
            obs[3] = 0.0

        # Laser
        if laser:
            obs[4] = np.clip(laser.centerx / WIDTH, 0.0, 1.0)
            obs[5] = np.clip(laser.centery / HEIGHT, 0.0, 1.0)
        else:
            obs[4] = 0.0
            obs[5] = 0.0

        # Nearest coin info
        if nearest_coin:
            obs[6] = np.clip(nearest_coin.rect.centerx / WIDTH, 0.0, 1.0)
            obs[7] = np.clip(nearest_coin.rect.centery / HEIGHT, 0.0, 1.0)

            # Relative normalized horizontal and vertical distances to coin
            dx = nearest_coin.rect.centerx - player.x
            dy = nearest_coin.rect.centery - player.y
            obs[8] = np.clip(dx / WIDTH, -1.0, 1.0)
            obs[9] = np.clip(dy / HEIGHT, -1.0, 1.0)
        else:
            obs[6] = 0.0
            obs[7] = 0.0
            obs[8] = 0.0
            obs[9] = 0.0

        # Game speed
        speed = self.game._get_speed() if hasattr(self.game, "_get_speed") else self.game.difficulty_system.game_speed
        obs[10] = np.clip(speed / 13.0, 0.0, 1.0)

        # Frames without coin
        obs[11] = np.clip(self.frames_without_coin / self.max_frames_without_coin, 0.0, 1.0)

        # Meteors: up to 3
        for i in range(3):
            if i < len(meteors):
                m = meteors[i].rect
                obs[12 + i * 2] = np.clip(m.centerx / WIDTH, 0.0, 1.0)
                obs[13 + i * 2] = np.clip(m.centery / HEIGHT, 0.0, 1.0)
            else:
                obs[12 + i * 2] = 0.0
                obs[13 + i * 2] = 0.0

        return obs


    def render(self, mode="human"):
        if self.game.render:
            self.game._draw_game_screen()