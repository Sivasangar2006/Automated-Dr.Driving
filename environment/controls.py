import pygetwindow as gw
import pyautogui
import time

pyautogui.FAILSAFE = False

# retry button coordinates
RETRY_BUTTON = (1752, 974)

# -------------------------
# MAIN ACTION FUNCTION (FINAL)
# -------------------------
def perform_action(action: int):
    """
    0 = straight
    1 = left
    2 = right
    3 = strong left
    4 = strong right
    """

    # 🚀 ALWAYS HOLD ACCELERATION (EVERY STEP)
    pyautogui.keyDown("up")

    # NEVER brake (for now)
    pyautogui.keyUp("down")

    # Reset steering every step
    pyautogui.keyUp("left")
    pyautogui.keyUp("right")

    # Apply steering
    if action == 1:
        pyautogui.keyDown("left")

    elif action == 2:
        pyautogui.keyDown("right")

    elif action == 3:
        pyautogui.keyDown("left")

    elif action == 4:
        pyautogui.keyDown("right")


# -------------------------
# OPTIONAL (ONLY FOR RESET CASES)
# -------------------------
def release_all():
    pyautogui.keyUp("up")
    pyautogui.keyUp("down")
    pyautogui.keyUp("left")
    pyautogui.keyUp("right")


# -------------------------
# RESTART FUNCTION
# -------------------------
def restart_mission():
    """
    Bring BlueStacks to front and click retry button
    """

    # 🚫 DO NOT release_all() here (important)

    time.sleep(2)

    windows = gw.getWindowsWithTitle("BlueStacks")

    if len(windows) > 0:
        win = windows[0]
        win.activate()
        time.sleep(1)

    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.3)
    pyautogui.click()

    time.sleep(4)