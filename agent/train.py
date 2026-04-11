# agent/train.py
# This is the main training loop.
# It creates the environment, builds the PPO agent, and starts learning.

import os
import numpy as np
from collections import deque
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback
from environment.game_env import DrDrivingEnv
from agent.model import (
    POLICY,
    HYPERPARAMS,
    TOTAL_TIMESTEPS,
    SAVE_DIR,
    LOG_DIR,
    MODEL_NAME,
)


class DiagnosticCallback(BaseCallback):
    def __init__(self, log_every=5_000):
        super().__init__()
        self.log_every = log_every
        self._act_buf  = deque(maxlen=log_every)
        self._rew_buf  = deque(maxlen=log_every)
        self._last_log = 0

    def _on_step(self):
        self._act_buf.append(int(self.locals["actions"][0]))
        self._rew_buf.append(float(self.locals["rewards"][0]))

        if self.num_timesteps - self._last_log >= self.log_every:
            self._last_log = self.num_timesteps
            arr = np.array(self._act_buf)
            mean_r = np.mean(self._rew_buf)
            n = len(arr)
            
            # Action buckets
            accel = np.sum(np.isin(arr, [0,1,2]))
            steer = np.sum(np.isin(arr, [1,2,4,5,7,8]))
            
            print(f"\nStep {self.num_timesteps:>7,} | mean_r: {mean_r:+.3f} | accel: {100*accel/n:.0f}% | steer: {100*steer/n:.0f}%")
        return True


def make_env(rank):
    """
    Utility function for multiplexed multiprocessing.
    Creates ADB environments explicitly on ports 5556, 5595, 5605.
    Hooks into specific Window Handles targeting those instances.
    """
    ports = [5556, 5595, 5605]
    
    # Exact Window Titles of the instances based on earlier diagnostics
    windows = ["BlueStacks App Player", "BlueStacks App Player 4", "BlueStacks App Player 5"]
    
    def _init():
        env = DrDrivingEnv(adb_port=ports[rank], window_title=windows[rank])
        env = Monitor(env)
        return env
    return _init

def train(resume=False):

    # --- create folders if they don't exist yet ---
    os.makedirs(SAVE_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    # --- set up the Vectorized Environment ---
    # Running 3 instances in parallel automatically maps to ports: 5555, 5565, 5575
    n_envs = 3
    env = SubprocVecEnv([make_env(i) for i in range(n_envs)])

    # --- save a checkpoint every 50k steps ---
    checkpoint_callback = CheckpointCallback(
        save_freq   = max(50_000 // n_envs, 1),
        save_path   = SAVE_DIR,
        name_prefix = MODEL_NAME,
    )

    if resume and os.path.exists(f"{SAVE_DIR}/{MODEL_NAME}.zip"):
        print("Resuming from saved RL checkpoint...")
        model = PPO.load(f"{SAVE_DIR}/{MODEL_NAME}", env=env)
    else:
        print("Starting fresh training...")
        model = PPO(
            policy          = POLICY,
            env             = env,
            tensorboard_log = LOG_DIR,
            **HYPERPARAMS,
        )

    diag_callback = DiagnosticCallback(log_every=5_000)

    # --- start training ---
    print(f"\nTraining for {TOTAL_TIMESTEPS:,} steps...")
    print("To monitor live, open a new terminal and run:")
    print("tensorboard --logdir logs/\n")

    model.learn(
        total_timesteps     = TOTAL_TIMESTEPS,
        callback            = [checkpoint_callback, diag_callback],
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
    env = DrDrivingEnv()

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