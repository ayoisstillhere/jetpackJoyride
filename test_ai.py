from stable_baselines3 import PPO
from ai.jetpack_env import JetpackEnv
import time

# 创建环境
env = JetpackEnv(render=True)

# 加载模型
model = PPO.load("models/jetpack_ppo")

# 运行测试
obs = env.reset()
done = False
total_reward = 0

while not done:
    action, _states = model.predict(obs)
    obs, reward, done, info = env.step(action)
    total_reward += reward
    env.render()
    time.sleep(0.01)  # 控制游戏速度

print(f"总奖励: {total_reward}") 