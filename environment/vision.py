import numpy as np
import cv2
import mss

# ---- CAMERA AREA (your coordinates) ----
MONITOR = {
    "top": 157,
    "left": 43,
    "width": 1591 - 43,
    "height": 659 - 157
}

sct = mss.mss()

def get_frame():
    """
    Captures the game screen and returns an 84x84 grayscale frame.
    This is what the AI 'sees'.
    """

    # Capture screen
    img = np.array(sct.grab(MONITOR))

    # Convert BGR -> Gray
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Resize to Atari-style observation
    resized = cv2.resize(gray, (84, 84), interpolation=cv2.INTER_AREA)

    # Normalize (0–255 -> 0–1)
    normalized = resized / 255.0

    # Add channel dimension (84,84) -> (84,84,1)
    frame = np.expand_dims(normalized, axis=-1)

    return frame