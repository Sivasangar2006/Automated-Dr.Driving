import gymnasium as gym
import numpy as np
from gymnasium import spaces


class DoctorDrivingEnv(gym.Env):

    def __init__(self):
        super().__init__()

        # what actions the AI can take
        # 0 = accelerate, 1 = brake, 2 = steer left, 3 = steer right
        self.action_space = spaces.Discrete(4)

        # what the AI sees — an 84x84 grayscale image
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(84, 84, 1), dtype=np.uint8
        )

        self._step_count = 0
        self._max_steps = 500

    def _get_observation(self):
        # DUMMY — returns a random image for now
        # Person A will replace this with real screen capture later
        return np.random.randint(0, 255, (84, 84, 1), dtype=np.uint8)

    def _send_action(self, action):
        # DUMMY — does nothing for now
        # Person A will replace this with real ADB tap commands later
        pass

    def _get_reward(self):
        # DUMMY — returns a small random reward for now
        # we will design the real reward function together later
        return np.random.uniform(-0.1, 1.0)

    def _is_done(self):
        # ends the episode if max steps reached
        if self._step_count >= self._max_steps:
            return True
        return False

    def step(self, action):
        self._step_count += 1
        self._send_action(action)

        obs = self._get_observation()
        reward = self._get_reward()
        terminated = self._is_done()
        truncated = False
        info = {"step": self._step_count}

        return obs, reward, terminated, truncated, info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._step_count = 0
        obs = self._get_observation()
        return obs, {}

    def close(self):
        pass

    