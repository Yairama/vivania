import argparse
import os

import torch
import numpy as np
from sb3_contrib import MaskablePPO
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
    model = MaskablePPO.load(model_path, env=env, device=device)

    reset_result = env.reset()
    obs = reset_result[0] if isinstance(reset_result, tuple) else reset_result
    for i in range(steps):
        action, _states = model.predict(obs, deterministic=True)
        print(f"action: {action} /// states: {_states}")
        step_result = env.step(action)
        if len(step_result) == 5:
            obs, reward, terminated, truncated, info = step_result
            done_flag = terminated or truncated
            if isinstance(terminated, (list, tuple, np.ndarray)):
                done_flag = terminated[0] or truncated[0]
        else:
            obs, reward, done_flag, info = step_result
            if isinstance(done_flag, (list, tuple, np.ndarray)):
                done_flag = done_flag[0]
        if done_flag:
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
