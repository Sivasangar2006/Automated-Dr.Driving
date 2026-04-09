import numpy as np
import cv2
import adbutils
import time

class ADBEnvManager:
    def __init__(self, serial=None):
        self.adb = adbutils.adb
        if serial:
            self.device = self.adb.device(serial)
        else:
            # Auto-connect if none provided
            devices = self.adb.device_list()
            if not devices:
                raise RuntimeError("No ADB devices connected. Please connect Bluestacks and try again.")
            self.device = devices[0]
            
        print(f"Connected to device: {self.device.serial}")

    def get_frame(self):
        """
        Grabs a frame using adb exec-out screencap.
        This captures the native Android screen.
        """
        # screencap with -p outputs PNG data. We stream it directly to memory.
        png_bytes = self.device.shell("screencap -p", encoding=None)
        
        # Decode the image directly from the byte stream
        nparr = np.frombuffer(png_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
             # Sometimes the capture fails or stream is corrupted
             return np.zeros((84, 84, 1), dtype=np.uint8)

        # Process the image for the model
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # You may need to crop out black bars depending on emulator resolution here
        # Example crop: gray = gray[100:-100, :] 
        
        resized = cv2.resize(gray, (84, 84), interpolation=cv2.INTER_AREA)
        normalized = resized / 255.0
        return np.expand_dims(normalized, axis=-1)

    def tap(self, x, y):
        self.device.shell(f"input tap {x} {y}")

    def hold_button(self, x, y, duration_ms):
        """
        Simulate holding a button by performing a 0-distance swipe over duration.
        """
        self.device.shell(f"input swipe {x} {y} {x} {y} {duration_ms}")
        
    def release_all(self):
        # With ADB, touch events complete based on their duration.
        # However, to be safe, we can send a dummy tap to interrupt.
        pass
