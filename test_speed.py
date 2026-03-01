import time
import cv2
from environment.vision import get_speed, get_speed_frame

print("Testing speed reader — drive the car and watch numbers change")
print("Press Ctrl+C to stop\n")

while True:
    gray = get_speed_frame()
    speed = get_speed()

    # draw center point and needle tip on image for debugging
    import numpy as np
    h, w = gray.shape
    cx, cy = w // 2, h // 2

    display = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    cv2.circle(display, (cx, cy), 3, (0, 255, 0), -1)  # green center dot

    # show speed value on image
    cv2.putText(display, f"Speed: {speed:.2f}", (5, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    cv2.imshow("Speedometer Debug", display)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    bar = "█" * int(speed * 30)
    print(f"Speed: {speed:.3f} |{bar:<30}|", end="\r")
    time.sleep(0.1)

cv2.destroyAllWindows()