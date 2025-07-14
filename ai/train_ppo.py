import os
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize
from ai.jetpack_env import JetpackEnv

if __name__ == '__main__':
    # 使用向量化环境，关闭渲染
    env = make_vec_env(lambda: JetpackEnv(render=False, curriculum_stage=2), n_envs=4, seed=0)
    env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_reward=2.0)

    model_path = "ai/ppo_jetpack_agent_stage2.zip"
    if os.path.exists(model_path):
        print(f"从 {model_path} 加载模型，继续训练...")
        model = PPO.load(model_path, env=env, tensorboard_log="./ppo_jetpack_tensorboard/")
    else:
        print("未找到已保存模型，将新建模型训练...")
        model = PPO('MlpPolicy', env, verbose=1, tensorboard_log="./ppo_jetpack_tensorboard/")

    # 创建检查点回调，每10000步保存一次模型
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,  # 每10000步保存一次
        save_path="./ai/checkpoints_stage2",  # 保存路径
        name_prefix="ppo_checkpoint"  # 文件名前缀
    )

    # 开始训练
    print("开始训练...")
    model.learn(total_timesteps=300_000, reset_num_timesteps=False, callback=checkpoint_callback)

    # 训练结束后保存最终模型
    model.save("ai/ppo_jetpack_agent_stage2")

    print("训练完成，模型已保存。") 