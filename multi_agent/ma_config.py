from __future__ import annotations

from ray.rllib.algorithms.mappo import MAPPOConfig

from .ma_mining_env import MiningParallelEnv


def get_default_config(render_mode: str = "headless") -> MAPPOConfig:
    """Return a basic MAPPO configuration for the mining environment."""
    env = MiningParallelEnv(render_mode=render_mode)
    config = (
        MAPPOConfig()
        .environment(env=MiningParallelEnv, env_config={"render_mode": render_mode})
        .framework("torch")
        .rollouts(num_rollout_workers=0)
        .training(train_batch_size=4000)
    )
    single_obs_space = env.observation_spaces[env.possible_agents[0]]
    single_act_space = env.action_spaces[env.possible_agents[0]]
    config = config.multi_agent(
        policies={
            "shared_policy": (
                None,
                single_obs_space,
                single_act_space,
                {},
            )
        },
        policy_mapping_fn=lambda agent_id, *args, **kwargs: "shared_policy",
    )
    return config

