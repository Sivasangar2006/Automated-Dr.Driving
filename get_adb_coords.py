import adbutils
import cv2
import numpy as np

def main():
    print("Conencting to BlueStacks port 5555...")
    try:
        d = adbutils.adb.device("127.0.0.1:5555")
    except Exception as e:
        print("Device offline or not found:", e)
        return
        
    print("Grabbing screenshot over ADB...")
    png = d.shell("screencap -p", encoding=None)
    img = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)
    
    if img is None:
        print("Failed to pull frame. Make sure Dr. Driving is open.")
        return

    coords = {}
    points_to_click = ["Gas Pedal (Bottom Right)", "Brake Pedal (Bottom Left)", "Steering Wheel (Middle Left Edge)", "Steering Wheel (Middle Right Edge)"]
    
    print("\n" + "="*50)
    print("A window will open showing your game.")
    print("Please click on each item exactly as prompted in the console.")
    print("="*50 + "\n")
    
    cv2.namedWindow("Map Coordinates", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Map Coordinates", 800, 450) # Scale it if it's too big
    
    current_idx = 0
    
    def on_mouse(event, x, y, flags, param):
        nonlocal current_idx
        if event == cv2.EVENT_LBUTTONDOWN:
            if current_idx < len(points_to_click):
                name = points_to_click[current_idx]
                coords[name] = (x, y) # Native pixel mapping usually matches scaled cv2.imshow without param scaling if it's WINDOW_NORMAL, wait no! 
                # If we resize with WINDOW_NORMAL, x,y are relative to the raw image data, not the screen space! This is perfect!
                print(f"✅ Picked {name} -> X: {x}, Y: {y}")
                
                cv2.circle(img, (x, y), 20, (0, 255, 0), -1)
                cv2.imshow("Map Coordinates", img)
                
                current_idx += 1
                if current_idx < len(points_to_click):
                    print(f"👉 Next, click: {points_to_click[current_idx]}")
                else:
                    print("\n🎉 All done! You can press any key to close the window.")
                    with open("coords_log.txt", "w") as f:
                        f.write(str(coords))

    print(f"👉 First, click: {points_to_click[0]}")
    cv2.imshow("Map Coordinates", img)
    cv2.setMouseCallback("Map Coordinates", on_mouse)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("Window closed. Coordinates saved!")

if __name__ == "__main__":
    main()
