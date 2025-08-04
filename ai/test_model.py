import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import numpy as np
from stable_baselines3 import SAC
from ai.jetpack_env import JetpackEnv
from core.game import Game

game = Game(render=True)
game.player.controlled_by_ai = True

env = JetpackEnv(render=True)
env.game = game

model = SAC.load("./ai/models/model_sac_pro1.8m_stage3_extended900", env=env)

def act_with_sac():
    obs = env._get_obs()
    action, _ = model.predict(obs, deterministic=True)

    game.player.booster_power = np.clip(action[0], 0.0, 1.0)
    game.player.move_speed = np.clip(action[1], -1.0, 1.0)

    if action[2] >= 0.7:
        proj = game.player.shoot()
        if proj:
            game.state.projectiles.append(proj)


game.act_with_model = act_with_sac

game.run()