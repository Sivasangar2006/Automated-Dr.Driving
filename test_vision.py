from environment.vision import get_frame
import cv2

while True:
    frame = get_frame()

    # convert normalized image back to display
    img = (frame.squeeze() * 255).astype("uint8")

    cv2.imshow("AI Camera", img)

    if cv2.waitKey(1) == 27:   # press ESC to close
        break

cv2.destroyAllWindows()