# agent/train.py
# This is the main training loop.
# It creates the environment, builds the PPO agent, and starts learning.

import os
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback
from environment.game_env import DoctorDrivingEnv
from agent.model import (
    POLICY,
    HYPERPARAMS,
    TOTAL_TIMESTEPS,
    SAVE_DIR,
    LOG_DIR,
    MODEL_NAME,
)


def train(resume=False):

    # --- create folders if they don't exist yet ---
    os.makedirs(SAVE_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    # --- set up the environment ---
    env = DoctorDrivingEnv()
    env = Monitor(env)  # Monitor logs rewards and episode lengths automatically

    # --- save a checkpoint every 50k steps ---
    checkpoint_callback = CheckpointCallback(
        save_freq   = 50_000,
        save_path   = SAVE_DIR,
        name_prefix = MODEL_NAME,
    )

    # --- create or load the model ---
    if resume and os.path.exists(f"{SAVE_DIR}/{MODEL_NAME}.zip"):
        print("Resuming from saved model...")
        model = PPO.load(f"{SAVE_DIR}/{MODEL_NAME}", env=env)
    else:
        print("Starting fresh training...")
        model = PPO(
            policy          = POLICY,
            env             = env,
            tensorboard_log = LOG_DIR,
            **HYPERPARAMS,
        )

    # --- start training ---
    print(f"\nTraining for {TOTAL_TIMESTEPS:,} steps...")
    print("To monitor live, open a new terminal and run:")
    print("tensorboard --logdir logs/\n")

    model.learn(
        total_timesteps     = TOTAL_TIMESTEPS,
        callback            = checkpoint_callback,
        tb_log_name         = MODEL_NAME,
        reset_num_timesteps = not resume,
    )

    # --- save the final model ---
    model.save(f"{SAVE_DIR}/{MODEL_NAME}")
    print(f"\nDone! Model saved to {SAVE_DIR}/{MODEL_NAME}.zip")


def evaluate(n_episodes=5):

    model_path = f"{SAVE_DIR}/{MODEL_NAME}.zip"

    if not os.path.exists(model_path):
        print("No trained model found. Run train() first!")
        return

    print(f"Loading model from {model_path}...\n")
    model = PPO.load(model_path)
    env = DoctorDrivingEnv()

    for ep in range(n_episodes):
        obs, _ = env.reset()
        total_reward = 0
        done = False

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            done = terminated or truncated

        print(f"Episode {ep + 1} | Steps: {info['step']} | Reward: {total_reward:.2f}")

    env.close()