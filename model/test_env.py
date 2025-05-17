from runner_env import RunnerEnv

env = RunnerEnv()

obs = env.reset()
done = False
total_reward = 0
step_count = 0

while not done:
    action = env.action_space.sample() # random action [0,1]
    obs, reward, done, info = env.step(action)
    total_reward += reward
    step_count += 1

    print(f'Step: {step_count}')
    print(f'Observation: {obs}')
    print(f'Action taken: {action}')
    print(f'Reward: {reward}')
    print('-' * 30)

print('Episode finished.')
print('Total reward:', total_reward)
print('Total steps survived:', step_count)
