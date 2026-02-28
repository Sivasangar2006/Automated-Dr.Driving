import pyautogui
import time

print("When the Mission Failed screen appears...")
print("Place your mouse exactly on the GREEN PLAY button in 5 seconds")
time.sleep(5)

print("Button Position:", pyautogui.position())