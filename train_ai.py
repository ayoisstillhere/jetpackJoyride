from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from ai.jetpack_env import JetpackEnv
import os

# 创建环境
env = JetpackEnv(render=False)
env = DummyVecEnv([lambda: env])

# 创建模型
model = PPO(
    "MlpPolicy",
    env,
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2,
    verbose=1
)

# 创建保存模型的目录
os.makedirs("models", exist_ok=True)

# 训练模型
total_timesteps = 1_000_000  # 可以根据需要调整
model.learn(
    total_timesteps=total_timesteps,
    progress_bar=False
)

# 保存模型
model.save("models/jetpack_ppo") 