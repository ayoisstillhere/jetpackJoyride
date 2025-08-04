from huggingface_hub import hf_hub_download
from stable_baselines3 import SAC
import numpy as np
from core.game import Game
from ai.jetpack_env import JetpackEnv
import argparse


def main(filename: str):
    """
    Download a Stable-Baselines3 model from Hugging Face Hub (with internal caching)
    and run the game using it.
    """
    model_path = hf_hub_download(
        repo_id="yanka9/jetpack-sb3sac-models",
        filename=filename,
        repo_type="model",
        local_dir="./ai",
    )

    game = Game(render=True)
    game.player.controlled_by_ai = True

    env = JetpackEnv(render=True)
    env.game = game

    model = SAC.load(model_path, env=env)

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Jetpack Game with a pretrained SB3 model from HF Hub.")
    parser.add_argument(
        "--filename",
        type=str,
        required=False,
        default="model_sac_pro1.8m_stage3_extended900",
        help="Model filename stored in the Hugging Face repo (e.g. model_sac_pro900k_stage3_extended200.zip)",
    )
    args = parser.parse_args()
    main(args.filename)