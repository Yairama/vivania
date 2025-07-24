from __future__ import annotations

import argparse
from ray import air, tune
from ray.rllib.algorithms.mappo import MAPPO

from .ma_config import get_default_config


def train(num_iters: int, logdir: str, resume_from: str | None = None):
    config = get_default_config()
    if resume_from:
        algo = MAPPO(config=config.to_dict())
        algo.restore(resume_from)
    else:
        algo = config.build()

    for _ in range(num_iters):
        result = algo.train()
        print(result.get("episode_reward_mean"))
    checkpoint = algo.save(logdir)
    print(f"Checkpoint saved at {checkpoint}")
    algo.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iters", type=int, default=1)
    parser.add_argument("--logdir", type=str, default="ma_training_logs")
    parser.add_argument("--resume", type=str, default=None)
    args = parser.parse_args()
    train(args.iters, args.logdir, args.resume)


if __name__ == "__main__":
    main()

