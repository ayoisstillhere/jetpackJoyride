import random
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from core.game import Game, GameStates
from entities.coin import spawn_coins
import config.settings as config

class JetpackEnv(gym.Env):
    """
    Custom Gymnasium environment for a Jetpack Joyride-like game.

    This environment implements curriculum learning with progressive stages:
    - Stage 0: Only coins
    - Stage 1: Coins + meteors
    - Stage 2: Coins + meteors + lasers
    - Stage 3: All (meteors, lasers, rockets, and shooting)
    """
    def __init__(self, render=False, mode="progressive"):
        """
        Initialize the Jetpack environment.

        Args:
            render (bool): Whether to render the game screen.
            mode (str): Training mode. "progressive" enables curriculum learning.
        """
        super(JetpackEnv, self).__init__()
        self.mode = mode
        self.game = Game(render=render, mode=mode)

        # Curriculum
        self.curriculum_stage = 0
        self.fixed_stage = -1  # means dynamic stage based on steps
        self.steps_done = 0
        self.stage_thresholds = [0, 50000, 200000, 400000] # to a 700k (default) total timesteps

        # Observation space
        # Format: 11-dimensional vector
        # [x, y, vy, dx_coin, dy_coin, dx_rocket, dy_rocket,
        #  dx_laser, dy_laser, dx_meteor, dy_meteor, rocket_mode_flag]
        self.observation_space = spaces.Box(
            low=np.array([0.0, 0.0, 0.0] + [-1.0, -1.0]*4 + [0.0], dtype=np.float32),
            high=np.array([1.0, 1.0, 1.0] + [ 1.0,  1.0]*4 + [1.0], dtype=np.float32),
            dtype=np.float32
        )

        # Action space: [booster_power, lateral_move_speed, shoot]
        self.action_space = spaces.Box(
            low=np.array([-1.0, -1.0, 0.0]),
            high=np.array([1.0, 1.0, 1.0]),
            dtype=np.float32
        )

        self.frames_without_coin = 0
        self.max_frames_without_coin = 500
        self.total_shots_fired = 0
        self.total_deaths = 0
        self.total_coins = 0
        self.prev_meteor_distance = None
        self.prev_laser_distance = None
        self.prev_rocket_distance = None

    def _apply_curriculum(self):
        """
        Enable/disable obstacles and enemies depending on the current curriculum stage.

        Stages:
            0: Only coins
            1: Coins + meteors
            2: Coins + meteors + lasers
            3: All obstacles (including rockets and shooting)
        """
        if self.mode != "progressive":
            return

        # Always active: coins
        # Stage 0: only coins
        if self.curriculum_stage < 1:
            self.game.rocket.active = False
            if hasattr(self.game.laser, "reset"):
                self.game.laser.reset()
            self.game.meteor_system.clear_meteors()

        # Stage 1: add meteors
        elif self.curriculum_stage == 1:
            self.game.rocket.active = False
            if hasattr(self.game.laser, "reset"):
                self.game.laser.reset()

        # Stage 2: add lasers
        elif self.curriculum_stage == 2:
            self.game.rocket.active = False

        # Stage 3: rockets and shooting -- everything active
        else:
            pass

    def reset(self, *, seed=None):
        """
        Reset the environment for a new episode.

        Args:
            seed (int, optional): Random seed for reproducibility.

        Returns:
            tuple:
                obs (np.ndarray): Initial observation.
                info (dict): Additional environment information.
        """
        super().reset(seed=seed)
        self.game._start_new_game()
        self.frames_without_coin = 0
        self.episode_steps = 0

        if self.fixed_stage > -1:
            self.curriculum_stage = self.fixed_stage

        self.max_episode_steps_stage0 = random.randint(1500, 2000)
        # print(f"[DEBUG] Resetando ambiente. Stage atual = {self.curriculum_stage}")
        spawn_coins(self.game.coins, pattern="horiz")

        return self._get_obs(), {}

    def step(self, action):
        """
        Perform one step in the environment.

        Args:
            action (np.ndarray): Action array [booster_power, move_speed, shoot].

        Returns:
            tuple:
                obs (np.ndarray): Next observation.
                reward (float): Scalar reward.
                done (bool): Whether the episode ended.
                truncated (bool): Whether the episode was truncated.
                info (dict): Additional info such as penalties and stats.
        """
        self.steps_done += 1
        self.episode_steps += 1
        done = False

        if self.fixed_stage == -1:  # Dynamic stage based on steps
            for i, th in enumerate(self.stage_thresholds):
                if self.steps_done >= th:
                    self.curriculum_stage = i
        else: # Fixed stage (retraining mode)
            self.curriculum_stage = self.fixed_stage

        player = self.game.player
        player.controlled_by_ai = True
        player.booster_power = np.clip(action[0], 0.0, 1.0)
        player.move_speed = np.clip(action[1], -1.0, 1.0)
        shaped_r = 0.0
        rocket_active_before_shoot = self.game.rocket.active if self.game.rocket else False
        shoot_success = False

        self._apply_curriculum()

        coin_count_before = self.game.state.coin_count
        self.game._update_game_logic()
        obs = self._get_obs()
        reward = 0.0

        # --- Coin reward ---
        coins_collected = self.game.state.coin_count - coin_count_before
        reward += coins_collected * config.COIN_REWARD

        # Reward shaping for proximity to nearest coin
        nearest_coin = None
        min_dist = float("inf")
        for coin in self.game.coins:
            cx, cy = coin.rect.centerx, coin.rect.centery
            d = np.hypot(cx - player.x, cy - player.y)
            if d < min_dist:
                min_dist = d
                nearest_coin = coin
        if nearest_coin:
            reward += config.COIN_SHAPING_SCALE * (1.0 - np.tanh(min_dist / config.WIDTH))

        # Penalty for too many frames without collecting coins
        if coins_collected == 0:
            self.frames_without_coin += 1
        else:
            self.frames_without_coin = 0
        if self.frames_without_coin > self.max_frames_without_coin:
            reward -= config.PENALTY_NO_COIN
            self.frames_without_coin = 0

        # --- Meteor proximity penalty ---
        meteor_penalty = 0.0
        if self.curriculum_stage >= 1 and self.game.meteor_system.meteors:
            nearest_meteor = None
            min_dist = float("inf")
            for m in self.game.meteor_system.meteors:
                d = np.hypot(m.rect.centerx - player.x, m.rect.centery - player.y)
                if d < min_dist:
                    min_dist = d
                    nearest_meteor = m

            if nearest_meteor is not None:
                dx = nearest_meteor.rect.centerx - player.x
                dy = nearest_meteor.rect.centery - player.y
                dist = np.hypot(dx, dy)
                if dist < config.METEOR_DANGER_RADIUS:
                    meteor_penalty =  config.METEOR_DANGER_PENALTY * (1.0 - dist / config.METEOR_DANGER_RADIUS)
                    reward -= meteor_penalty

                # reward shaping based on distance to previous meteor
                if self.prev_meteor_distance is not None and dist > self.prev_meteor_distance:
                    reward += 0.1 * (dist - self.prev_meteor_distance)

                self.prev_meteor_distance = dist
            else:
                self.prev_meteor_distance = None

        # --- Laser proximity penalty ---
        laser_penalty = 0.0
        if self.curriculum_stage >= 2 and self.game.laser_rect:
            laser_rect = self.game.laser_rect
            dx = laser_rect.centerx - player.x
            dy = laser_rect.centery - player.y
            dist = np.hypot(dx, dy)
            if dist < config.LASER_DANGER_RADIUS:
                laser_penalty = config.LASER_DANGER_PENALTY * (1.0 - dist / config.LASER_DANGER_RADIUS)
                reward -= laser_penalty

            # Reward shaping based on distance to previous laser
            if self.prev_laser_distance is not None and dist > self.prev_laser_distance:
                reward += 0.1 * (dist - self.prev_laser_distance)

                self.prev_laser_distance = dist
            else:
                self.prev_laser_distance = None

        # --- Rocket and shooting handling ---
        rocket_penalty = 0.0
        if self.curriculum_stage >= 3:
            rocket_mode_before_shoot = self.game.rocket.mode if self.game.rocket else None
            shoot = action[2] >= 0.7
            if shoot and rocket_mode_before_shoot == 1:
                projectile = player.shoot()
                if projectile:
                    self.game.state.projectiles.append(projectile)
                    self.total_shots_fired += 1
                    shoot_success = True

            rocket_active_after_shoot = self.game.rocket.active
            rocket_mode_after_shoot = self.game.rocket.mode if self.game.rocket else None
            rocket_hitbox = self.game.rocket.get_hitbox() if self.game.rocket else None

            if rocket_active_before_shoot and not rocket_active_after_shoot:
                reward += config.ROCKET_DESTROY_REWARD

            elif rocket_hitbox and rocket_mode_after_shoot == 1:
                dist = np.hypot(
                    rocket_hitbox.centerx - player.x,
                    rocket_hitbox.centery - player.y
                )

                if shoot_success:
                    shaped_r = config.ROCKET_SHAPING_SCALE / (dist + 1.0)
                    reward += shaped_r

                if dist < config.ROCKET_DANGER_RADIUS:
                    rocket_penalty = config.ROCKET_DANGER_PENALTY * (1.0 - dist / config.ROCKET_DANGER_RADIUS)
                    reward -= rocket_penalty

                if self.prev_rocket_distance is not None and dist > self.prev_rocket_distance:
                    reward += 0.05 * (dist - self.prev_rocket_distance)

                self.prev_rocket_distance = dist

            else:
                self.prev_rocket_distance = None # Warning mode

            if shoot_success and rocket_active_after_shoot:
                reward -= config.PENALTY_BAD_SHOT

        # Penalty for moving too far to the right
        x_ratio = player.x / config.WIDTH
        if x_ratio > config.X_RATIO_THRESHOLD:
            reward -= config.PENALTY_X_RATIO * (x_ratio - config.X_RATIO_THRESHOLD)

        if 0.4 < x_ratio < config.X_RATIO_THRESHOLD - 0.1:
            reward += config.REWARD_STAY_IN_MIDDLE

        # --- Episode termination conditions ---
        if self.curriculum_stage == 0 and self.episode_steps > self.max_episode_steps_stage0:
            done = True
        if self.game.game_state == GameStates.GAME_OVER:
            done = True
            reward -= config.PENALTY_DEATH
            self.total_deaths += 1
            self.total_coins += self.game.state.coin_count

        info = {
            "coins_collected": self.game.state.coin_count,
            "coins_reward": coins_collected * config.COIN_REWARD,
            "frames_without_coin": self.frames_without_coin,
            "deaths": self.total_deaths,
            "shots_fired": self.total_shots_fired,
            "rocket_reward": shaped_r,
            "rocket_penalty": rocket_penalty,
            "meteor_penalty": meteor_penalty,
            "laser_penalty": laser_penalty,
            "distance_to_coin": min_dist if nearest_coin else None,
            "episode_reward": float(reward),
        }

        if self.mode == "progressive":
            info["curriculum_stage"] = self.curriculum_stage

        return obs, float(reward), done, False, info

    def _get_obs(self):
        """
        Compute the current observation vector.

        Returns:
            np.ndarray: An 11-dimensional normalized vector representing:
                [x_norm, y_norm, vy_norm,
                 dx_coin, dy_coin,
                 dx_rocket, dy_rocket,
                 dx_laser, dy_laser,
                 dx_meteor, dy_meteor,
                 rocket_active_flag]
        """
        p = self.game.player

        x_norm = np.clip(p.x / config.WIDTH, 0.0, 1.0)
        y_norm = np.clip(p.y / config.HEIGHT, 0.0, 1.0)
        vy_norm = np.clip(p.velocity_y / 20.0, -1.0, 1.0) * 0.5 + 0.5

        def rel(entity):
            """Return relative (dx, dy) normalized between -1 and 1."""
            if entity is None:
                return 0.0, 0.0
            cx, cy = entity.centerx, entity.centery
            return (
                np.clip((cx - p.x) / config.WIDTH, -1.0, 1.0),
                np.clip((cy - p.y) / config.HEIGHT, -1.0, 1.0)
            )

        # --- Nearest coin ---
        nearest_coin = None
        min_dist = float("inf")
        for c in self.game.coins:
            dx = abs(c.rect.centerx - p.x)
            dy = abs(c.rect.centery - p.y)
            d = np.hypot(dx, dy)
            if d < min_dist:
                min_dist = d
                nearest_coin = c.rect

        # --- Nearest meteor ---
        nearest_meteor = None
        if self.game.meteor_system.meteors:
            nearest_meteor = min(
                [m.rect for m in self.game.meteor_system.meteors],
                key=lambda r: abs(r.centerx - p.x)
            )

        rocket_rect = self.game.rocket.get_hitbox()
        laser_rect = self.game.laser_rect if hasattr(self.game, "laser_rect") else None

        dx_coin, dy_coin = rel(nearest_coin)
        dx_rocket, dy_rocket = rel(rocket_rect)
        dx_laser, dy_laser = rel(laser_rect)
        dx_meteor, dy_meteor = rel(nearest_meteor)

        rocket_active_flag = 1.0 if self.game.rocket.active and getattr(self.game.rocket, 'mode', 0) == 1 else 0.0

        return np.array([
            x_norm, y_norm, vy_norm,
            dx_coin, dy_coin,
            dx_rocket, dy_rocket,
            dx_laser, dy_laser,
            dx_meteor, dy_meteor,
            rocket_active_flag
        ], dtype=np.float32)
