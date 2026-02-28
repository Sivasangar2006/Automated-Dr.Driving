import time
from environment.controls import perform_action

print("Starting in 3 seconds... focus the game window!")
time.sleep(3)

while True:
    perform_action(1)   # accelerate
    time.sleep(2)

    perform_action(3)   # left
    time.sleep(2)

    perform_action(4)   # right
    time.sleep(2)

    perform_action(2)   # brake
    time.sleep(2)

    perform_action(0)   # idle
    time.sleep(2)