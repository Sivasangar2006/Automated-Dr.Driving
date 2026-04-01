import time
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from environment.vision import get_frame, get_speed
from environment.controls import perform_action, release_all, restart_mission

class DrDrivingEnv(gym.Env):

    def __init__(self):
        super(DrDrivingEnv, self).__init__()

        self.action_space = spaces.Discrete(3)

        self.observation_space = spaces.Box(
            low=0,
            high=255,
            shape=(84, 84, 1),
            dtype=np.uint8
        )

        self._step_count = 0
        self._max_steps = 500
        self.prev_speed = 0.0

    def _process_frame(self, frame):
        return (frame * 255).astype(np.uint8)

    def _is_crashed(self, frame):
        bottom_strip = frame[65:84, :, :]
        return np.mean(bottom_strip) < 0.05

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        time.sleep(1)

        self._step_count = 0
        self.prev_speed = 0.0

        frame = self._process_frame(get_frame())
        return frame, {}

    def step(self, action):
        self._step_count += 1

        if self._step_count < 20:
            action = 0

        perform_action(action)
        time.sleep(0.08)

        raw_frame = get_frame()
        frame = self._process_frame(raw_frame)

        speed = get_speed()
        reward = 0.0

        target_min = 0.30
        target_max = 0.35

        if target_min <= speed <= target_max:
            reward += 2.0
        elif speed < target_min:
            reward -= 0.5
        elif speed > target_max:
            reward -= 1.0

        terminated = False

        if self._is_crashed(raw_frame):
            terminated = True
            reward = -10.0
            restart_mission()

        truncated = self._step_count >= self._max_steps

        info = {
            "speed": speed,
            "reward": reward,
            "action": action
        }

        return frame, reward, terminated, truncated, info

    def close(self):
        release_all()