import argparse
import os

import gym
import torch
from stable_baselines3 import A2C, PPO, DQN
from stable_baselines3.common.callbacks import (
    EvalCallback,
    StopTrainingOnNoModelImprovement,
    CheckpointCallback,
    CallbackList,
)
from stable_baselines3.common.monitor import Monitor

from rl.mining_env import MiningEnv

ALGOS = {
    "a2c": A2C,
    "ppo": PPO,
    "dqn": DQN,
}


def make_env(render_mode: str) -> gym.Env:
    env = MiningEnv(render_mode=render_mode)
    return Monitor(env)


def train(algo_name: str, timesteps: int, logdir: str, render_mode: str):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    algo_class = ALGOS[algo_name]
    env = make_env(render_mode)
    # Evaluation environment should be headless to speed up training
    eval_env = make_env("headless")

    stop_callback = StopTrainingOnNoModelImprovement(max_no_improvement_evals=5, min_evals=5, verbose=1)
    eval_callback = EvalCallback(
        eval_env,
        callback_after_eval=stop_callback,
        best_model_save_path=os.path.join(logdir, "best"),
        log_path=logdir,
        eval_freq=500,
        n_eval_episodes=3,
    )

    checkpoint_callback = CheckpointCallback(
        save_freq=1000,
        save_path=os.path.join(logdir, "checkpoints"),
        name_prefix=algo_name,
    )

    callbacks = CallbackList([checkpoint_callback, eval_callback])

    model = algo_class(
        "MlpPolicy",
        env,
        verbose=1,
        tensorboard_log=os.path.join(logdir, "tb"),
        learning_rate=3e-4,
        gamma=0.99,
        device=device,
    )

    try:
        model.learn(total_timesteps=timesteps, callback=callbacks)
    except KeyboardInterrupt:
        print("Training interrupted. Saving model...")
    finally:
        model.save(os.path.join(logdir, f"{algo_name}_final"))
        env.close()
        eval_env.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--algo", choices=list(ALGOS.keys()), default="ppo")
    parser.add_argument("--timesteps", type=int, default=10000)
    parser.add_argument("--logdir", type=str, default="training_logs")
    parser.add_argument(
        "--mode",
        choices=["headless", "visual"],
        default="headless",
        help="Training mode: with or without visualization",
    )
    args = parser.parse_args()

    os.makedirs(args.logdir, exist_ok=True)
    train(args.algo, args.timesteps, args.logdir, args.mode)


if __name__ == "__main__":
    main()

