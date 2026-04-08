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

# -------------------------------------------------------
# FRAME SKIPPING
#   The agent decides once, then the action is held for
#   FRAME_SKIP game frames before the next decision.
#   Each RL step is therefore richer — 4× more game time
#   per training decision → fewer total steps to converge.
# -------------------------------------------------------
FRAME_SKIP  = 4      # frames per decision
STEP_SLEEP  = 0.02  # seconds per frame (was 0.08 for 1 frame)


class DrDrivingEnv(gym.Env):

    def __init__(self):
        super(DrDrivingEnv, self).__init__()

        self.action_space = spaces.Discrete(9)  # 3 speed states × 3 steer states

        self.observation_space = spaces.Box(
            low=0,
            high=255,
            shape=(84, 84, 1),
            dtype=np.uint8
        )

        self._step_count = 0
        self._max_steps = 500
        self.prev_speed = 0.0
        self._stall_since = None   # timestamp when speed first dropped to ~0

    def _process_frame(self, frame):
        return (frame * 255).astype(np.uint8)

    def _is_crashed(self, frame):
        """
        Detects the brief dark flash when the car first hits something.
        Threshold raised to 0.10 to be more sensitive.
        NOTE: The 'Mission Failed' screen itself is NOT dark — it is
        handled by stall detection (speed stays 0 on that screen).
        """
        bottom_strip = frame[65:84, :, :]
        return np.mean(bottom_strip) < 0.10

    def _is_finished(self, frame):
        """
        Finish line = the game overlays a bright win screen.
        Detected when the ENTIRE frame becomes very bright (mean > 0.85).
        Normal driving frames are much darker (roads, cars, sky).
        """
        return np.mean(frame) > 0.85

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        time.sleep(0.4)  # ⚡ reduced: was 1.0s

        self._step_count = 0
        self.prev_speed = 0.0
        self._stall_since = None

        frame = self._process_frame(get_frame())
        return frame, {}

    def step(self, action):
        self._step_count += 1

        # Warm-up: force accelerate-straight for the first 20 steps
        if self._step_count < 20:
            action = 0  # Accelerate + Straight

        # Phase 1 override: no steering allowed
        if PHASE == 1:
            action = 0

        # ── ACT ──────────────────
        # Send keys once per RL step instead of 4 times (prevents jitter)
        perform_action(action)

        # ── WAIT ─────────────────
        # Wait for frame-skip
        for _ in range(FRAME_SKIP):
            time.sleep(STEP_SLEEP)

        # ── OBSERVE ──────────────
        # Capture frame/speed AFTER acting (fixes "brain lag")
        raw_frame = get_frame()
        frame     = self._process_frame(raw_frame)
        speed     = get_speed()

        # ── Reward (Phase 2: full AI control) ────────────────────────────────
        #
        #   The AI controls acceleration, coasting, AND braking.
        #   Reward logic encourages:
        #     - Fast driving on clear road
        #     - Coasting (not braking) when dodging — your key insight
        #     - Hard braking only when truly necessary
        #     - Staying alive above everything else
        #
        #   +0.05        → survival bonus every step
        #   +0.30        → speed > 50 km/h  (good cruising)
        #   +0.10        → speed 20–50 km/h (coasting through obstacle zone ✅)
        #   -0.20        → speed < 20 km/h  (too slow, nearly stopped)
        #   -0.03        → coast action (small, don't coast needlessly)
        #   -0.07        → brake action  (more aggressive, use sparingly)
        #   -0.15        → any steering   (steer only when needed)
        #   -10.0        → crash / stall  (overrides everything)
        #   +50.0        → finish line 🏆
        # ─────────────────────────────────────────────────────────────────────

        reward = 0.05   # survival bonus every step

        # Speed reward — nuanced: coasting is acceptable, not punished
        if speed > 0.25:          # > 50 km/h — good speed
            reward += 0.30
        elif speed > 0.10:        # 20–50 km/h — coasting (OK near obstacles)
            reward += 0.10
        else:                     # < 20 km/h — nearly stopped
            reward -= 0.20

        # Coast penalty — small, discourages pointless coasting on clear road
        if action in (3, 4, 5):
            reward -= 0.03

        # Brake penalty — more expensive, use only when truly needed
        if action in (6, 7, 8):
            reward -= 0.07

        # Steering penalty — prefer straight, steer only to avoid crashes
        if action in (1, 2, 4, 5, 7, 8):
            reward -= 0.15

        terminated = False

        # ── Stall detection: speedometer near 0 for > 3 seconds ──
        # Catches the "Mission Failed" screen and any other freeze.
        # Time-based is more reliable than step-counting since
        # step rate varies with CPU load.
        STALL_SPEED     = 0.02   # anything below this = "stopped"
        STALL_TIMEOUT   = 3.0    # seconds before forcing restart
        STALL_GRACE     = 30     # ignore stall during warmup steps

        if self._step_count > STALL_GRACE and speed < STALL_SPEED:
            if self._stall_since is None:
                self._stall_since = time.time()   # start the clock
            elif time.time() - self._stall_since >= STALL_TIMEOUT:
                print(f"[STALL] Speed near 0 for >3s at step {self._step_count} — forcing restart")
                terminated = True
                reward = -10.0
                self._stall_since = None
                restart_mission()
        else:
            self._stall_since = None              # reset clock when moving

        if not terminated:
            if self._is_finished(raw_frame):
                # Reached the finish line — big reward, then restart
                terminated = True
                reward = +50.0
                print(f"[FINISH LINE] Reached finish at step {self._step_count}! 🏆")
                finish_mission()

            elif self._is_crashed(raw_frame):
                # Crashed into a car or wall (screen went dark)
                terminated = True
                reward = -10.0
                restart_mission()

        truncated = self._step_count >= self._max_steps

        info = {
            "phase":     PHASE,
            "speed":     speed,
            "speed_kmh": round(speed * 200, 1),
            "reward":    reward,
            "action":    action,
            "action_name": [
                "Accel+Straight", "Accel+Left",  "Accel+Right",
                "Coast+Straight", "Coast+Left",  "Coast+Right",
                "Brake+Straight", "Brake+Left",  "Brake+Right",
            ][action],
            "step":      self._step_count,
        }

        return frame, reward, terminated, truncated, info

    def close(self):
        release_all()