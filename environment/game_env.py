import time
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from environment.vision import get_frame, get_speed
from environment.controls import perform_action, release_all, restart_mission


class DrDrivingEnv(gym.Env):

    def __init__(self):
        super(DrDrivingEnv, self).__init__()

        # 🔥 REDUCED ACTION SPACE
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
        return np.mean(bottom_strip) < 0.35

    def _lane_reward(self, frame):
        h, w, _ = frame.shape
        center = frame[:, w//3:2*w//3]
        brightness = np.mean(center)
        return 1.0 - brightness

    # -------- RESET --------
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        time.sleep(1)

        self._step_count = 0
        self.prev_speed = 0.0

        frame = self._process_frame(get_frame())
        return frame, {}

    # -------- STEP --------
    def step(self, action):
        self._step_count += 1

        # 🔥 FORCE SAFE START
        if self._step_count < 20:
            action = 0  # straight

        # 🔥 MAP ACTIONS
        # 0 = straight
        # 1 = left
        # 2 = right

        perform_action(action)
        time.sleep(0.08)

        raw_frame = get_frame()
        frame = self._process_frame(raw_frame)

        # =========================
        # REWARD
        # =========================
        speed = get_speed()
        reward = 0.0

        reward += speed * 2.0

        if speed > 0.6:
            reward += 0.1

        lane_reward = self._lane_reward(raw_frame)
        reward += lane_reward * 1.5

        speed_diff = speed - self.prev_speed
        reward += speed_diff * 2.0

        self.prev_speed = speed

        if speed < 0.2:
            reward -= 0.2

        # 🔥 STRONG STRAIGHT BIAS
        if action == 0:
            reward += 0.1
        else:
            reward -= 0.05

        # =========================
        # TERMINATION
        # =========================
        terminated = False

        if self._is_crashed(raw_frame):
            terminated = True
            reward = -8.0
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