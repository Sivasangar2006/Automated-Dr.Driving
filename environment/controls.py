import pygetwindow as gw
import pyautogui
import time

pyautogui.FAILSAFE = False

RETRY_BUTTON = (1752, 974)

pyautogui.keyUp("left")
pyautogui.keyUp("right")

if action == 0:
    pyautogui.keyDown("up")
    pyautogui.keyUp("down")
elif action == 1:
    pyautogui.keyUp("up")
    pyautogui.keyDown("down")
elif action == 2:
    pyautogui.keyUp("up")
    pyautogui.keyUp("down")

pyautogui.keyUp("up")
pyautogui.keyUp("down")
pyautogui.keyUp("left")
pyautogui.keyUp("right")

time.sleep(2)

windows = gw.getWindowsWithTitle("BlueStacks")

if len(windows) > 0:
    win = windows[0]
    win.activate()
    time.sleep(1)

pyautogui.moveTo(RETRY_BUTTON[0], RETRY_BUTTON[1], duration=0.3)
pyautogui.click()

time.sleep(4)