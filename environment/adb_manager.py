import numpy as np
import cv2
import adbutils
import time

class ADBEnvManager:
    def __init__(self, serial=None):
        self.adb = adbutils.adb
        if serial:
            try:
                # Must explicitly connect to TCP adb ports first
                self.adb.connect(serial)
                self.device = self.adb.device(serial)
            except Exception as e:
                raise RuntimeError(f"Could not connect to {serial}. Ensure you have the BlueStacks instance for this port open! Error: {e}")
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

    def execute_action(self, action):
        """
        Actions:
        0: Accel        | 1: Accel+Left   | 2: Accel+Right
        3: Coast        | 4: Coast+Left   | 5: Coast+Right
        6: Brake        | 7: Brake+Left   | 8: Brake+Right
        """
        # --- Coordinates from coords_log.txt ---
        # Gas: 297, 740
        # Brake: 102, 810
        # Wheel Left: 1239, 721
        # Wheel Right: 1548, 718
        
        commands = []
        
        # 1. Evaluate Gas/Brake
        if action in [0, 1, 2]:
            commands.append("input swipe 297 740 297 740 400") # Hold gas completely
        elif action in [6, 7, 8]:
            commands.append("input swipe 102 810 102 810 400") # Hold brake completely

        # 2. Evaluate Steering
        if action in [1, 4, 7]:
            commands.append("input tap 1239 721 &")  # Tap left wheel edge asynchronously
        elif action in [2, 5, 8]:
            commands.append("input tap 1548 718 &")  # Tap right wheel edge asynchronously

        # Execute in sequence on device
        if commands:
            # We put tap first using & so it runs in bg, then swipe blocks for 400ms holding gas
            shell_cmd = " ".join(commands)
            self.device.shell(shell_cmd)

    def release_all(self):
        pass
