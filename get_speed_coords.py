import pyautogui
import time

print("Put mouse on TOP-LEFT of the SPEEDOMETER in 5 seconds...")
time.sleep(5)
print("Top Left:", pyautogui.position())

print("Now put mouse on BOTTOM-RIGHT of the SPEEDOMETER in 5 seconds...")
time.sleep(5)
print("Bottom Right:", pyautogui.position())