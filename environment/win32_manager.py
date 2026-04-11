import win32gui
import win32con
import win32api

class Win32Manager:
    def __init__(self, window_title):
        self.window_title = window_title
        self.hwnd = win32gui.FindWindow(None, self.window_title)
        if not self.hwnd:
            raise RuntimeError(f"Could not find window exclusively named '{self.window_title}'.")
        print(f"Bound to Win32 Handle: {self.hwnd} for {self.window_title}")
        self.active_keys = []

    def set_key(self, key_hex, state):
        """
        Sends background keystrokes directly to the application layer.
        """
        if state:
            # lparam 0 often works for generic down
            win32api.PostMessage(self.hwnd, win32con.WM_KEYDOWN, key_hex, 0)
        else:
            # lparam MUST have the transition bit set (bit 31) for BlueStacks to register the release!
            win32api.PostMessage(self.hwnd, win32con.WM_KEYUP, key_hex, 0xC0000001)

    def execute_action(self, action):
        """
        Actions:
        0: Accel        | 1: Accel+Left   | 2: Accel+Right
        3: Coast        | 4: Coast+Left   | 5: Coast+Right
        6: Brake        | 7: Brake+Left   | 8: Brake+Right
        """
        # Define virtual keys
        VK_UP    = 0x26
        VK_DOWN  = 0x28
        VK_LEFT  = 0x25
        VK_RIGHT = 0x27

        # Determine target keys for the current frame
        target_keys = set()

        if action in [0, 1, 2]: target_keys.add(VK_UP)
        elif action in [6, 7, 8]: target_keys.add(VK_DOWN)

        if action in [1, 4, 7]: target_keys.add(VK_LEFT)
        elif action in [2, 5, 8]: target_keys.add(VK_RIGHT)

        # 1. Release keys that are no longer active
        for key in list(self.active_keys):
            if key not in target_keys:
                self.set_key(key, False)
                self.active_keys.remove(key)

        # 2. Press newly active keys
        for key in target_keys:
            if key not in self.active_keys:
                self.set_key(key, True)
                self.active_keys.append(key)

    def release_all(self):
        for key in self.active_keys:
            self.set_key(key, False)
        self.active_keys.clear()
