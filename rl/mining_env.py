import gymnasium as gym
import numpy as np
from typing import List, Tuple, Dict, Any

from core.fms_manager import FMSManager

class MiningEnv(gym.Env):
    """Gym environment wrapper around the FMSManager for RL."""

    metadata = {"render.modes": ["human"]}

    def __init__(self):
        super().__init__()
        self.manager = FMSManager()

        # Observation space: 11 floats
        obs_low = np.zeros(11, dtype=np.float32)
        obs_high = np.ones(11, dtype=np.float32) * np.inf
        self.observation_space = gym.spaces.Box(low=obs_low, high=obs_high, dtype=np.float32)

        # Action space: index into list of available actions
        self.max_actions = len(self.manager.trucks) * 6  # worst case
        self.action_space = gym.spaces.Discrete(self.max_actions)

        self.valid_action_mask: np.ndarray = np.zeros(self.max_actions, dtype=np.float32)

    # ------------------------------------------------------------------
    # Environment core functions
    # ------------------------------------------------------------------
    def reset(self, *, seed: int | None = None, options: Dict[str, Any] | None = None):
        super().reset(seed=seed)
        # Recreate manager to reset state
        self.manager = FMSManager()
        obs = self._get_observation()
        info = {"action_mask": self.valid_action_mask}
        return obs, info

    def step(self, action: int):
        actions = self.manager.get_available_actions()
        if 0 <= action < len(actions):
            chosen = actions[action]
        else:
            chosen = None
        self.manager.execute_action(chosen)
        self.manager.update()
        obs = self._get_observation()
        reward = self._calculate_reward()
        terminated = False
        truncated = False
        info = {"action_mask": self.valid_action_mask}
        return obs, reward, terminated, truncated, info

    def render(self):
        stats = self.manager.get_statistics()
        print(stats)

    def close(self):
        pass

    # ------------------------------------------------------------------
    # Helper functions
    # ------------------------------------------------------------------
    def _calculate_reward(self) -> float:
        """Balanced reward: throughput + efficiency - queues."""
        throughput = self.manager.crusher.total_processed + self.manager.dump.total_dumped
        efficiency = np.mean([t.efficiency for t in self.manager.trucks])
        queues = sum(len(s.queue) for s in self.manager.shovels)
        queues += len(self.manager.crusher.queue) + len(self.manager.dump.queue)
        return throughput + efficiency - queues

    def _get_observation(self) -> np.ndarray:
        raw_obs = np.array(self.manager.get_observation_vector(), dtype=np.float32)
        # Normalization: simplistic, divide by fixed values
        norm_factors = np.array([
            1000.0, 10000.0, 10000.0, 3.0, 3.0,
            3.0, 3.0, 3.0, 3.0, 3.0, 3.0
        ], dtype=np.float32)
        obs = raw_obs / norm_factors
        obs = np.clip(obs, 0, 1)

        actions = self.manager.get_available_actions()
        self.valid_action_mask = np.zeros(self.max_actions, dtype=np.float32)
        self.valid_action_mask[:len(actions)] = 1.0
        return obs
