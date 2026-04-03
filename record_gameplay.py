"""
record_gameplay.py
==================
Run this WHILE playing Dr. Driving in BlueStacks.

Controls:
  R → Start recording
  Q → Stop and save to disk

What it captures every 0.08 seconds:
  - 84×84 grayscale frame (same format as RL training)
  - Which key was pressed → action label (0=straight, 1=left, 2=right)

Data is saved (or appended) to:
  recordings/frames.npy    shape: (N, 84, 84, 1)  dtype: uint8
  recordings/actions.npy   shape: (N,)             dtype: int64

Multiple sessions are automatically merged — you can record in batches.

Usage:
  1. Start BlueStacks and open Dr. Driving in highway mode
  2. Run:  python record_gameplay.py
  3. Switch to BlueStacks window
  4. Press R to start recording, then play normally
  5. Press Q when done — data is saved automatically
  6. (Optional) record more sessions; they will be appended
  7. Run:  python train_bc.py  to train the BC model offline
"""

import os
import time
import numpy as np
import cv2
import mss
import keyboard

# ── Same screen coordinates as environment/vision.py ──────────────────────────
MONITOR = {"top": 157, "left": 43, "width": 1548, "height": 502}

CAPTURE_INTERVAL = 0.08   # seconds between frames (matches RL step rate)
SAVE_DIR         = "recordings"

sct = mss.mss()


# ── Helpers ────────────────────────────────────────────────────────────────────

def get_frame() -> np.ndarray:
    """Captures the game window and returns a (84, 84, 1) uint8 array."""
    img    = np.array(sct.grab(MONITOR))
    gray   = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (84, 84), interpolation=cv2.INTER_AREA)
    return resized.reshape(84, 84, 1).astype(np.uint8)


def get_action() -> int:
    """
    Detects which arrow keys are held and maps to one of 9 actions.

    Speed state:    UP held → Accelerate | DOWN held → Brake | neither → Coast
    Steer state:    LEFT held → Left     | RIGHT held → Right | neither → Straight

    Action table (matches game_env.py exactly):
      0 = Accel  + Straight    4 = Coast + Left      8 = Brake + Right
      1 = Accel  + Left        5 = Coast + Right
      2 = Accel  + Right       6 = Brake + Straight
      3 = Coast  + Straight    7 = Brake + Left
    """
    up    = keyboard.is_pressed("up")
    down  = keyboard.is_pressed("down")
    left  = keyboard.is_pressed("left")  or keyboard.is_pressed("a")
    right = keyboard.is_pressed("right") or keyboard.is_pressed("d")

    # Speed state
    if up and not down:
        spd = "accel"
    elif down and not up:
        spd = "brake"
    else:
        spd = "coast"   # neither / both = coast

    # Steer state
    if left and not right:
        steer = "left"
    elif right and not left:
        steer = "right"
    else:
        steer = "straight"

    return {
        ("accel", "straight"): 0,
        ("accel", "left"):     1,
        ("accel", "right"):    2,
        ("coast", "straight"): 3,
        ("coast", "left"):     4,
        ("coast", "right"):    5,
        ("brake", "straight"): 6,
        ("brake", "left"):     7,
        ("brake", "right"):    8,
    }[(spd, steer)]


def save_recordings(frames: list, actions: list) -> None:
    """Saves (or appends to) the recordings directory."""
    os.makedirs(SAVE_DIR, exist_ok=True)

    frames_arr  = np.array(frames,  dtype=np.uint8)
    actions_arr = np.array(actions, dtype=np.int64)

    frames_path  = os.path.join(SAVE_DIR, "frames.npy")
    actions_path = os.path.join(SAVE_DIR, "actions.npy")

    # Append to existing dataset if it exists
    if os.path.exists(frames_path):
        old_frames  = np.load(frames_path)
        old_actions = np.load(actions_path)
        frames_arr  = np.concatenate([old_frames,  frames_arr],  axis=0)
        actions_arr = np.concatenate([old_actions, actions_arr], axis=0)
        print(f"\n  Appended to existing data.")

    np.save(frames_path,  frames_arr)
    np.save(actions_path, actions_arr)

    # Print dataset summary
    labels = [
        "Accel+Straight", "Accel+Left",  "Accel+Right",
        "Coast+Straight", "Coast+Left",  "Coast+Right",
        "Brake+Straight", "Brake+Left",  "Brake+Right",
    ]
    unique, counts = np.unique(actions_arr, return_counts=True)

    print(f"\n  ✅ Dataset saved!")
    print(f"     Total frames : {len(frames_arr)}")
    print(f"     Action split :")
    for a, c in zip(unique, counts):
        pct = c / len(actions_arr) * 100
        print(f"       {labels[a]:>15}: {c:>6}  ({pct:.1f}%)")
    print(f"\n     Files : {frames_path}")
    print(f"             {actions_path}")
    print("\n  ➡  Next step: python train_bc.py")


# ── Main loop ──────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 52)
    print("  DR. DRIVING — GAMEPLAY RECORDER")
    print("=" * 52)
    print("  1. Switch to BlueStacks and start a race")
    print("  2. Press  R  to begin recording")
    print("  3. Drive normally — try to play well!")
    print("  4. Press  Q  to stop and save")
    print("=" * 52 + "\n")

    frames    = []
    actions   = []
    recording = False

    while True:

        # ── Start recording ─────────────────────────────────────────────────
        if keyboard.is_pressed("r") and not recording:
            recording = True
            print("[REC] ● Recording started — drive now!\n")
            time.sleep(0.5)   # debounce so 'r' isn't captured as a frame

        # ── Stop and save ────────────────────────────────────────────────────
        if keyboard.is_pressed("q"):
            if recording:
                print(f"\n[STOP] ■ Stopped. Captured {len(frames)} frames.")
                save_recordings(frames, actions)
            else:
                print("\n[EXIT] No recording in progress. Exiting.")
            break

        # ── Capture frame ────────────────────────────────────────────────────
        if recording:
            frame  = get_frame()
            action = get_action()

            frames.append(frame)
            actions.append(action)

            # Live status every 100 frames
            if len(frames) % 100 == 0:
                label = [
                    "Accel+Straight", "Accel+Left",  "Accel+Right",
                    "Coast+Straight", "Coast+Left",  "Coast+Right",
                    "Brake+Straight", "Brake+Left",  "Brake+Right",
                ][action]
                elapsed = len(frames) * CAPTURE_INTERVAL
                print(f"  Frame {len(frames):>5} | {label:>15} | {elapsed:.0f}s recorded")

        time.sleep(CAPTURE_INTERVAL)


if __name__ == "__main__":
    main()
