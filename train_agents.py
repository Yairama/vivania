import argparse
import os

import gym
from stable_baselines3 import A2C, PPO, DQN
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnNoModelImprovement
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.logger import configure

from rl.mining_env import MiningEnv

ALGOS = {
    "a2c": A2C,
    "ppo": PPO,
    "dqn": DQN,
}


def make_env() -> gym.Env:
    env = MiningEnv()
    return Monitor(env)


def train(algo_name: str, timesteps: int, logdir: str):
    algo_class = ALGOS[algo_name]
    env = make_env()
    eval_env = make_env()

    stop_callback = StopTrainingOnNoModelImprovement(max_no_improvement_evals=5, min_evals=5, verbose=1)
    eval_callback = EvalCallback(
        eval_env,
        callback_after_eval=stop_callback,
        best_model_save_path=os.path.join(logdir, "best"),
        log_path=logdir,
        eval_freq=500,
        n_eval_episodes=3,
    )

    model = algo_class(
        "MlpPolicy",
        env,
        verbose=1,
        tensorboard_log=os.path.join(logdir, "tb"),
        learning_rate=3e-4,
        gamma=0.99,
    )

    model.learn(total_timesteps=timesteps, callback=eval_callback)
    model.save(os.path.join(logdir, f"{algo_name}_final"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--algo", choices=list(ALGOS.keys()), default="ppo")
    parser.add_argument("--timesteps", type=int, default=5000)
    parser.add_argument("--logdir", type=str, default="training_logs")
    args = parser.parse_args()

    os.makedirs(args.logdir, exist_ok=True)
    train(args.algo, args.timesteps, args.logdir)


if __name__ == "__main__":
    main()
