import time
import numpy as np

from environment.vision import get_frame, get_speed
from environment.controls import perform_action, restart_mission, finish_mission


# -----------------------------
# PARAMETERS (tune these)
# -----------------------------
OBSTACLE_THRESHOLD = 0.35   # lower = more sensitive
TURN_THRESHOLD     = 0.40   # how much difference to consider "free"
SPEED_FAST         = 0.25
SPEED_SLOW         = 0.10


def analyze_frame(frame):
    """
    Splits frame into left, center, right
    Returns brightness of each region
    """
    frame = frame.squeeze()  # (84,84)

    h, w = frame.shape

    # Focus only on lower half (road area)
    roi = frame[int(h*0.4):, :]

    left   = roi[:, :w//3]
    center = roi[:, w//3:2*w//3]
    right  = roi[:, 2*w//3:]

    return np.mean(left), np.mean(center), np.mean(right)


def decide_action(left, center, right, speed):

    # Default: always accelerate
    action = 0

    # If center looks darker → obstacle
    if center < 0.22:
        if left > right:
            action = 1  # accel left
        else:
            action = 2  # accel right

    return action


def main():
    print("🚗 Rule-based driving started...")

    step = 0

    while True:
        try:
            frame = get_frame()
            speed = get_speed()

            left, center, right = analyze_frame(frame)

            action = decide_action(left, center, right, speed)

            perform_action(action)

            # Debug print
            if step % 20 == 0:
                print(f"[{step}] speed={speed:.2f} | L={left:.2f} C={center:.2f} R={right:.2f} | action={action}")

            step += 1
            time.sleep(0.05)

        except KeyboardInterrupt:
            print("Stopped.")
            break


if __name__ == "__main__":
    main()