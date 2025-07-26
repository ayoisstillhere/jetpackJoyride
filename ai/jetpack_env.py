import gym
from gym import spaces
import numpy as np
import pygame
from core.game import Game, GameStates
from config.settings import WIDTH, HEIGHT

class JetpackEnv(gym.Env):
    def __init__(self, render=False, debug=True):
        super(JetpackEnv, self).__init__()
        self.game = Game(render=render)
        self.debug = debug

        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(26,), dtype=np.float32)

        # actions: [move right, move left, jetpack, shoot], can be combined, 0/1 represents inactive/active
        self.action_space = spaces.MultiBinary(4)

    def reset(self):
        self.game._start_new_game()
        return self._get_obs()

    def step(self, action):
        from core.game import GameStates
        self.game.game_state = GameStates.PLAYING  # Ensure game is in playing state
        self.game.player.controlled_by_ai = True
        # reset all actions
        self.game.player.move_left = False
        self.game.player.move_right = False
        self.game.player.booster = False
        self.fired_this_step = False

        # Parse combined actions
        move_right, move_left, booster, shoot = action
        
        # move_right/move_left
        if move_right:
            self.game.player.move_right = True
        if move_left:
            self.game.player.move_left = True
        # jump/booster
        if booster:
            self.game.player.booster = True
            self.game.player.booster_duration = 2  # duration frame
        # shoot
        if shoot:
            projectile = self.game.player.shoot()
            if projectile:
                self.game.state.projectiles.append(projectile)
                self.fired_this_step = True

        coin_count_before = self.game.state.coin_count

        # automatic render during training
        if self.game.render:
            self.game._draw_game_screen()
            if self.game.screen:
                pygame.display.flip()

        self.game._update_game_logic()

        obs = self._get_obs()
        reward = self._get_reward(coin_count_before, shoot)
        done = self.game.game_state == GameStates.GAME_OVER
        info = {}

        return obs, reward, done, info

    def render(self, mode='human'):
        """Render the environment"""
        if self.game.render and self.game.screen:
            # Ensure the game is in PLAYING state for proper rendering
            from core.game import GameStates
            if self.game.game_state != GameStates.PLAYING:
                self.game.game_state = GameStates.PLAYING
            
            self.game._draw_game_screen()
            pygame.display.flip()
        return None

    def _get_obs(self):
        obs = np.zeros(26, dtype=np.float32)
        screen_width = self.game.screen.get_width() if self.game.render else WIDTH
        screen_height = self.game.screen.get_height() if self.game.render else HEIGHT

        # player
        player = getattr(self.game, 'player', None)
        obs[0] = np.clip(player.x / screen_width, 0.0, 1.0) if player else 0.0
        obs[1] = np.clip(player.y / screen_height, 0.0, 1.0) if player else 0.0
        obs[2] = np.clip(player.velocity_y / 20.0, -1.0, 1.0) * 0.5 + 0.5 if player else 0.0

        # rocket
        rocket = getattr(self.game, 'rocket', None)
        rocket_box = rocket.get_hitbox() if rocket and hasattr(rocket, 'get_hitbox') else None
        if rocket_box:
            obs[3] = np.clip(rocket_box.left / screen_width, 0.0, 1.0)
            obs[4] = np.clip(rocket_box.right / screen_width, 0.0, 1.0)
            obs[5] = np.clip(rocket_box.top / screen_height, 0.0, 1.0)
            obs[6] = np.clip(rocket_box.bottom / screen_height, 0.0, 1.0)
        else:
            obs[3:7] = 0.0

        # laser
        laser = getattr(self.game, 'laser', None)
        laser_box = laser.get_hitbox() if laser and hasattr(laser, 'get_hitbox') else None
        if laser_box:
            obs[7] = np.clip(laser_box.left / screen_width, 0.0, 1.0)
            obs[8] = np.clip(laser_box.right / screen_width, 0.0, 1.0)
            obs[9] = np.clip(laser_box.top / screen_height, 0.0, 1.0)
            obs[10] = np.clip(laser_box.bottom / screen_height, 0.0, 1.0)
        else:
            obs[7:11] = 0.0

        # nearest coin - only consider coins visible on screen
        coins = getattr(self.game, 'coins', [])
        nearest_coin = None
        if coins and player:
            # Filter coins that are on screen and in front of the player
            visible_coins = [coin for coin in coins if coin.rect.right > 0 and coin.rect.left < screen_width and coin.rect.x > player.x]
            if visible_coins:
                # Select the nearest one (smallest x coordinate)
                nearest_coin = min(visible_coins, key=lambda c: c.rect.x)
        if nearest_coin:
            obs[11] = np.clip(nearest_coin.rect.left / screen_width, 0.0, 1.0)
            obs[12] = np.clip(nearest_coin.rect.right / screen_width, 0.0, 1.0)
            obs[13] = np.clip(nearest_coin.rect.top / screen_height, 0.0, 1.0)
            obs[14] = np.clip(nearest_coin.rect.bottom / screen_height, 0.0, 1.0)
        else:
            obs[11:15] = 0.0

        # game speed
        speed = self.game._get_speed() if hasattr(self.game, "_get_speed") else self.game.difficulty_system.game_speed
        obs[15] = np.clip(speed / 13.0, 0.0, 1.0)

        # rocket warning
        rocket_obj = rocket
        obs[16] = 1.0 if rocket_obj and rocket_obj.active and getattr(rocket_obj, 'mode', 1) == 0 else 0.0
        obs[17] = np.clip(rocket_obj.y / screen_height, 0.0, 1.0) if (rocket_obj and rocket_obj.active and getattr(rocket_obj, 'mode', 1) == 0) else 0.0

        # meteor
        meteor_system = getattr(self.game, 'meteor_system', None)
        meteor_obj = meteor_system.meteors[0] if meteor_system and hasattr(meteor_system, 'meteors') and meteor_system.meteors else None
        meteor_box = meteor_obj.get_hitbox() if meteor_obj and hasattr(meteor_obj, 'get_hitbox') else None
        if meteor_box:
            obs[18] = np.clip(meteor_box.left / screen_width, 0.0, 1.0)
            obs[19] = np.clip(meteor_box.right / screen_width, 0.0, 1.0)
            obs[20] = np.clip(meteor_box.top / screen_height, 0.0, 1.0)
            obs[21] = np.clip(meteor_box.bottom / screen_height, 0.0, 1.0)
        else:
            obs[18:22] = 0.0

        # player hitbox
        player_box = player.get_hitbox() if player and hasattr(player, 'get_hitbox') else None
        if player_box:
            obs[22] = np.clip(player_box.left / screen_width, 0.0, 1.0)
            obs[23] = np.clip(player_box.right / screen_width, 0.0, 1.0)
            obs[24] = np.clip(player_box.top / screen_height, 0.0, 1.0)
            obs[25] = np.clip(player_box.bottom / screen_height, 0.0, 1.0)
        else:
            obs[22:26] = 0.0



        return obs

    def _get_reward(self, coin_count_before, shoot):
        reward = 0.1

        # Coin reward
        if self.game.state.coin_count > coin_count_before:
            reward += 5.0

        # Death penalty
        if self.game.game_state == GameStates.GAME_OVER:
            reward -= 3.0

        return reward