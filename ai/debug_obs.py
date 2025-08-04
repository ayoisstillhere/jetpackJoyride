import numpy as np
from ai.jetpack_env import JetpackEnv

if __name__ == '__main__':
    env = JetpackEnv(render=False)
    obs, info = env.reset()
    print('初始观测向量:', obs)
    step_count = 0
    while True:
        # 随机动作（你也可以手动指定动作）
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        step_count += 1
        print(f'\n第{step_count}步:')
        print('观测向量:', obs)
        # 解析玩家x坐标
        player_x = obs[0]
        print('玩家x归一化坐标:', player_x)
        # 火箭包围盒信息（假设在obs[7:11]和[11:15]）
        print('火箭1包围盒:', obs[7:11])
        print('火箭2包围盒:', obs[11:15])
        # 激光包围盒信息
        print('激光1包围盒:', obs[15:19])
        print('激光2包围盒:', obs[19:23])
        # 陨石包围盒信息
        print('陨石1包围盒:', obs[23:27])
        print('陨石2包围盒:', obs[27:31])
        if terminated or truncated or step_count > 50:
            print('回合结束或步数超过50，退出。')
            break 