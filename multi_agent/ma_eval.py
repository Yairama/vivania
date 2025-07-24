import argparse
from typing import Dict

from ray.rllib.algorithms.mappo import MAPPO

from .ma_config import get_default_config


def evaluate(checkpoint: str, render_mode: str = "headless", steps: int = 100) -> None:
    """Load a MAPPO checkpoint and run a short evaluation."""
    config = get_default_config(render_mode)
    algo = MAPPO(config=config.to_dict())
    algo.restore(checkpoint)

    env = algo.workers.local_worker().env
    obs, _ = env.reset()
    for _ in range(steps):
        actions: Dict[str, int] = {}
        for agent_id, agent_obs in obs.items():
            action, _, _ = algo.compute_single_action(agent_obs, policy_id="shared_policy")
            actions[agent_id] = int(action)
        obs, _, term, trunc, _ = env.step(actions)
        if env.render_mode == "visual":
            env.render()
        if term.get("__all__") or trunc.get("__all__"):
            obs, _ = env.reset()

    env.close()
    algo.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from", dest="checkpoint", required=True)
    parser.add_argument("--mode", choices=["headless", "visual"], default="headless")
    parser.add_argument("--steps", type=int, default=100)
    args = parser.parse_args()
    evaluate(args.checkpoint, render_mode=args.mode, steps=args.steps)


if __name__ == "__main__":
    main()
