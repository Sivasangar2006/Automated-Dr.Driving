"""
train_bc.py
===========
Trains the behavioral cloning model from your recorded gameplay.

This runs ENTIRELY OFFLINE — no game, no BlueStacks needed.
Just your recordings/ files and a CPU.

Workflow:
  Step 1:  python record_gameplay.py    ← record 20-30 min of gameplay
  Step 2:  python train_bc.py           ← train BC model offline (this file)
  Step 3:  python main.py --mode train --pretrain  ← RL starts from BC weights
"""

from agent.bc_model import train_bc

if __name__ == "__main__":
    train_bc(
        frames_path  = "recordings/frames.npy",
        actions_path = "recordings/actions.npy",
        save_path    = "models/bc_pretrained",
        epochs       = 30,      # increase to 50 if accuracy is still low at end
        batch_size   = 64,
        lr           = 1e-4,
    )
