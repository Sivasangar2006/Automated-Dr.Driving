import time
from environment.game_env import DrDrivingEnv

env = DrDrivingEnv()

state = env.reset()

for _ in range(50):
    action = env.action_space.sample()
    state, reward, done, _ = env.step(action)
    print("Reward:", reward, "Done:", done)

    if done:
        print("Episode ended, resetting...")
        state = env.reset()