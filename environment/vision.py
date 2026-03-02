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
    img = np.array(sct.grab(SPEED_MONITOR))
    img = img[:, :, :3]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, w = img.shape[:2]
    cx, cy = w // 2, h // 2

    # detect orange-red needle
    lower_red1 = np.array([0,   80, 80])
    upper_red1 = np.array([20, 255, 255])
    lower_red2 = np.array([160, 80, 80])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    # only look at BOTTOM HALF of dial where needle sweeps
    # this cuts out the top text and markings
    bottom_mask = np.zeros_like(red_mask)
    bottom_mask[cy:, :] = 255
    needle_mask = cv2.bitwise_and(red_mask, bottom_mask)

    points = cv2.findNonZero(needle_mask)
    if points is None:
        return 0.0

    points = points.reshape(-1, 2)

    # use the rightmost red pixel X position as speed indicator
    # leftmost X = 0 km/h, rightmost X = 200 km/h
    min_x = int(w * -0.55)   # left boundary
    max_x = int(w * 2.0)   # right boundary
    tip_x = int(np.mean(points[:, 0]))  # average X of all needle pixels

    speed = (tip_x - min_x) / (max_x - min_x)
    speed = float(np.clip(speed, 0.0, 1.0))

    return speed