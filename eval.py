import argparse
import os

from stable_baselines3 import PPO

from rl.mining_env import MiningEnv


def _resolve_path(path: str) -> str:
    """Return a model file path. If a directory is given, pick the newest zip."""
    if os.path.isdir(path):
        ckpts = [
            os.path.join(path, f)
            for f in os.listdir(path)
            if f.endswith(".zip")
        ]
        if ckpts:
            return max(ckpts, key=os.path.getmtime)
    return path

def evaluate(model_path: str, render_mode: str = "headless", steps: int = 1000):
    """Run evaluation of a saved model for a number of steps."""
    model_path = _resolve_path(model_path)
    model = PPO.load(model_path)
    env = MiningEnv(
        render_mode=render_mode,
        max_steps=steps,
        target_production=40000,
        freeze_stats=True,
    )
    obs, _ = env.reset()
    stats_path = model_path.replace(".zip", "_stats.npz")
    env.load_running_stats_from_file(stats_path)
    obs = env.get_normalised_observation()

    for _ in range(steps):
        action, _ = model.predict(obs, deterministic=True)
        obs, _, done, truncated, _ = env.step(action)
        if done or truncated:
            obs, _ = env.reset()
            if os.path.exists(stats_path):
                env.load_running_stats_from_file(stats_path)
                obs = env.get_normalised_observation()

    env.close()


def main():
    parser = argparse.ArgumentParser(description="Evaluate a trained agent")
    parser.add_argument(
        "--from",
        dest="model_path",
        required=True,
        help="Path to a model or directory with checkpoints",
    )
    parser.add_argument(
        "--mode",
        choices=["headless", "visual"],
        default="headless",
        help="Evaluation mode",
    )
    parser.add_argument("--steps", type=int, default=10000, help="Number of steps")
    args = parser.parse_args()

    evaluate(args.model_path, args.mode, args.steps)


if __name__ == "__main__":
    main()
