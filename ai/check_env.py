from ai.jetpack_env import JetpackEnv
from stable_baselines3.common.env_checker import check_env

if __name__ == '__main__':
    env = JetpackEnv(render=False)
    check_env(env, warn=True)
    print('环境检查完成！') 