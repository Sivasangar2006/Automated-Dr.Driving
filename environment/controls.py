import pygetwindow as gw
import pyautogui
import time

pyautogui.FAILSAFE = False

# retry button coordinates
RETRY_BUTTON = (1752, 974)

# ─────────────────────────────────────────────────────────────────────────────
# 9-ACTION FULL CONTROL SYSTEM
#
#   Speed state  ×  Steer state  =  Action
#   ─────────────────────────────────────────
#   Accelerate   +  Straight     =  0   (UP)
#   Accelerate   +  Left         =  1   (UP + LEFT)
#   Accelerate   +  Right        =  2   (UP + RIGHT)
#   Coast        +  Straight     =  3   (no keys — let car slow naturally)
#   Coast        +  Left         =  4   (LEFT only — YOUR KEY INSIGHT)
#   Coast        +  Right        =  5   (RIGHT only)
#   Brake        +  Straight     =  6   (DOWN)
#   Brake        +  Left         =  7   (DOWN + LEFT)
#   Brake        +  Right        =  8   (DOWN + RIGHT)
#
#   The old speed governor has been REMOVED.
#   The AI now fully controls when to accelerate, coast, or brake.
# ─────────────────────────────────────────────────────────────────────────────

def perform_action(action: int):
    """
    Executes one of 9 driving actions by sending the appropriate key events.
    All keys are released first to ensure a clean state each step.
    """
    # ── Release everything first (clean slate each step) ──────────────────
    pyautogui.keyUp("up")
    pyautogui.keyUp("down")
    pyautogui.keyUp("left")
    pyautogui.keyUp("right")

    # ── Speed control ──────────────────────────────────────────────────────
    if action in (0, 1, 2):        # Accelerate
        pyautogui.keyDown("up")
    elif action in (6, 7, 8):      # Brake
        pyautogui.keyDown("down")
    # Coast (3, 4, 5): no vertical key — car slows naturally

    # ── Steering ───────────────────────────────────────────────────────────
    if action in (1, 4, 7):        # Left
        pyautogui.keyDown("left")
    elif action in (2, 5, 8):      # Right
        pyautogui.keyDown("right")
    # Straight (0, 3, 6): no horizontal key


# ─────────────────────────────────────────────────────────────────────────────
# RELEASE ALL KEYS  (used on reset / episode end)
# ─────────────────────────────────────────────────────────────────────────────
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

    time.sleep(1.2)  # ⚡ reduced: was 3.0s

    windows = gw.getWindowsWithTitle("BlueStacks")
    if len(windows) > 0:
        win = windows[0]
        win.activate()
        time.sleep(0.3)  # ⚡ reduced: was 1.0s

    # Click 1 — dismisses result screen
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.05)  # ⚡ was 0.3
    pyautogui.click()
    time.sleep(0.8)  # ⚡ reduced: was 2.0s

    # Click 2 — confirms / starts new run
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.05)  # ⚡ was 0.2
    pyautogui.click()
    time.sleep(0.5)  # ⚡ reduced: was 1.5s

    # Click 3 — safety click in case dialog was slow loading
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.05)  # ⚡ was 0.2
    pyautogui.click()

    time.sleep(2.0)  # ⚡ reduced: was 4.0s — ~5.0s total vs 12.2s before


# -------------------------
# FINISH LINE FUNCTION
# -------------------------
def finish_mission():
    """
    After reaching the finish line:
    - Same three-click sequence to dismiss win screen and restart
    """
    release_all()

    time.sleep(1.2)  # ⚡ reduced: was 3.0s

    windows = gw.getWindowsWithTitle("BlueStacks")
    if len(windows) > 0:
        win = windows[0]
        win.activate()
        time.sleep(0.3)  # ⚡ reduced: was 1.0s

    # Click 1 — dismisses win/result screen
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.05)  # ⚡ was 0.3
    pyautogui.click()
    time.sleep(0.8)  # ⚡ reduced: was 2.0s

    # Click 2 — starts new run
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.05)  # ⚡ was 0.2
    pyautogui.click()
    time.sleep(0.5)  # ⚡ reduced: was 1.5s

    # Click 3 — safety click
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.05)  # ⚡ was 0.2
    pyautogui.click()

    time.sleep(2.0)  # ⚡ reduced: was 4.0s
