import pygetwindow as gw
import pyautogui
import time

pyautogui.FAILSAFE = False

RETRY_BUTTON = (1752, 974)


def _focus_bluestacks():
    """
    Brings BlueStacks window to front so key presses go to the right place.
    """
    windows = gw.getWindowsWithTitle("BlueStacks")
    if windows:
        try:
            windows[0].activate()
        except:
            pass


def perform_action(action: int):
    """
    0 = straight
    1 = left
    2 = right
    """
    _focus_bluestacks()

    # always hold acceleration
    pyautogui.keyDown("up")
    pyautogui.keyUp("down")

    # reset steering every step
    pyautogui.keyUp("left")
    pyautogui.keyUp("right")

    # apply steering
    if action == 1:
        pyautogui.keyDown("left")
    elif action == 2:
        pyautogui.keyDown("right")
    # action 0 = straight, no steering needed


def release_all():
    pyautogui.keyUp("up")
    pyautogui.keyUp("down")
    pyautogui.keyUp("left")
    pyautogui.keyUp("right")


def restart_mission():
    """
    Brings BlueStacks to front and clicks retry button.
    """
    time.sleep(2)

    _focus_bluestacks()
    time.sleep(1)

    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.3)
    pyautogui.click()

    time.sleep(4)