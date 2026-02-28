import pygetwindow as gw
import pyautogui
import time

pyautogui.FAILSAFE = False

KEY_DELAY = 0.08

# retry button coordinates
RETRY_BUTTON = (1752, 974)


def release_all():
    pyautogui.keyUp('up')
    pyautogui.keyUp('down')
    pyautogui.keyUp('left')
    pyautogui.keyUp('right')


def accelerate():
    release_all()
    pyautogui.keyDown('up')
    time.sleep(KEY_DELAY)


def brake():
    release_all()
    pyautogui.keyDown('down')
    time.sleep(KEY_DELAY)


def go_left():
    release_all()
    pyautogui.keyDown('left')
    time.sleep(KEY_DELAY)


def go_right():
    release_all()
    pyautogui.keyDown('right')
    time.sleep(KEY_DELAY)


def no_action():
    release_all()


def perform_action(action: int):

    if action == 0:
        no_action()

    elif action == 1:
        accelerate()

    elif action == 2:
        brake()

    elif action == 3:
        go_left()

    elif action == 4:
        go_right()


def restart_mission():
    """
    Bring BlueStacks to front and click retry button
    """
    release_all()

    # wait for mission failed screen
    time.sleep(2)

    # find BlueStacks window
    windows = gw.getWindowsWithTitle("BlueStacks")

    if len(windows) > 0:
        win = windows[0]
        win.activate()   # bring to front
        time.sleep(1)

    # move mouse to button and click
    pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.3)
    pyautogui.click()

    # wait for new mission to load
    time.sleep(4)