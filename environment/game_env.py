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

    def _process_frame(self, frame):
        # convert normalized float (0-1) to uint8 (0-255) for SB3
        return (frame * 255).astype(np.uint8)

    def _is_crashed(self, frame):
        # Person A's improved crash detection
        # checks bottom strip of frame for darkness (road disappears on crash)
        bottom_strip = frame[65:84, :, :]
        return np.mean(bottom_strip) < 0.35

    # -------- RESET --------
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        release_all()
        time.sleep(1)

        self._step_count = 0
        self.last_frame = self._process_frame(get_frame())

        return self.last_frame, {}  # gymnasium requires (obs, info)

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
        reward = speed * 1.0

        # small survival bonus each step
        reward += 0.1

        # penalise idle (action 0)
        if action == 0:
            reward -= 0.05

        # penalise braking (action 2)
        if action == 2:
            reward -= 0.05

        # reward accelerating (action 1)
        if action == 1:
            reward += 0.05

        # crash detection using Person A's bottom strip method
        terminated = False
        if self._is_crashed(raw_frame):  # use raw float frame for crash check
            terminated = True
            reward = -10.0
            restart_mission()

        # truncated = hit max steps without crashing
        truncated = self._step_count >= self._max_steps

        self.last_frame = frame
        info = {"step": self._step_count, "speed": speed}

        return frame, reward, terminated, truncated, info

    # -------- CLOSE --------
    def close(self):
        release_all()