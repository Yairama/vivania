from __future__ import annotations

import argparse
from ray.rllib.algorithms.mappo import MAPPO
from torch.utils.tensorboard import SummaryWriter

from .ma_config import get_default_config


def train(
    num_iters: int,
    logdir: str,
    resume_from: str | None = None,
    render_mode: str = "headless",
):
    """Train a MAPPO agent and log metrics to TensorBoard."""

    config = get_default_config(render_mode)
    if resume_from:
        algo = MAPPO(config=config.to_dict())
        algo.restore(resume_from)
    else:
        algo = config.build()

    writer = SummaryWriter(logdir)
    for i in range(num_iters):
        result = algo.train()
        writer.add_scalar("episode_reward_mean", result.get("episode_reward_mean", 0.0), i)
        policy_mean = result.get("policy_reward_mean", {})
        if "shared_policy" in policy_mean:
            writer.add_scalar(
                "shared_policy_reward_mean",
                policy_mean["shared_policy"],
                i,
            )
        env = algo.workers.local_worker().env
        writer.add_scalar(
            "coordination/wrong_assignments",
            getattr(env.manager, "wrong_assignment_count", 0),
            i,
        )
        print(result.get("episode_reward_mean"))

    checkpoint = algo.save(logdir)
    writer.close()
    print(f"Checkpoint saved at {checkpoint}")
    algo.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iters", type=int, default=1)
    parser.add_argument("--logdir", type=str, default="ma_training_logs")
    parser.add_argument("--resume", type=str, default=None)
    parser.add_argument(
        "--mode",
        choices=["headless", "visual"],
        default="headless",
        help="Training mode: with or without visualization",
    )
    args = parser.parse_args()
    train(args.iters, args.logdir, args.resume, args.mode)


if __name__ == "__main__":
    main()

