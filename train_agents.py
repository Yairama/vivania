import argparse
import os

import gymnasium as gym
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
            # New detailed metrics
            mineral_crusher = info.get("mineral_in_crusher")
            mineral_dump = info.get("mineral_in_dump")
            waste_dump = info.get("waste_in_dump")
            wrong_assign = info.get("wrong_assignments")
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
            if mineral_crusher is not None:
                self.logger.record("rollout/mineral_crusher", float(mineral_crusher))
            if mineral_dump is not None:
                self.logger.record("rollout/mineral_dump", float(mineral_dump))
            if waste_dump is not None:
                self.logger.record("rollout/waste_dump", float(waste_dump))
            if wrong_assign is not None:
                self.logger.record("rollout/wrong_assignments", float(wrong_assign))

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
                    self.training_env.save(self.stats_path)
        return True



def make_env(render_mode: str, max_steps=800, training=True, stats_path: str | None = None):
    def _init():
        env = MiningEnv(render_mode=render_mode, max_steps=max_steps)
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
    stats_file = os.path.join(logdir, "checkpoints","vecnormalize.pkl")
    env = make_env(render_mode=render_mode, max_steps=1000000, training=True, stats_path=stats_file if os.path.exists(stats_file) else None)

    checkpoint_callback = CheckpointCallback(
        save_freq=100000,
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
        if not os.path.exists(vec_normalize_path):
            alt = os.path.join(os.path.dirname(resume_from), "checkpoints", "vecnormalize.pkl")
            if os.path.exists(alt):
                vec_normalize_path = alt
        logger.info(f"Resuming from checkpoint {resume_from}")
        logger.info(f"Loading vecnormalize from {vec_normalize_path}")

        model = algo_class.load(resume_from, env=env, device=device)
        if os.path.exists(vec_normalize_path):
            env = VecNormalize.load(vec_normalize_path, env)
    else:
        policy = (
            "MultiInputPolicy"
            if isinstance(env.observation_space, gym.spaces.Dict)
            else "MlpPolicy"
        )
        model = PPO(
            "MultiInputPolicy",
            env,
            verbose=1,
            tensorboard_log=os.path.join(logdir, "tb"),
            
            # CAMBIOS CRÍTICOS para episodios largos:
            learning_rate=3e-4,     # Standard PPO
            gamma=0.999,            # ¡CRÍTICO! Para episodios de 5k steps
            gae_lambda=0.98,        # Alto para dependencias largas
            
            n_steps=6144,           # ¡CRÍTICO! Buffer >= ~80% episodio
            batch_size=512,         # Proporcional al buffer grande
            n_epochs=6,             # Menos épocas con buffer grande
            
            # Red más robusta para episodios complejos
            policy_kwargs=dict(
                net_arch=dict(
                    pi=[512, 256, 128],
                    vf=[512, 256, 128]
                ),
                activation_fn=torch.nn.Tanh
            ),
            
            clip_range=0.1,         # Más conservador
            ent_coef=0.005,         # Menos exploración
            device=device
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
