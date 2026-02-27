# main.py
# Entry point for the entire project.
# Run this file to start training or evaluating the agent.

import argparse
from agent.train import train, evaluate


def main():
    parser = argparse.ArgumentParser(description="Dr Driving AI")

    parser.add_argument(
        "--mode",
        type    = str,
        default = "train",
        choices = ["train", "evaluate"],
        help    = "train the agent or evaluate a saved model"
    )

    parser.add_argument(
        "--resume",
        action  = "store_true",
        help    = "resume training from last saved checkpoint"
    )

    parser.add_argument(
        "--episodes",
        type    = int,
        default = 5,
        help    = "number of episodes to run during evaluation"
    )

    args = parser.parse_args()

    if args.mode == "train":
        train(resume=args.resume)

    elif args.mode == "evaluate":
        evaluate(n_episodes=args.episodes)


if __name__ == "__main__":
    main()