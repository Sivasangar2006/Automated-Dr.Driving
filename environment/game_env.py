import time
import numpy as np
import gym
from gym import spaces

from environment.vision import get_frame
from environment.controls import perform_action, release_all, restart_mission


class DrDrivingEnv(gym.Env):

    def __init__(self):
        super(DrDrivingEnv, self).__init__()

        # 5 actions: idle, accelerate, brake, left, right
        self.action_space = spaces.Discrete(5)

        # observation = 84x84 grayscale image
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(84, 84, 1),
            dtype=np.float32
        )

        self.last_frame = None


    # -------- RESET --------
    def reset(self):
        release_all()
        time.sleep(1)
        self.last_frame = get_frame()
        return self.last_frame


    # -------- STEP --------
    def step(self, action):

        # perform action
        perform_action(action)

        # wait for game to update
        time.sleep(0.08)

        # capture new frame
        frame = get_frame()

        # reward for staying alive
        reward = 0.1

        # detect crash (mission failed screen is dark)
        if np.mean(frame) < 0.05:
            done = True
            reward = -10
            restart_mission()
        else:
            done = False

        self.last_frame = frame

        return frame, reward, done, {}


    # -------- CLOSE --------
    def close(self):
        release_all()