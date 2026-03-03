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
# ---- SPEEDOMETER AREA --------
# ==============================
SPEED_MONITOR = {
    "top":    833,
    "left":   506,
    "width":  753 - 506,
    "height": 1060 - 833
}

sct = mss.mss()


# ===============================
# 84x84 GAME FRAME (FOR RL AGENT)
# ===============================
def get_frame():
    img = np.array(sct.grab(MONITOR))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (84, 84), interpolation=cv2.INTER_AREA)
    normalized = resized / 255.0

    frame = np.expand_dims(normalized, axis=-1)
    return frame


# ===============================
# SPEEDOMETER IMAGE
# ===============================
def get_speed_frame():
    img = np.array(sct.grab(SPEED_MONITOR))
    img = img[:, :, :3]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray


# ===============================
# NEEDLE SPEED DETECTOR (FINAL)
# ===============================
def get_speed():

    img = np.array(sct.grab(SPEED_MONITOR))
    img = img[:, :, :3]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # Correct center of dial
    cx = int(w * 0.50)
    cy = int(h * 0.62)

    # Edge detection (no color filtering)
    edges = cv2.Canny(gray, 80, 200)

    # Detect straight lines
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=60,
        minLineLength=40,
        maxLineGap=10
    )

    if lines is None:
        return get_speed.last_speed if hasattr(get_speed, "last_speed") else 0.0

    # Find line closest to dial center
    best_line = None
    best_dist = 999999

    for line in lines:
        x1, y1, x2, y2 = line[0]
        mx, my = (x1 + x2) // 2, (y1 + y2) // 2
        dist = np.sqrt((mx - cx)**2 + (my - cy)**2)

        if dist < best_dist:
            best_dist = dist
            best_line = (x1, y1, x2, y2)

    x1, y1, x2, y2 = best_line

    # Pick farthest endpoint as needle tip
    d1 = np.sqrt((x1 - cx)**2 + (y1 - cy)**2)
    d2 = np.sqrt((x2 - cx)**2 + (y2 - cy)**2)

    tip = (x1, y1) if d1 > d2 else (x2, y2)

    # Calculate angle
    angle = np.degrees(np.arctan2(cy - tip[1], tip[0] - cx))
    if angle < 0:
        angle += 360

    # --- CALIBRATION ---
    # Measure from your dial:
    # At 0 mph -> around 182 degrees
    # At 200 mph -> around 138 degrees

    ANGLE_STOP = 182.0
    ANGLE_MAX = 138.0

    angle_clamped = max(min(angle, ANGLE_STOP), ANGLE_MAX)

    speed_ratio = (ANGLE_STOP - angle_clamped) / (ANGLE_STOP - ANGLE_MAX)
    speed_ratio = float(np.clip(speed_ratio, 0.0, 1.0))

    # Smooth
    if not hasattr(get_speed, "last_speed"):
        get_speed.last_speed = speed_ratio

    alpha = 0.2
    speed_ratio = alpha * speed_ratio + (1 - alpha) * get_speed.last_speed
    get_speed.last_speed = speed_ratio

    speed_mph = speed_ratio * 200.0

    print(f"ANGLE: {angle:.2f} | SPEED: {speed_mph:.1f} MPH")

    return speed_ratio