import gymnasium as gym
import numpy as np
from typing import Dict, Any

from core.fms_manager import FMSManager
from logger import get_logger


class RunningStats:
    """Simple running mean/std calculator for normalisation."""

    def __init__(self, shape):
        self.mean = np.zeros(shape, dtype=np.float32)
        self.var = np.ones(shape, dtype=np.float32)
        self.count = 1e-4

    def update(self, x: np.ndarray):
        batch_mean = x.mean(axis=0)
        batch_var = x.var(axis=0)
        batch_count = x.shape[0]

        delta = batch_mean - self.mean
        tot_count = self.count + batch_count

        new_mean = self.mean + delta * batch_count / tot_count
        m_a = self.var * self.count
        m_b = batch_var * batch_count
        M2 = m_a + m_b + np.square(delta) * self.count * batch_count / tot_count
        new_var = M2 / tot_count

        self.mean = new_mean
        self.var = new_var
        self.count = tot_count

    def normalize(self, x: np.ndarray) -> np.ndarray:
        return np.clip((x - self.mean) / (np.sqrt(self.var) + 1e-8), 0.0, 1.0)

logger = get_logger(__name__)

class MiningEnv(gym.Env):
    """Gym environment wrapper around the FMSManager for RL.

    Parameters
    ----------
    render_mode : str, optional
        If ``"visual"`` a pygame window will be opened and the environment
        state will be rendered every step. ``"headless"`` (default) disables
        any visual output.
    """

    metadata = {"render.modes": ["human"]}

    def __init__(self, render_mode: str = "headless"):
        super().__init__()
        self.render_mode = render_mode
        self.manager = FMSManager()
        self.visualizer = None
        if self.render_mode == "visual":
            import pygame
            from core.visualizer import Visualizer
            pygame.init()
            self.clock = pygame.time.Clock()
            self.visualizer = Visualizer(self.manager)

        # Observation space: extended 54-dimensional vector
        self.obs_dim = 54
        obs_low = np.zeros(self.obs_dim, dtype=np.float32)
        obs_high = np.ones(self.obs_dim, dtype=np.float32) * np.inf
        self.observation_space = gym.spaces.Box(low=obs_low, high=obs_high, dtype=np.float32)

        # Simplified action space (0=nothing, 1-6=shovels, 7=crusher, 8=dump)
        self.action_space = gym.spaces.Discrete(9)

        self.valid_action_mask: np.ndarray = np.zeros(9, dtype=np.float32)
        self.running_stats = RunningStats(self.obs_dim)
        self.last_processed = 0.0
        self.last_dumped = 0.0

    # ------------------------------------------------------------------
    # Environment core functions
    # ------------------------------------------------------------------
    def reset(self, *, seed: int | None = None, options: Dict[str, Any] | None = None):
        super().reset(seed=seed)
        # Recreate manager to reset state
        self.manager = FMSManager()
        if self.visualizer:
            # Recreate visualizer with the new manager
            from core.visualizer import Visualizer
            self.visualizer = Visualizer(self.manager)
        self.running_stats = RunningStats(self.obs_dim)
        self.last_processed = 0.0
        self.last_dumped = 0.0
        obs = self._get_observation()
        info = {"action_mask": self.valid_action_mask}
        return obs, info

    def step(self, action: int):
        if action == 0:
            pass
        elif 1 <= action <= 6:
            truck = self.manager.get_available_truck(loaded=False)
            if truck:
                self.manager.dispatch_shovel(truck.id, action)
        elif action == 7:
            truck = self.manager.get_available_truck(loaded=True)
            if truck:
                self.manager.dispatch_dump(truck.id, True)
        elif action == 8:
            truck = self.manager.get_available_truck(loaded=True)
            if truck:
                self.manager.dispatch_dump(truck.id, False)
        self.manager.update()
        if self.visualizer:
            import pygame
            self.clock.tick(60)
            pygame.event.pump()
            self.visualizer.draw()
        obs = self._get_observation()
        reward = self._calculate_reward()
        terminated = False
        truncated = False
        info = {"action_mask": self.valid_action_mask}
        return obs, reward, terminated, truncated, info

    def render(self):
        stats = self.manager.get_statistics()
        logger.info(stats)

    def close(self):
        if self.visualizer:
            import pygame
            pygame.quit()

    # ------------------------------------------------------------------
    # Helper functions
    # ------------------------------------------------------------------
    def _calculate_reward(self) -> float:
        """Balanced reward with production deltas and penalties."""
        delta_mineral = self.manager.crusher.total_processed - self.last_processed
        delta_waste = self.manager.dump.total_dumped - self.last_dumped
        self.last_processed = self.manager.crusher.total_processed
        self.last_dumped = self.manager.dump.total_dumped

        production = delta_waste + 2.0 * delta_mineral

        working = np.mean([1.0 if not t.is_available() else 0.0 for t in self.manager.trucks])
        queue_penalty = (
            len(self.manager.crusher.queue)
            + len(self.manager.dump.queue)
            + sum(len(s.queue) for s in self.manager.shovels)
        )
        return production + working - 0.1 * queue_penalty

    def _get_observation(self) -> np.ndarray:
        raw_obs = np.array(self.manager.get_extended_observation_vector(), dtype=np.float32)
        self.running_stats.update(raw_obs[None, :])
        obs = self.running_stats.normalize(raw_obs)

        self._update_action_mask()
        return obs

    def _update_action_mask(self):
        mask = np.zeros(9, dtype=np.float32)
        mask[0] = 1.0
        any_empty = any(t.is_available() and not t.loading for t in self.manager.trucks)
        any_loaded = any(t.is_available() and t.loading for t in self.manager.trucks)
        if any_empty:
            for i, shovel in enumerate(self.manager.shovels, start=1):
                if shovel.can_accept_truck():
                    mask[i] = 1.0
        if any_loaded:
            if self.manager.crusher.can_accept_truck():
                mask[7] = 1.0
            if self.manager.dump.can_accept_truck():
                mask[8] = 1.0
        self.valid_action_mask = mask
