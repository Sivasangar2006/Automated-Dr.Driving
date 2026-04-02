import pygetwindow as gw
import pyautogui
import time

pyautogui.FAILSAFE = False

# Speed governor thresholds (speed_ratio = km/h / 200)
SPEED_MIN = 0.29   # 58 km/h  — re-apply throttle below this
SPEED_MAX = 0.315  # 63 km/h  — cut throttle above this

# Internal throttle state so we don't spam keyDown/keyUp every frame
_throttle_on = False

# retry button coordinates
RETRY_BUTTON = (1752, 974)

# -------------------------
# MAIN ACTION FUNCTION (FINAL)
# -------------------------
def perform_action(action: int, speed: float = None):
    """
    Controls steering and throttle.

    action:
        0 = straight
        1 = left
        2 = right
        3 = strong left
        4 = strong right

    speed (optional):
        Current speed ratio (0.0 – 1.0) from get_speed().
        If provided, the throttle is governed to stay in the
        60–70 km/h band (ratio 0.30–0.35).
        If None, always accelerates (legacy behaviour).
    """
    global _throttle_on

    # --- SPEED GOVERNOR ---
    if speed is None:
        # Legacy: always hold acceleration
        if not _throttle_on:
            pyautogui.keyDown("up")
            _throttle_on = True
    else:
        if speed >= SPEED_MAX and _throttle_on:
            # Reached 70 km/h — release throttle
            pyautogui.keyUp("up")
            _throttle_on = False
        elif speed < SPEED_MIN and not _throttle_on:
            # Dropped below 60 km/h — apply throttle again
            pyautogui.keyDown("up")
            _throttle_on = True
        # Between 60–70 km/h: keep current throttle state (no change)

    # Never brake
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
# RESTART FUNCTION (after crash)
# -------------------------
def restart_mission():
    """
    After a crash:
    - Click 1: dismisses the crash/result overlay
    - Click 2: confirms and starts the new run
    - Click 3: safety click in case dialog was slow
    """
    release_all()  # release keys before UI interaction

    time.sleep(3)  # wait longer for crash overlay to fully settle

    windows = gw.getWindowsWithTitle("BlueStacks")
    if len(windows) > 0:
        win = windows[0]
        win.activate()
        time.sleep(1.0)  # give window time to come to front

    # Click 1 — dismisses result screen
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.3)
    pyautogui.click()
    time.sleep(2.0)  # wait generously for next dialog

    # Click 2 — confirms / starts new run
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.2)
    pyautogui.click()
    time.sleep(1.5)

    # Click 3 — safety click in case dialog was slow loading
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.2)
    pyautogui.click()

    time.sleep(4)   # wait for game to fully reload


# -------------------------
# FINISH LINE FUNCTION
# -------------------------
def finish_mission():
    """
    After reaching the finish line:
    - Same three-click sequence to dismiss win screen and restart
    """
    release_all()

    time.sleep(3)

    windows = gw.getWindowsWithTitle("BlueStacks")
    if len(windows) > 0:
        win = windows[0]
        win.activate()
        time.sleep(1.0)

    # Click 1 — dismisses win/result screen
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.3)
    pyautogui.click()
    time.sleep(2.0)

    # Click 2 — starts new run
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.2)
    pyautogui.click()
    time.sleep(1.5)

    # Click 3 — safety click
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.2)
    pyautogui.click()

    time.sleep(4)
