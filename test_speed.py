import time
import cv2
import numpy as np
import mss
from environment.vision import get_speed, SPEED_MONITOR

sct = mss.mss()

print("Press Q in debug window to quit\n")

log = []

try:
    while True:
        img = np.array(sct.grab(SPEED_MONITOR))
        img = img[:, :, :3]
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, w = img.shape[:2]
        cx, cy = w // 2, h // 2

        # red mask
        mask1 = cv2.inRange(hsv, np.array([0,   120, 70]), np.array([10,  255, 255]))
        mask2 = cv2.inRange(hsv, np.array([170, 120, 70]), np.array([180, 255, 255]))
        red_mask = cv2.bitwise_or(mask1, mask2)

        # donut mask
        donut = np.zeros_like(red_mask)
        cv2.circle(donut, (cx, cy), int(min(h,w)*0.48), 255, -1)
        cv2.circle(donut, (cx, cy), int(min(h,w)*0.12), 0,   -1)
        needle_mask = cv2.bitwise_and(red_mask, donut)

        speed = get_speed()
        kmh = int(speed * 200)
        timestamp = time.strftime('%H:%M:%S')

        # log to list
        line = f"[{timestamp}] Speed: {speed:.3f}  |  {kmh:3d} MPH"
        log.append(line)
        print(line)

        # show debug window always on top
        display = np.hstack([
            img,
            cv2.cvtColor(red_mask,    cv2.COLOR_GRAY2BGR),
            cv2.cvtColor(needle_mask, cv2.COLOR_GRAY2BGR),
        ])
        cv2.putText(display, f"Speed: {speed:.3f} = {kmh} km/h", (5, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        cv2.putText(display, "Original",    (5,     h-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 1)
        cv2.putText(display, "Red Mask",    (w+5,   h-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 1)
        cv2.putText(display, "Needle Only", (w*2+5, h-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 1)

        cv2.namedWindow("Speed Debug", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Speed Debug", cv2.WND_PROP_TOPMOST, 1)
        cv2.imshow("Speed Debug", display)

        # save log every 10 readings automatically
        if len(log) % 10 == 0:
            with open("speed_log.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(log))

        time.sleep(0.5)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass

finally:
    # always save on exit
    with open("speed_log.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(log))
    print(f"\n\nSaved {len(log)} readings to speed_log.txt")
    cv2.destroyAllWindows()