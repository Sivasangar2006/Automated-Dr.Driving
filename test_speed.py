import time
import cv2
import numpy as np
from environment.vision import get_speed

print("Press Q in debug window to quit\n")
log = []

try:
    while True:
        # Call the updated vision function with debug=True
        speed_ratio, angle, images = get_speed(debug=True)
        
        kmh = int(speed_ratio * 200)
        timestamp = time.strftime('%H:%M:%S')

        line = f"[{timestamp}] Angle: {angle:5.1f}° | Speed: {speed_ratio:.3f} | {kmh:3d} km/h"
        log.append(line)
        print(line)

        # Show debug window
        display = np.hstack([images["original"], images["mask"]])
        
        cv2.putText(display, f"Angle: {angle:.1f}", (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
        cv2.putText(display, f"Speed: {kmh} km/h", (5, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
        
        cv2.namedWindow("Speed Debug", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Speed Debug", cv2.WND_PROP_TOPMOST, 1)
        cv2.imshow("Speed Debug", display)

        if len(log) % 10 == 0:
            with open("speed_log.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(log))

        time.sleep(0.1) # Sped up slightly for smoother debugging

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass
finally:
    with open("speed_log.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(log))
    print(f"\nSaved {len(log)} readings.")
    cv2.destroyAllWindows()