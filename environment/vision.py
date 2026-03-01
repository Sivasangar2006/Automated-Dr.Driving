import numpy as np
import cv2
import mss

# ---- GAME SCREEN AREA ----
MONITOR = {
    "top":    157,
    "left":   43,
    "width":  1591 - 43,
    "height": 659 - 157
}

# ---- SPEEDOMETER AREA (Person A's coordinates) ----
SPEED_MONITOR = {
    "top":    862,
    "left":   564,
    "width":  706 - 564,
    "height": 1030 - 862
}

sct = mss.mss()


def get_frame():
    """
    Captures the game screen and returns an 84x84 grayscale frame.
    This is what the AI 'sees'.
    """
    # capture screen
    img = np.array(sct.grab(MONITOR))

    # convert BGR -> gray
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # resize to 84x84
    resized = cv2.resize(gray, (84, 84), interpolation=cv2.INTER_AREA)

    # normalize 0-255 -> 0-1
    normalized = resized / 255.0

    # add channel dimension (84,84) -> (84,84,1)
    frame = np.expand_dims(normalized, axis=-1)

    return frame


def get_speed_frame():
    """
    Captures just the speedometer region.
    Returns raw grayscale image of the dial.
    """
    img = np.array(sct.grab(SPEED_MONITOR))
    img = img[:, :, :3]  # remove alpha channel
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray


def get_speed():
    """
    Reads the speedometer and returns a speed value between 0.0 and 1.0.
    Uses needle angle detection via OpenCV.
    0.0 = fully stopped, 1.0 = max speed (200 km/h)
    """
    gray = get_speed_frame()

    if gray is None or gray.size == 0:
        return 0.0

    # find center of dial
    h, w = gray.shape
    cx, cy = w // 2, h // 2

    # threshold to isolate the needle
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # find white pixels (the needle)
    points = cv2.findNonZero(thresh)

    if points is None:
        return 0.0  # no needle detected, assume stopped

    # find the tip of the needle (furthest point from center)
    points = points.reshape(-1, 2)
    distances = np.sqrt((points[:, 0] - cx)**2 + (points[:, 1] - cy)**2)
    tip = points[np.argmax(distances)]

    # calculate needle angle
    angle = np.degrees(np.arctan2(tip[1] - cy, tip[0] - cx))

    # needle goes from ~-220 degrees (0 km/h) to ~40 degrees (200 km/h)
    # adjust these if speed reading feels wrong
    min_angle = -220.0
    max_angle =   40.0
    speed = (angle - min_angle) / (max_angle - min_angle)
    speed = float(np.clip(speed, 0.0, 1.0))

    return speed