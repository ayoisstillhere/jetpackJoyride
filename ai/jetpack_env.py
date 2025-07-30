import random
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from core.game import Game, GameStates
from entities.coin import spawn_coins
from config.settings import WIDTH, HEIGHT

# === REWARD CONSTANTS ===
COIN_REWARD = 15.0
COIN_SHAPING_SCALE = 2.0
PENALTY_NO_COIN = 1.0

ROCKET_DESTROY_REWARD = 8.0
ROCKET_SHAPING_SCALE = 0.2
ROCKET_DANGER_RADIUS = 0.15 * WIDTH
ROCKET_DANGER_PENALTY = 2.0
PENALTY_BAD_SHOT = 0.5

LASER_DANGER_RADIUS = 0.15 * WIDTH
LASER_DANGER_PENALTY = 2.0

METEOR_DANGER_RADIUS = 0.15 * WIDTH
METEOR_DANGER_PENALTY = 2.0

PENALTY_DEATH = 10.0

class JetpackEnv(gym.Env):
    def __init__(self, render=False, mode="progressive"):
        super(JetpackEnv, self).__init__()
        self.mode = mode
        self.game = Game(render=render, mode=mode)

        # Curriculum
        self.curriculum_stage = 0
        self.steps_done = 0
        self.stage_thresholds = [0, 50000, 200000, 400000] # to a 700k total timesteps

        # Observation space
        self.observation_space = spaces.Box(
            low=np.array([0.0, 0.0, 0.0] + [-1.0, -1.0]*4 + [0.0], dtype=np.float32),
            high=np.array([1.0, 1.0, 1.0] + [ 1.0,  1.0]*4 + [1.0], dtype=np.float32),
            dtype=np.float32
        )

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
        Liga/desliga obstáculos e inimigos dependendo do estágio do currículo.
        stage 0: só moedas
        stage 1: moedas + meteoro
        stage 2: moedas + meteoro + laser
        stage 3: tudo (inclui rocket e tiros)
        """
        if self.mode != "progressive":
            return

        # print(f"[DEBUG] Aplicando curriculum: stage={self.curriculum_stage}")

        # Sempre ativo: moedas
        # Stage 0: apenas moedas
        if self.curriculum_stage < 1:
            self.game.rocket.active = False
            if hasattr(self.game.laser, "reset"):
                self.game.laser.reset()
            self.game.meteor_system.clear_meteors()
        # Stage 1: meteoros
        elif self.curriculum_stage == 1:
            self.game.rocket.active = False
            if hasattr(self.game.laser, "reset"):
                self.game.laser.reset()
        # Stage 2: meteoros + laser
        elif self.curriculum_stage == 2:
            self.game.rocket.active = False
        # Stage 3: tudo ativo
        else:
            pass

    def reset(self, *, seed=None):
        super().reset(seed=seed)
        self.game._start_new_game()
        self.frames_without_coin = 0
        self.episode_steps = 0
        self.max_episode_steps_stage0 = random.randint(1500, 2000)
        print(f"[DEBUG] Resetando ambiente. Stage atual = {self.curriculum_stage}")
        spawn_coins(self.game.coins, pattern="horiz")

        return self._get_obs(), {}

    def step(self, action):
        self.steps_done += 1
        self.episode_steps += 1
        done = False
        for i, th in enumerate(self.stage_thresholds):
            if self.steps_done >= th:
                self.curriculum_stage = i

        player = self.game.player
        player.controlled_by_ai = True
        player.booster_power = np.clip(action[0], 0.0, 1.0)
        player.move_speed = np.clip(action[1], -1.0, 1.0)
        shaped_r = 0.0
        rocket_active_before_shoot = self.game.rocket.active if self.game.rocket else False
        shoot_success = False

        # Aplica regras do curriculum se progressivo
        self._apply_curriculum()

        coin_count_before = self.game.state.coin_count
        self.game._update_game_logic()
        obs = self._get_obs()
        reward = 0.0

        if self.curriculum_stage >= 3:
            rocket_mode_before_shoot = self.game.rocket.mode if self.game.rocket else None # TO REMOVE
            shoot = action[2] >= 0.7
            if shoot and rocket_mode_before_shoot == 1:
                projectile = player.shoot()
                if projectile:
                    self.game.state.projectiles.append(projectile)
                    self.total_shots_fired += 1
                    shoot_success = True

        # --- Reward coins ---
        coins_collected = self.game.state.coin_count - coin_count_before
        reward += coins_collected * COIN_REWARD

        # Shaping para proximidade da moeda
        nearest_coin = None
        min_dist = float("inf")
        for coin in self.game.coins:
            cx, cy = coin.rect.centerx, coin.rect.centery
            d = np.hypot(cx - player.x, cy - player.y)
            if d < min_dist:
                min_dist = d
                nearest_coin = coin
        if nearest_coin:
            reward += COIN_SHAPING_SCALE * (1.0 - np.tanh(min_dist / WIDTH))

        # Penalidade se fica muito tempo sem pegar moedas
        if coins_collected == 0:
            self.frames_without_coin += 1
        else:
            self.frames_without_coin = 0
        if self.frames_without_coin > self.max_frames_without_coin:
            reward -= PENALTY_NO_COIN
            self.frames_without_coin = 0

        # --- Meteor proximity shaping ---
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
                if dist < METEOR_DANGER_RADIUS:
                    meteor_penalty =  METEOR_DANGER_PENALTY * (1.0 - dist / METEOR_DANGER_RADIUS)
                    reward -= meteor_penalty

                # reward shaping based on distance to previous meteor
                if self.prev_meteor_distance is not None and dist > self.prev_meteor_distance:
                    reward += 0.1 * (dist - self.prev_meteor_distance)

                self.prev_meteor_distance = dist
            else:
                self.prev_meteor_distance = None

        # --- Laser proximity shaping ---
        laser_penalty = 0.0
        if self.curriculum_stage >= 2 and self.game.laser_rect:
            laser_rect = self.game.laser_rect
            dx = laser_rect.centerx - player.x
            dy = laser_rect.centery - player.y
            dist = np.hypot(dx, dy)
            if dist < LASER_DANGER_RADIUS:
                laser_penalty = LASER_DANGER_PENALTY * (1.0 - dist / LASER_DANGER_RADIUS)
                reward -= laser_penalty

            # Reward shaping based on distance to previous laser
            if self.prev_laser_distance is not None and dist > self.prev_laser_distance:
                reward += 0.1 * (dist - self.prev_laser_distance)

                self.prev_laser_distance = dist
            else:
                self.prev_laser_distance = None

        # --- Rocket and shooting logic ---
        rocket_penalty = 0.0
        if self.curriculum_stage >= 3:
            rocket_active_after_shoot = self.game.rocket.active
            rocket_mode_after_shoot = self.game.rocket.mode if self.game.rocket else None
            rocket_hitbox = self.game.rocket.get_hitbox() if self.game.rocket else None

            if rocket_active_before_shoot and not rocket_active_after_shoot:
                reward += ROCKET_DESTROY_REWARD

            elif rocket_hitbox and rocket_mode_after_shoot == 1:
                # O foguete está ativo em modo ataque
                dist = np.hypot(
                    rocket_hitbox.centerx - player.x,
                    rocket_hitbox.centery - player.y
                )

                # Recompensa de shaping por se aproximar da trajetória do foguete
                shaped_r = ROCKET_SHAPING_SCALE / (dist + 1.0)
                reward += shaped_r

                # Penaliza se está muito perto do foguete (zona de perigo)
                if dist < ROCKET_DANGER_RADIUS:
                    rocket_penalty = ROCKET_DANGER_PENALTY * (1.0 - dist / ROCKET_DANGER_RADIUS)
                    reward -= rocket_penalty

                # Pequeno bônus se conseguiu aumentar a distância em relação ao passo anterior
                if self.prev_rocket_distance is not None and dist > self.prev_rocket_distance:
                    reward += 0.05 * (dist - self.prev_rocket_distance)

                self.prev_rocket_distance = dist

            else:
                # Foguete em aviso (mode 0) ou inativo: reset histórico
                self.prev_rocket_distance = None

            # Penalidade por tiro ruim (atirou, mas foguete continua ativo)
            if shoot_success and rocket_active_after_shoot:
                reward -= PENALTY_BAD_SHOT

        # Finaliza se morreu
        if self.curriculum_stage == 0 and self.episode_steps > self.max_episode_steps_stage0:
            done = True
        if self.game.game_state == GameStates.GAME_OVER:
            done = True
            reward -= PENALTY_DEATH
            self.total_deaths += 1
            self.total_coins += self.game.state.coin_count

        info = {
            "coins_collected": self.game.state.coin_count,
            "coins_reward": coins_collected * COIN_REWARD,
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

        # Adicionar estágio atual para acompanhar no TensorBoard
        if self.mode == "progressive":
            info["curriculum_stage"] = self.curriculum_stage

        return obs, float(reward), done, False, info

    def _get_obs(self):
        """
        Retorna um vetor de 11 valores normalizados:
        [x_norm, y_norm, vy_norm,
         dx_coin, dy_coin,
         dx_rocket, dy_rocket,
         dx_laser, dy_laser,
         dx_meteor, dy_meteor,
         rocket_active_flag]
        """

        p = self.game.player

        # Normaliza posição e velocidade
        x_norm = np.clip(p.x / WIDTH, 0.0, 1.0)
        y_norm = np.clip(p.y / HEIGHT, 0.0, 1.0)
        vy_norm = np.clip(p.velocity_y / 20.0, -1.0, 1.0) * 0.5 + 0.5

        def rel(entity):
            """Retorna posição relativa (dx, dy) normalizada entre -1 e 1"""
            if entity is None:
                return 0.0, 0.0
            cx, cy = entity.centerx, entity.centery
            return (
                np.clip((cx - p.x) / WIDTH, -1.0, 1.0),
                np.clip((cy - p.y) / HEIGHT, -1.0, 1.0)
            )

        # === Coin mais próxima (2D) ===
        nearest_coin = None
        min_dist = float("inf")
        for c in self.game.coins:
            dx = abs(c.rect.centerx - p.x)
            dy = abs(c.rect.centery - p.y)
            d = np.hypot(dx, dy)
            if d < min_dist:
                min_dist = d
                nearest_coin = c.rect

        # === Meteor mais próximo ===
        nearest_meteor = None
        if self.game.meteor_system.meteors:
            nearest_meteor = min(
                [m.rect for m in self.game.meteor_system.meteors],
                key=lambda r: abs(r.centerx - p.x)
            )

        rocket_rect = self.game.rocket.get_hitbox()
        laser_rect = self.game.laser_rect if hasattr(self.game, "laser_rect") else None

        # Calcula deslocamentos relativos
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
