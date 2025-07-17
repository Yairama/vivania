import argparse
import os

import torch
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

from rl.mining_env import MiningEnv


def make_env(render_mode: str, stats_path: str | None = None):
    def _init():
        env = MiningEnv(render_mode=render_mode)
        return Monitor(env)

    env = DummyVecEnv([_init])
    if stats_path and os.path.exists(stats_path):
        env = VecNormalize.load(stats_path, env)
        env.training = False
    else:
        env = VecNormalize(env, training=False, norm_obs=True, norm_reward=False)
    return env


def evaluate(model_path: str, render_mode: str = "headless", steps: int = 1000):
    device = "cuda" if torch.cuda.is_available() else "cpu"

    stats_path = os.path.join(os.path.dirname(model_path), "vecnormalize.pkl")
    if not os.path.exists(stats_path):
        alt = os.path.join(os.path.dirname(model_path), "checkpoints", "vecnormalize.pkl")
        stats_path = alt if os.path.exists(alt) else None

    env = make_env(render_mode=render_mode, stats_path=stats_path)
    model = PPO.load(model_path, env=env, device=device)

    reset_result = env.reset()
    obs = reset_result[0] if isinstance(reset_result, tuple) else reset_result
    for i in range(steps):
        action, _states = model.predict(obs, deterministic=True)
        # print(f"action: {action} /// states: {_states}")
        obs, reward, done, info = env.step(action)
        print(reward)
        if done[0] if isinstance(done, (list, tuple, np.ndarray)) else done:
            reset_result = env.reset()
            obs = reset_result[0] if isinstance(reset_result, tuple) else reset_result

    env.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--from", dest="model_path", required=True, help="Path to model")
    parser.add_argument("--mode", choices=["headless", "visual"], default="headless")
    parser.add_argument("--steps", type=int, default=1000)
    args = parser.parse_args()
    evaluate(args.model_path, render_mode=args.mode, steps=args.steps)
