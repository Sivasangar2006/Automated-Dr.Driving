# agent/model.py
# This file holds the configuration for our AI model.
# We're using PPO (Proximal Policy Optimization) with a CNN policy
# meaning the AI learns directly from images (screen frames)

ALGORITHM = "PPO"
POLICY = "CnnPolicy"  # CNN because our input is an image

# Hyperparameters — these control how the AI learns
# you can come back and tweak these later to improve performance
HYPERPARAMS = {
    "learning_rate":  3e-4,   # how fast the AI updates itself
    "n_steps":        512,    # how many steps before each update
    "batch_size":     64,     # how many samples per training batch
    "n_epochs":       10,     # how many times to reuse each batch
    "gamma":          0.99,   # how much the AI values future rewards
    "gae_lambda":     0.95,   # controls advantage estimation
    "clip_range":     0.2,    # prevents too large updates at once
    "ent_coef":       0.01,   # encourages the AI to explore
    "verbose":        1,      # prints training progress
    "device":         "cpu",  # change to "cuda" when using Colab GPU
}

# Training config
TOTAL_TIMESTEPS = 500_000   # increase to 2M+ when using real game
SAVE_DIR        = "models/"
LOG_DIR         = "logs/"
MODEL_NAME      = "dr_driving_ppo"