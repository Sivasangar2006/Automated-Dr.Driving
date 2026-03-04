import numpy as np
import cv2
import mss

MONITOR = {"top": 157, "left": 43, "width": 1548, "height": 502}
SPEED_MONITOR = {"top": 833, "left": 506, "width": 247, "height": 227}
sct = mss.mss()

def get_frame():
    img = np.array(sct.grab(MONITOR))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (84, 84), interpolation=cv2.INTER_AREA)
    normalized = resized / 255.0
    return np.expand_dims(normalized, axis=-1)

def get_speed(debug=False):
    """
    Returns (speed_ratio, debug_images_dict) if debug=True
    Otherwise returns just speed_ratio
    """
    img = np.array(sct.grab(SPEED_MONITOR))
    img = img[:, :, :3]
    h, w = img.shape[:2]
    
    cx = int(w * 0.50)
    cy = int(h * 0.62)

    # 1. Isolate the Red Needle (Moved from your test script)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, np.array([0,   120, 70]), np.array([10,  255, 255]))
    mask2 = cv2.inRange(hsv, np.array([170, 120, 70]), np.array([180, 255, 255]))
    red_mask = cv2.bitwise_or(mask1, mask2)

    donut = np.zeros_like(red_mask)
    cv2.circle(donut, (cx, cy), int(min(h, w) * 0.48), 255, -1)
    cv2.circle(donut, (cx, cy), int(min(h, w) * 0.12), 0, -1)
    needle_mask = cv2.bitwise_and(red_mask, donut)

    # 2. Find the Needle Tip using Contours
    contours, _ = cv2.findContours(needle_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    speed_ratio = get_speed.last_speed if hasattr(get_speed, "last_speed") else 0.0
    angle = 0.0

    if contours:
        # Get the largest red blob
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Find the point in the contour furthest from the center
        best_dist = -1
        tip = (cx, cy)
        for point in largest_contour:
            px, py = point[0]
            dist = (px - cx)**2 + (py - cy)**2
            if dist > best_dist:
                best_dist = dist
                tip = (px, py)

        # 3. Calculate Angle
        # Using standard math: 0° is right, 90° is up. 
        angle = np.degrees(np.arctan2(cy - tip[1], tip[0] - cx))
        if angle < 0:
            angle += 360

       # --- NEW CALIBRATION BASED ON VIDEO ---
    # ---- SPEED CALIBRATION ----

    ANGLE_STOP = 190.0   # needle at 0 km/h (far right)
    ANGLE_MAX  = 60.0    # needle at 200 km/h (far left)

    speed_ratio = (ANGLE_STOP - angle) / (ANGLE_STOP - ANGLE_MAX)

    speed_ratio = float(np.clip(speed_ratio, 0.0, 1.0))
    # 4. Smooth the output
    if not hasattr(get_speed, "last_speed"):
        get_speed.last_speed = speed_ratio

    alpha = 0.2
    speed_ratio = alpha * speed_ratio + (1 - alpha) * get_speed.last_speed
    get_speed.last_speed = speed_ratio

    if debug:
        # Draw debug visuals
        debug_img = img.copy()
        cv2.circle(debug_img, (cx, cy), 3, (255, 0, 0), -1) # Center
        if contours:
            cv2.circle(debug_img, tip, 5, (0, 255, 0), -1)  # Tip
            cv2.line(debug_img, (cx, cy), tip, (0, 255, 0), 2) # Needle line
        
        return speed_ratio, angle, {
            "original": debug_img,
            "mask": cv2.cvtColor(needle_mask, cv2.COLOR_GRAY2BGR)
        }

    return speed_ratio