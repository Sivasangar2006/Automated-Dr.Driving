from environment.controls import perform_action, release_all
import time

print("Starting in 3 seconds... focus the game window!")
time.sleep(3)

print("Holding ACCELERATE for 5 seconds...")
perform_action(1)   # accelerate

time.sleep(5)

release_all()
print("Done")