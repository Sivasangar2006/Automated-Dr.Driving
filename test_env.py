from environment.game_env import DrDrivingEnv

env = DrDrivingEnv()
obs, info = env.reset()

print(f"Observation shape: {obs.shape}")   # should be (84, 84, 1)
print(f"Observation dtype: {obs.dtype}")   # should be uint8
print(f"Observation min: {obs.min()}")     # should be 0
print(f"Observation max: {obs.max()}")     # should be 255

# run 10 random steps
for i in range(10):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    print(f"Step {i+1} | Action: {action} | Reward: {reward:.3f} | Speed: {info['speed']:.3f} | Terminated: {terminated}")

env.close()
print("\nAll good!")