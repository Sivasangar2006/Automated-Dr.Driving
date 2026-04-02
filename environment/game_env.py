import time
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from environment.vision import get_frame, get_speed
from environment.controls import perform_action, release_all, restart_mission, finish_mission

# -------------------------------------------------------
# CURRICULUM PHASE
#   1 = Phase 1: straight-line only, learn speed control
#   2 = Phase 2: full steering + obstacle avoidance  ← ACTIVE
# -------------------------------------------------------
PHASE = 2


class DrDrivingEnv(gym.Env):

    def __init__(self):
        super(DrDrivingEnv, self).__init__()

        self.action_space = spaces.Discrete(3)  # 0=straight, 1=left, 2=right

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
        """Crash = bottom strip goes nearly black"""
        bottom_strip = frame[65:84, :, :]
        return np.mean(bottom_strip) < 0.05

    def _is_finished(self, frame):
        """
        Finish line = the game overlays a bright win screen.
        Detected when the ENTIRE frame becomes very bright (mean > 0.85).
        Normal driving frames are much darker (roads, cars, sky).
        """
        return np.mean(frame) > 0.85

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        time.sleep(1)

        self._step_count = 0
        self.prev_speed = 0.0

        frame = self._process_frame(get_frame())
        return frame, {}

    def step(self, action):
        self._step_count += 1

        # Warm-up: force straight for the first 20 steps regardless of phase
        if self._step_count < 20:
            action = 0

        # Phase 1 override: no steering allowed
        if PHASE == 1:
            action = 0

        # Read frame + speed BEFORE acting
        raw_frame = get_frame()
        frame = self._process_frame(raw_frame)
        speed = get_speed()

        perform_action(action, speed=speed)
        time.sleep(0.08)

        # ── Reward (Phase 2: survival-first) ─────────────────────
        #
        #   PRIMARY GOAL   → stay alive as long as possible
        #   SECONDARY GOAL → cruise near 55-65 km/h
        #   TERTIARY GOAL  → prefer going straight (steer only when needed)
        #
        #   +0.05/step  → alive and moving (survival bonus)
        #   +0.50       → speed in acceptable range (45–70 km/h)
        #   -0.30       → speed out of acceptable range
        #   -0.20       → steering penalty (left or right action)
        #   -10.0       → crash (overrides everything)
        #
        #   Steering penalty logic:
        #     The model WILL still steer to avoid a crash because
        #     avoiding -10.0 is worth far more than -0.20 penalty.
        #     But it won't randomly steer for no reason.
        # ─────────────────────────────────────────────────────────
        SPEED_OK_MIN = 0.225  # 45 km/h — below this = too slow
        SPEED_OK_MAX = 0.35   # 70 km/h — above this = too fast

        reward = 0.05         # survival bonus every step

        if SPEED_OK_MIN <= speed <= SPEED_OK_MAX:
            reward += 0.50    # in acceptable speed range
        else:
            reward -= 0.30    # too slow or too fast

        # Steering penalty — discourage random left/right
        if action in (1, 2):
            reward -= 0.20

        terminated = False

        if self._is_finished(raw_frame):
            # Reached the finish line — big reward, then restart
            terminated = True
            reward = +50.0
            print(f"[FINISH LINE] Reached finish at step {self._step_count}! 🏆")
            finish_mission()

        elif self._is_crashed(raw_frame):
            # Crashed into a car or wall
            terminated = True
            reward = -10.0
            restart_mission()

        truncated = self._step_count >= self._max_steps

        info = {
            "phase": PHASE,
            "speed": speed,
            "speed_kmh": round(speed * 200, 1),
            "reward": reward,
            "action": action,
            "step": self._step_count,
        }

        return frame, reward, terminated, truncated, info

    def close(self):
        release_all()