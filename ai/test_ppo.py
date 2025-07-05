import os
import gym
from stable_baselines3 import PPO
from ai.jetpack_env import JetpackEnv
import time

if __name__ == '__main__':
    # 加载环境
    env = JetpackEnv(render=True)

    # 加载模型
    model = PPO.load("ai/ppo_jetpack_agent")

    obs = env.reset()
    done = False
    total_reward = 0
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        total_reward += reward
        env.render()
        time.sleep(1/30)  # 帧率限制，30FPS
    print(f"测试完成，总奖励: {total_reward}") 