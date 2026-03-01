import numpy as np
import cv2
import mss

# =========================
# ---- GAME SCREEN AREA ---
# =========================
MONITOR = {
    "top":    157,
    "left":   43,
    "width":  1591 - 43,
    "height": 659 - 157
}

# ==============================
# ---- SPEEDOMETER AREA (NEW) ---
# ==============================
# Top Left:     (506, 833)
# Bottom Right: (753, 1060)

SPEED_MONITOR = {
    "top":    833,
    "left":   506,
    "width":  753 - 506,
    "height": 1060 - 833
}

sct = mss.mss()


def get_frame():
    """
    Captures the game screen and returns an 84x84 grayscale frame.
    This is what the AI 'sees'.
    """
    img = np.array(sct.grab(MONITOR))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    resized = cv2.resize(gray, (84, 84), interpolation=cv2.INTER_AREA)

    normalized = resized / 255.0

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
    0.0 = stopped
    1.0 = max speed (~200 km/h)
    """
    gray = get_speed_frame()

    if gray is None or gray.size == 0:
        return 0.0

    h, w = gray.shape
    cx, cy = w // 2, h // 2

    # Slightly lower threshold to better capture needle
    _, thresh = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)

    points = cv2.findNonZero(thresh)

    if points is None:
        return 0.0

    points = points.reshape(-1, 2)

    distances = np.sqrt((points[:, 0] - cx)**2 +  (points[:, 1] - cy)**2)

    tip = points[np.argmax(distances)]

    angle = np.degrees(np.arctan2(tip[1] - cy, tip[0] - cx))

    # These may require small tuning later
    min_angle = -220.0
    max_angle =  40.0

    speed = (angle - min_angle) / (max_angle - min_angle)
    speed = float(np.clip(speed, 0.0, 1.0))

    return speed