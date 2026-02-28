import cv2
from environment.vision import get_speed_frame
import time

print("Showing speedometer capture... Press Q to quit")

while True:
    frame = get_speed_frame()

    cv2.imshow("Speedometer", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()