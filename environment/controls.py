import pygetwindow as gw
import pyautogui
import time

pyautogui.FAILSAFE = False

# retry button coordinates
RETRY_BUTTON = (1752, 974)

# ─────────────────────────────────────────────────────────────
# KEY STATE TRACKING (IMPORTANT FIX)
# ─────────────────────────────────────────────────────────────
current_keys = {
    "up": False,
    "down": False,
    "left": False,
    "right": False
}


def set_key(key, state):
    """
    Press/release key ONLY if state changes.
    Prevents spamming and enables smooth control.
    """
    global current_keys

    if current_keys[key] != state:
        if state:
            pyautogui.keyDown(key)
        else:
            pyautogui.keyUp(key)

        current_keys[key] = state


# ─────────────────────────────────────────────────────────────
# ACTION EXECUTION (SMOOTH CONTROL)
# ─────────────────────────────────────────────────────────────
def perform_action(action: int):
    """
    Executes action WITHOUT resetting keys every frame.
    Enables continuous acceleration and smooth steering.
    """

    # --- Speed control ---
    set_key("up", action in (0, 1, 2))      # Accelerate
    set_key("down", action in (6, 7, 8))    # Brake

    # --- Steering ---
    set_key("left", action in (1, 4, 7))
    set_key("right", action in (2, 5, 8))


# ─────────────────────────────────────────────────────────────
# RELEASE ALL KEYS
# ─────────────────────────────────────────────────────────────
def release_all():
    global current_keys

    for key in current_keys:
        pyautogui.keyUp(key)
        current_keys[key] = False


# ─────────────────────────────────────────────────────────────
# RESTART FUNCTION
# ─────────────────────────────────────────────────────────────
def restart_mission():
    release_all()

    time.sleep(0.6)

    windows = gw.getWindowsWithTitle("BlueStacks")
    if len(windows) > 0:
        win = windows[0]
        win.activate()
        time.sleep(0.2)

    # Click 1
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.05)
    pyautogui.click()
    time.sleep(0.5)

    # Click 2
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.05)
    pyautogui.click()
    time.sleep(0.3)

    # Click 3 (safety)
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.05)
    pyautogui.click()

    time.sleep(1.2)


# ─────────────────────────────────────────────────────────────
# FINISH FUNCTION
# ─────────────────────────────────────────────────────────────
def finish_mission():
    release_all()

    time.sleep(0.6)

    windows = gw.getWindowsWithTitle("BlueStacks")
    if len(windows) > 0:
        win = windows[0]
        win.activate()
        time.sleep(0.2)

    # Click 1
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.05)
    pyautogui.click()
    time.sleep(0.5)

    # Click 2
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.05)
    pyautogui.click()
    time.sleep(0.3)

    # Click 3
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.05)
    pyautogui.click()

    time.sleep(1.2)