import os
import gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import VecNormalize, DummyVecEnv
from ai.jetpack_env import JetpackEnv
import numpy as np
import time

if __name__ == '__main__':
    # 创建单环境并渲染
    def make_env():
        return JetpackEnv(render=True)
    env = DummyVecEnv([make_env])

    # 加载归一化参数（如果存在）
    if os.path.exists("vecnormalize.pkl"):
        env = VecNormalize.load("vecnormalize.pkl", env)
        env.training = False  # 测试时关闭归一化的更新
        env.norm_reward = False
        print("已加载VecNormalize归一化参数。")
    else:
        print("未找到vecnormalize.pkl，直接用原始环境测试。")

    # 加载模型
    #model = PPO.load("ai/ppo_stage1_shooting.zip")
    # 或
    #model = PPO.load("ai/ppo_stage2_dodge.zip")
    # 或
    #model = PPO.load("ai/ppo_stage3_coins.zip")
    # 或
    model = PPO.load("ai\checkpoints_stage2\ppo_checkpoint_stage0_2111424_steps.zip")
    obs = env.reset()
    total_reward = 0
    while True:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        total_reward += reward[0]
        env.render()
        time.sleep(1/30)  # 控制帧率
        if done[0]:
            print(f"本局总奖励: {total_reward}")
            obs = env.reset()
            total_reward = 0 