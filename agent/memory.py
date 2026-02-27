# agent/memory.py
# PPO manages its own memory internally via Stable Baselines3's rollout buffer
# so we don't need to build a custom one right now.
#
# In simple terms — after every 512 steps (n_steps in model.py),
# SB3 automatically stores all the experiences (observations, actions,
# rewards) and uses them to update the AI, then clears the buffer
# and starts fresh.
#
# This file is reserved for later if we want to:
# - Switch to DQN which needs a custom replay buffer
# - Add prioritized experience replay
# - Log or inspect what the AI is experiencing during training


def get_buffer_info():
    """
    Just a helper to remind us what buffer settings we're using.
    SB3 handles the actual buffer internally.
    """
    info = {
        "type":        "Rollout Buffer (PPO default)",
        "buffer_size": 512,   # same as n_steps in model.py
        "managed_by":  "Stable Baselines3 automatically",
    }
    for key, value in info.items():
        print(f"{key}: {value}")