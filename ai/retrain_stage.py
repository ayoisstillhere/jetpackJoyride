import os, sys
# ========== ENV CONFIG ==========
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

from stable_baselines3 import SAC
from jetpack_env import JetpackEnv

# === SAVING CONFIG ===
exp_name = "sac_pro900k_stage3_extended900v2"
total_timesteps = 900000
model_path = "./ai/models/model_sac_pro900k_stage3_retrained.zip"

stage = 3
env = JetpackEnv(render=False)
env.fixed_stage = stage

# === Load existing model ===
print(f"Loading pretrained model from {model_path}")
old_model = SAC.load(model_path)
new_model = SAC(
            'MlpPolicy',
            env=env,
            verbose=1,
            tensorboard_log="./ai/models/logs/",
            device='cuda',
            ent_coef="auto"
        )
new_model.policy.load_state_dict(old_model.policy.state_dict())

# === Continue training ===
print(f"Starting retraining for {total_timesteps} steps at stage {stage}...")
new_model.learn(
    total_timesteps=total_timesteps,
    tb_log_name=exp_name,
    progress_bar=True,
    reset_num_timesteps=False
)

# === Save final model ===
final_path = f"./ai/models/model_{exp_name}"
new_model.save(final_path)
print(f"Model saved to {final_path}")
