import sys
import os

USE_RENDER = False

if not USE_RENDER:
    os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
pygame.init()
if not USE_RENDER:
    pygame.display.set_mode((1, 1))

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# === Imports ===
import gymnasium as gym
from stable_baselines3 import SAC
from stable_baselines3.common.env_checker import check_env
from ai.jetpack_env import JetpackEnv

from stable_baselines3.common.callbacks import BaseCallback

# ==================================================================
EXP_NAME = 'sac_jetpack_500k'

class CustomTensorboardCallback(BaseCallback):
    def __init__(self, verbose=0):
        super().__init__(verbose)

    def _on_step(self) -> bool:
        infos = self.locals.get("infos", [])
        for info in infos:
            if "shots_fired" in info:
                self.logger.record("custom/shots_fired", info["shots_fired"])
            if "coins_collected" in info:
                self.logger.record("custom/coins_collected", info["coins_collected"])
            if "deaths" in info:
                self.logger.record("custom/deaths", info["deaths"])
            if "reward_from_coins" in info:
                self.logger.record("rewards/coins", info["reward_from_coins"])
            if "reward_from_survival" in info:
                self.logger.record("rewards/survival", info["reward_from_survival"])
            if "reward_from_rocket" in info:
                self.logger.record("rewards/rocket", info["reward_from_rocket"])
        return True

env = JetpackEnv(render=False)
check_env(env, warn=True)

model = SAC(
    "MlpPolicy",
    env,
    verbose=1,
    tensorboard_log=f"./ai/models/logs/",
    device='cuda',
    ent_coef="auto_0.1"
)
callback = CustomTensorboardCallback()
model.learn(
    total_timesteps=500_000,
    callback=callback,
    tb_log_name=EXP_NAME
)
model.save(f"./ai/models/model_{EXP_NAME}")