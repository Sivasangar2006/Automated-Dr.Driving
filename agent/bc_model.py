"""
agent/bc_model.py
=================
Behavioral Cloning (BC) trainer.

Uses Stable Baselines3's own PPO policy network (CnnPolicy) as the
classifier — so the trained weights are 100% compatible with your
existing PPO training pipeline.

Training is entirely OFFLINE: no game, no BlueStacks needed.
Just your recorded frames + action labels.

How it works:
  1. Load recordings/frames.npy and recordings/actions.npy
  2. Create a PPO model shell (no env interaction)
  3. Run supervised cross-entropy training on the policy network
  4. Save to models/bc_pretrained.zip
  5. You pass --pretrain to main.py to start RL from those weights
"""

import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

from environment.game_env import DrDrivingEnv
from agent.model import POLICY, HYPERPARAMS, SAVE_DIR


# ── Dataset ────────────────────────────────────────────────────────────────────

class GameplayDataset(Dataset):
    """
    Loads your recorded gameplay from disk.

    frames:  (N, 84, 84, 1) uint8  →  normalized to float32 (N, 1, 84, 84)
    actions: (N,)            int64   (0=straight, 1=left, 2=right)
    """

    def __init__(self, frames_path: str, actions_path: str):
        frames  = np.load(frames_path)           # (N, 84, 84, 1)  uint8
        actions = np.load(actions_path)          # (N,)            int64

        # Normalize + reshape to PyTorch channel-first format
        frames_f     = frames.astype(np.float32) / 255.0
        self.frames  = torch.FloatTensor(frames_f).permute(0, 3, 1, 2)   # (N,1,H,W)
        self.actions = torch.LongTensor(actions)

        # Validate
        assert len(self.frames) == len(self.actions), "Frame/action count mismatch!"

    def __len__(self) -> int:
        return len(self.actions)

    def __getitem__(self, idx):
        return self.frames[idx], self.actions[idx]


# ── BC Trainer ─────────────────────────────────────────────────────────────────

def train_bc(
    frames_path:  str   = "recordings/frames.npy",
    actions_path: str   = "recordings/actions.npy",
    save_path:    str   = "models/bc_pretrained",
    epochs:       int   = 30,
    batch_size:   int   = 64,
    lr:           float = 1e-4,
) -> None:
    """
    Trains a PPO CnnPolicy via behavioral cloning on recorded gameplay.
    Saves the result as a .zip compatible with PPO.load().

    Args:
        frames_path:  Path to recorded frames numpy file
        actions_path: Path to recorded actions numpy file
        save_path:    Where to save the trained model (no .zip extension)
        epochs:       Number of full passes over the dataset
        batch_size:   Mini-batch size for gradient updates
        lr:           Learning rate for Adam optimizer
    """

    print("\n" + "=" * 48)
    print("  BEHAVIORAL CLONING — OFFLINE TRAINER")
    print("=" * 48)

    # ── Validate recordings exist ───────────────────────────────────────────
    for path in [frames_path, actions_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"\n  ❌ Not found: {path}\n"
                f"  Run  python record_gameplay.py  first to capture gameplay!"
            )

    # ── Load dataset ────────────────────────────────────────────────────────
    dataset = GameplayDataset(frames_path, actions_path)
    loader  = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)

    labels      = {0: "STRAIGHT", 1: "LEFT", 2: "RIGHT"}
    unique, cnt = np.unique(np.load(actions_path), return_counts=True)
    print(f"\n  Dataset : {len(dataset)} frames")
    print(f"  Split   : ", end="")
    print(" | ".join(f"{labels[a]} {c/len(dataset)*100:.0f}%" for a, c in zip(unique, cnt)))
    print(f"  Epochs  : {epochs}   Batch: {batch_size}   LR: {lr}\n")

    # ── Build PPO model shell (weights will be trained via BC) ──────────────
    # We wrap a DrDrivingEnv just to define obs/action spaces.
    # No actual game interaction happens during BC training.
    env    = Monitor(DrDrivingEnv())
    params = {k: v for k, v in HYPERPARAMS.items()}   # copy so we don't mutate
    model  = PPO(POLICY, env, device="cpu", **params)
    policy = model.policy
    policy.train()

    # ── Optimizer + loss ────────────────────────────────────────────────────
    optimizer = torch.optim.Adam(policy.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    best_acc  = 0.0

    # ── Training loop ───────────────────────────────────────────────────────
    for epoch in range(1, epochs + 1):
        total_loss = 0.0
        correct    = 0
        total      = 0

        for frames_batch, actions_batch in loader:

            # Forward: extract features → MLP → action logits
            features        = policy.extract_features(frames_batch, policy.pi_features_extractor)
            latent_pi, _    = policy.mlp_extractor(features)
            logits          = policy.action_net(latent_pi)

            loss = criterion(logits, actions_batch)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * len(actions_batch)
            preds       = logits.argmax(dim=1)
            correct    += (preds == actions_batch).sum().item()
            total      += len(actions_batch)

        avg_loss = total_loss / total
        accuracy = correct / total * 100
        marker   = " ✅ best" if accuracy > best_acc else ""

        if accuracy > best_acc:
            best_acc = accuracy

        print(f"  Epoch {epoch:>3}/{epochs}  |  Loss: {avg_loss:.4f}  |  Accuracy: {accuracy:.1f}%{marker}")

    # ── Save ────────────────────────────────────────────────────────────────
    os.makedirs(SAVE_DIR, exist_ok=True)
    model.save(save_path)
    env.close()

    print(f"\n  ✅ BC model saved → {save_path}.zip")
    print(f"  Best accuracy : {best_acc:.1f}%")
    print(f"\n  ➡  Next step:")
    print(f"       python main.py --mode train --pretrain")
    print("=" * 48 + "\n")
