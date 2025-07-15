import argparse
import os

import gym
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import (
    CheckpointCallback,
    CallbackList,
    BaseCallback,
)
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

import logging
from rl.mining_env import MiningEnv

logger = logging.getLogger(__name__)


class TensorboardMetricsCallback(BaseCallback):
    """Log custom metrics and save env stats alongside checkpoints."""

    def __init__(
        self,
        checkpoint_callback: CheckpointCallback | None = None,
        stats_path: str | None = None,
    ):
        super().__init__()
        self.checkpoint_callback = checkpoint_callback
        self.stats_path = stats_path

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

        if self.checkpoint_callback is not None:
            ckpt_cb = self.checkpoint_callback
            if ckpt_cb.n_calls % ckpt_cb.save_freq == 0 and ckpt_cb.n_calls > 0:
                path = os.path.join(
                    ckpt_cb.save_path,
                    f"{ckpt_cb.name_prefix}_{ckpt_cb.num_timesteps}_steps.zip",
                )
                self.logger.record("checkpoint/path", path)
                self.logger.record(
                    "checkpoint/num_timesteps", ckpt_cb.num_timesteps
                )
                if self.stats_path is not None:
                    self.training_env.save(ckpt_cb.save_path+self.stats_path)
        return True



def make_env(render_mode: str, max_steps=800, training=True, stats_path: str | None = None):
    def _init():
        env = MiningEnv(render_mode=render_mode, max_steps=max_steps, target_production=40000)
        return Monitor(env)

    env = DummyVecEnv([_init])
    if stats_path and os.path.exists(stats_path):
        env = VecNormalize.load(stats_path, env)
        env.training = training
    else:
        env = VecNormalize(env, training=training, norm_obs=True, norm_reward=False)
    return env


def train(
    timesteps: int,
    logdir: str,
    render_mode: str,
    resume_from: str | None = None,
):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    algo_class = PPO
    stats_file = os.path.join(logdir, "vecnormalize.pkl")
    env = make_env(render_mode=render_mode, max_steps=1000000, training=True, stats_path=stats_file if os.path.exists(stats_file) else None)

    checkpoint_callback = CheckpointCallback(
        save_freq=10000,
        save_path=os.path.join(logdir, "checkpoints"),
        name_prefix="ppo",
    )

    tb_callback = TensorboardMetricsCallback(
        checkpoint_callback=checkpoint_callback, stats_path=stats_file
    )

    callbacks = CallbackList([checkpoint_callback, tb_callback])

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
                vec_normalize_path = os.path.join(os.path.dirname(resume_from), "vecnormalize.pkl")
                logger.info(f"Resuming from checkpoint {resume_from}")
                logger.info(f"Loading vecnormalize from {vec_normalize_path}")
                
        model = algo_class.load(resume_from, env=env, device=device)
        env = VecNormalize.load(vec_normalize_path, env)
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
    except Exception as e:
        print("Training interrupted. Saving model...", e)
        model.save(os.path.join(logdir, "ppo_final"))
        env.save(stats_file)
        env.close()

    finally:
        model.save(os.path.join(logdir, "ppo_final"))
        env.save(stats_file)
        env.close()


def main():
    parser = argparse.ArgumentParser()
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
    train(args.timesteps, args.logdir, args.mode, args.resume_from)


if __name__ == "__main__":
    main()
