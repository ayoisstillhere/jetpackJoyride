import sys
import os
import argparse

# ========== ARGUMENTS ==========
parser = argparse.ArgumentParser()
parser.add_argument("--mode", type=str, default="progressive", choices=["progressive"], help="Training mode")
parser.add_argument("--timesteps", type=int, default=700_000, help="Total timesteps")
args = parser.parse_args()

# ========== CONFIG ==========
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
from stable_baselines3 import SAC
from stable_baselines3.common.env_checker import check_env
from ai.jetpack_env import JetpackEnv
from stable_baselines3.common.callbacks import CallbackList, BaseCallback

# ========== EXPERIMENT SETUP ==========
mode = args.mode
total_timesteps = args.timesteps
exp_name = f"sac_{mode}_{total_timesteps // 1000}k"

print(f"Mode: {mode}, Timesteps: {total_timesteps}, Experiment: {exp_name}")

# ========== CALLBACK ==========
class CustomTensorboardCallback(BaseCallback):
    """
    Custom callback for logging additional metrics to TensorBoard.

    This callback reads information from the `info` dictionary returned by the environment
    and records metrics related to curriculum stage, coins, survival, shooting, penalties,
    and distances.
    """
    def __init__(self, verbose=0):
        super().__init__(verbose)

    def _on_step(self) -> bool:
        infos = self.locals.get("infos", [])
        for info in infos:
            # Curriculum stage
            if "curriculum_stage" in info:
                self.logger.record("general/curriculum_stage", info["curriculum_stage"])

            # Coins
            self.logger.record("coins/collected", info.get("coins_collected", -1))
            self.logger.record("coins/reward", info.get("coins_reward", -1))
            self.logger.record("coins/frames_without_coin", info.get("frames_without_coin", -1))

            # Dodge / deaths
            self.logger.record("dodge/deaths", info.get("deaths", -1))
            self.logger.record("dodge/survival_reward", info.get("survival_reward", -1))

            # Shooter
            self.logger.record("shooter/shots_fired", info.get("shots_fired", -1))
            self.logger.record("shooter/rocket_reward", info.get("rocket_reward", -1))

            # Penalties
            self.logger.record("penalties/rocket_penalty", info.get("rocket_penalty", -1))
            self.logger.record("penalties/meteor_penalty", info.get("meteor_penalty", -1))
            self.logger.record("penalties/laser_penalty", info.get("laser_penalty", -1))

            # Extra metrics
            self.logger.record("general/distance_to_coin", info.get("distance_to_coin", -1))
            self.logger.record("general/episode_reward", info.get("episode_reward", -1))

        return True

class CurriculumCheckpointCallback(BaseCallback):
    """
    Callback that saves a model checkpoint every time the curriculum stage changes.
    """
    def __init__(self, save_path="./ai/models/", verbose=1, exp_name=""):
        super().__init__(verbose)
        self.save_path = save_path
        self.last_stage = 0
        self.exp_name = exp_name

    def _on_step(self) -> bool:
        infos = self.locals.get("infos", [])
        for info in infos:
            if "curriculum_stage" in info:
                current_stage = info["curriculum_stage"]
                if current_stage > self.last_stage:
                    # Stage mudou → salvar checkpoint
                    self.last_stage = current_stage
                    steps = self.num_timesteps
                    filename = f"checkpoint_stage_{current_stage}_STP{steps}_{exp_name}"
                    full_path = os.path.join(self.save_path, filename)
                    self.model.save(full_path)
                    if self.verbose > 0:
                        print(f"[Checkpoint] Modelo salvo: {full_path}")
        return True

# ========== ENV ==========
env = JetpackEnv(render=USE_RENDER, mode=mode)
check_env(env, warn=True)

# ========== MODEL ==========
model = SAC(
    "MlpPolicy",
    env,
    verbose=1,
    tensorboard_log="./ai/models/logs/",
    device='cuda',
    ent_coef="auto"
)

# ========== TRAIN ==========
callback = CallbackList([
    CustomTensorboardCallback(),
    CurriculumCheckpointCallback(save_path="./ai/models/", exp_name=exp_name)
])
model.learn(
    total_timesteps=total_timesteps,
    callback=callback,
    tb_log_name=exp_name,
)
model.save(f"./ai/models/model_{exp_name}")