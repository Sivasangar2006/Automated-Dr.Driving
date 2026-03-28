import time
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from environment.vision import get_frame, get_speed
from environment.controls import perform_action, release_all, restart_mission


class DrDrivingEnv(gym.Env):

    def __init__(self):
        super(DrDrivingEnv, self).__init__()

        # 5 actions: idle, accelerate, brake, left, right
        self.action_space = spaces.Discrete(5)

        # observation = 84x84 grayscale image (uint8 for SB3 CnnPolicy)
        self.observation_space = spaces.Box(
            low=0,
            high=255,
            shape=(84, 84, 1),
            dtype=np.uint8
        )

        self.last_frame = None
        self._step_count = 0
        self._max_steps = 500
        self._crash_cooldown = 0

    def _process_frame(self, frame):
        # convert normalized float (0-1) to uint8 (0-255) for SB3
        return (frame * 255).astype(np.uint8)

    def _is_crashed(self, frame):
        # frame is normalized float (0-1)
        # screen goes very dark on crash
        bottom_strip = frame[65:84, :, :]
        return np.mean(bottom_strip) < 0.05

    # -------- RESET --------
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        release_all()
        time.sleep(3)  # wait for level to load

        self._step_count = 0
        self._crash_cooldown = 0
        self.last_frame = self._process_frame(get_frame())

        return self.last_frame, {}

    # -------- STEP --------
    def step(self, action):
        self._step_count += 1

        # send action to game
        perform_action(action)

        # wait for game to update
        time.sleep(0.08)

        # capture new frame
        raw_frame = get_frame()
        frame = self._process_frame(raw_frame)

        # --- reward function ---
        speed = get_speed()

        # main reward — go fast
        reward = speed * 5.0

        # small survival bonus each step
        reward += 0.5

        # penalise idle (action 0)
        if action == 0:
            reward -= 0.05

        # penalise braking (action 2)
        if action == 2:
            reward -= 0.05

        # reward accelerating (action 1)
        if action == 1:
            reward += 0.05

        # --- crash detection with cooldown ---
        terminated = False
        if self._crash_cooldown > 0:
            # still in cooldown, skip crash check
            self._crash_cooldown -= 1
        elif self._is_crashed(raw_frame):
            terminated = True
            reward = -10.0
            self._crash_cooldown = 10  # ignore next 10 steps after crash
            restart_mission()

        # truncated = hit max steps without crashing
        truncated = self._step_count >= self._max_steps

        self.last_frame = frame
        info = {"step": self._step_count, "speed": speed}

        return frame, reward, terminated, truncated, info

    # -------- CLOSE --------
    def close(self):
        release_all()