"""
merge_recordings.py
===================
Merges gameplay recordings from two players into one combined dataset.

Usage:
  1. Person A sends their  recordings/  folder to Person B
  2. Person B renames it to  recordings_A/
  3. Their own recordings stay in  recordings/
  4. Run:  python merge_recordings.py

Or specify custom paths:
  python merge_recordings.py  recordings_A  recordings_B  recordings_merged

The merged output is saved to  recordings/  by default (overwrites existing).
After merging, run:  python train_bc.py
"""

import sys
import os
import numpy as np


LABELS = [
    "Accel+Straight", "Accel+Left",  "Accel+Right",
    "Coast+Straight", "Coast+Left",  "Coast+Right",
    "Brake+Straight", "Brake+Left",  "Brake+Right",
]


def load_recording(folder: str):
    """Loads frames and actions from a recordings folder."""
    fp = os.path.join(folder, "frames.npy")
    ap = os.path.join(folder, "actions.npy")

    if not os.path.exists(fp) or not os.path.exists(ap):
        raise FileNotFoundError(
            f"  ❌ Could not find frames.npy / actions.npy in '{folder}'\n"
            f"     Make sure the folder exists and contains recordings."
        )

    frames  = np.load(fp)
    actions = np.load(ap)
    return frames, actions


def print_summary(name: str, frames: np.ndarray, actions: np.ndarray):
    """Prints a breakdown of one dataset."""
    print(f"\n  [{name}]  {len(frames)} frames")
    unique, counts = np.unique(actions, return_counts=True)
    for a, c in zip(unique, counts):
        pct = c / len(actions) * 100
        print(f"    {LABELS[a]:>15} : {c:>6}  ({pct:.1f}%)")


def merge(folder_a: str, folder_b: str, out_folder: str):

    print("\n" + "=" * 52)
    print("  RECORDING MERGER")
    print("=" * 52)

    # ── Load both datasets ─────────────────────────────────────────────────
    print(f"\n  Loading '{folder_a}'...")
    frames_a, actions_a = load_recording(folder_a)
    print_summary("Player A", frames_a, actions_a)

    print(f"\n  Loading '{folder_b}'...")
    frames_b, actions_b = load_recording(folder_b)
    print_summary("Player B", frames_b, actions_b)

    # ── Validate shapes match ──────────────────────────────────────────────
    assert frames_a.shape[1:] == frames_b.shape[1:], (
        f"Frame shape mismatch: {frames_a.shape} vs {frames_b.shape}\n"
        "Both players must use the same screen coordinates and resolution."
    )

    # ── Merge ──────────────────────────────────────────────────────────────
    frames_merged  = np.concatenate([frames_a,  frames_b],  axis=0)
    actions_merged = np.concatenate([actions_a, actions_b], axis=0)

    print_summary("MERGED", frames_merged, actions_merged)

    # ── Save ───────────────────────────────────────────────────────────────
    os.makedirs(out_folder, exist_ok=True)
    np.save(os.path.join(out_folder, "frames.npy"),  frames_merged)
    np.save(os.path.join(out_folder, "actions.npy"), actions_merged)

    print(f"\n  ✅ Merged dataset saved to '{out_folder}/'")
    print(f"     Total frames : {len(frames_merged)}")
    print(f"\n  ➡  Next step: python train_bc.py")
    print("=" * 52 + "\n")


if __name__ == "__main__":
    # Allow optional command-line path overrides
    folder_a   = sys.argv[1] if len(sys.argv) > 1 else "recordings_A"
    folder_b   = sys.argv[2] if len(sys.argv) > 2 else "recordings"
    out_folder = sys.argv[3] if len(sys.argv) > 3 else "recordings"

    merge(folder_a, folder_b, out_folder)
