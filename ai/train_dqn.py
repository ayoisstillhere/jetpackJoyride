import os
import gym
from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import CheckpointCallback
from ai.jetpack_env import JetpackEnv

if __name__ == '__main__':
    # 创建环境
    env = JetpackEnv(render=True)
    
    model = DQN('MlpPolicy', env, verbose=1, tensorboard_log="./dqn_jetpack_tensorboard/")

    # 创建检查点回调，每10000步保存一次模型
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,  # 每10000步保存一次
        save_path="./ai/checkpoints/",  # 保存路径
        name_prefix="dqn_jetpack_checkpoint"  # 文件名前缀
    )

    # 开始训练
    print("开始DQN训练...")
    model.learn(total_timesteps=200_000, reset_num_timesteps=False, callback=checkpoint_callback)

    # 训练结束后保存最终模型
    model.save("ai/dqn_jetpack_agent1")

    print("DQN训练完成，模型已保存。") 