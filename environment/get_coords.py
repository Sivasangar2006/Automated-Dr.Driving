import pyautogui
import time

print("Move mouse to TOP LEFT corner of road in 5 seconds")
time.sleep(5)
print("Top Left:", pyautogui.position())

print("Now move mouse to BOTTOM RIGHT corner of road in 5 seconds")
time.sleep(5)
print("Bottom Right:", pyautogui.position())