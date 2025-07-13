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
    BaseCallback,
)
from stable_baselines3.common.monitor import Monitor

from rl.mining_env import MiningEnv

ALGOS = {
    "a2c": A2C,
    "ppo": PPO,
    "dqn": DQN,
}


class TensorboardMetricsCallback(BaseCallback):
    """Log custom environment metrics to TensorBoard."""

    def _on_step(self) -> bool:
        infos = self.locals.get("infos")
        if infos:
            info = infos[0]
            throughput = info.get("throughput")
            util = info.get("fleet_utilization")
            lost = info.get("lost_mineral")
            wrong = info.get("waste_in_crusher")
            hang = info.get("hang_time")
            if throughput is not None:
                self.logger.record("rollout/throughput", float(throughput))
            if util is not None:
                self.logger.record("rollout/utilization", float(util))
            if lost is not None:
                self.logger.record("rollout/lost_mineral", float(lost))
            if wrong is not None:
                self.logger.record("rollout/waste_in_crusher", float(wrong))
            if hang is not None:
                self.logger.record("rollout/hang_time", float(hang))
        return True


class VisualEvalCallback(EvalCallback):
    """EvalCallback that pauses the training visualizer during evaluation."""

    def __init__(self, train_env: MiningEnv, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.train_env = train_env

    def _on_step(self) -> bool:
        if hasattr(self.train_env, "pause_visualizer"):
            self.train_env.pause_visualizer()
        try:
            return super()._on_step()
        finally:
            if hasattr(self.train_env, "resume_visualizer"):
                self.train_env.resume_visualizer()


def make_env(render_mode: str, max_steps=800) -> gym.Env:
    env = MiningEnv(render_mode=render_mode, max_steps=max_steps, target_production=40000)
    return Monitor(env)


def train(
    algo_name: str,
    timesteps: int,
    logdir: str,
    render_mode: str,
    resume_from: str | None = None,
):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    algo_class = ALGOS[algo_name]
    env = make_env(render_mode=render_mode, max_steps=1000000)
    # Evaluation environment should be headless to speed up training
    eval_env = make_env("headless")

    stop_callback = StopTrainingOnNoModelImprovement(
        max_no_improvement_evals=5, min_evals=5, verbose=1
    )
    eval_callback = VisualEvalCallback(
        env,
        eval_env=eval_env,
        callback_after_eval=stop_callback,
        best_model_save_path=os.path.join(logdir, "best"),
        log_path=logdir,
        eval_freq=5000,
        n_eval_episodes=2,
    )

    checkpoint_callback = CheckpointCallback(
        save_freq=10000,
        save_path=os.path.join(logdir, "checkpoints"),
        name_prefix=algo_name,
    )

    tb_callback = TensorboardMetricsCallback()

    callbacks = CallbackList([checkpoint_callback, eval_callback, tb_callback])

    if resume_from is not None:
        # If a directory is passed, load the most recent checkpoint inside
        if os.path.isdir(resume_from):
            ckpts = [
                os.path.join(resume_from, f)
                for f in os.listdir(resume_from)
                if f.endswith(".zip")
            ]
            if ckpts:
                resume_from = max(ckpts, key=os.path.getmtime)
        model = algo_class.load(resume_from, env=env, device=device)
    else:
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
    parser.add_argument("--timesteps", type=int, default=100000)
    parser.add_argument("--logdir", type=str, default="training_logs")
    parser.add_argument(
        "--mode",
        choices=["headless", "visual"],
        default="headless",
        help="Training mode: with or without visualization",
    )
    parser.add_argument(
        "--resume-from",
        type=str,
        default=None,
        help="Path to a saved model or checkpoint to resume from",
    )
    args = parser.parse_args()

    os.makedirs(args.logdir, exist_ok=True)
    train(args.algo, args.timesteps, args.logdir, args.mode, args.resume_from)


if __name__ == "__main__":
    main()
