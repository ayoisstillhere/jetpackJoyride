import os
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize
from ai.jetpack_env import JetpackEnv

def train_stage(stage, prev_model_path=None, save_path=None, total_timesteps=500_000):
    env = make_vec_env(lambda: JetpackEnv(render=False, curriculum_stage=stage), n_envs=2, seed=0)
    env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_reward=10.0)
    if prev_model_path and os.path.exists(prev_model_path):
        print(f'从 {prev_model_path} 加载模型，继续训练...')
        model = PPO.load(prev_model_path, env=env, tensorboard_log="./ppo_jetpack_tensorboard/")
    else:
        print('新建模型训练...')
        model = PPO('MlpPolicy', env, verbose=1, tensorboard_log="./ppo_jetpack_tensorboard/")
    checkpoint_callback = CheckpointCallback(
        save_freq=100_000,
        save_path="./ai/checkpoints_stage2",
        name_prefix=f"ppo_checkpoint_stage{stage}"
    )
    print(f"开始第{stage}阶段训练...")
    model.learn(total_timesteps=total_timesteps, reset_num_timesteps=False, callback=checkpoint_callback)
    if save_path:
        model.save(save_path)
        print(f"第{stage}阶段训练完成，模型已保存到{save_path}")
    return model

if __name__ == '__main__':
    # 第一阶段：只训练射击
    train_stage(1, prev_model_path=None, save_path="ai/ppo_stage1_shooting.zip", total_timesteps=500_000)
    # 第二阶段：只训练躲陨石
    train_stage(2, prev_model_path="ai/ppo_stage1_shooting.zip", save_path="ai/ppo_stage2_dodge.zip", total_timesteps=500_000)
    # 第三阶段：只训练吃金币
    train_stage(3, prev_model_path="ai/ppo_stage2_dodge.zip", save_path="ai/ppo_stage3_coins.zip", total_timesteps=500_000)
    # 最终阶段：全目标
    train_stage(0, prev_model_path="ai/ppo_stage3_coins.zip", save_path="ai/ppo_jetpack_agent.zip", total_timesteps=1_000_000) 