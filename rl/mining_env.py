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
    max_steps : int, optional
        Maximum number of steps per episode before truncation.
    target_production : float, optional
        Total tonnage after which the episode terminates.
    """

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        render_mode: str = "headless",
        max_steps: int = 800,
        target_production: float = 400.0,
    ):
        super().__init__()
        self.render_mode = render_mode
        self.manager = FMSManager()
        self.max_steps = max_steps
        self.target_production = target_production
        self.step_count = 0
        self.visualizer = None
        self.clock = None
        self._visual_paused = False
        if self.render_mode == "visual":
            self._init_pygame()

        # Observation space dimension based on fleet size
        self.obs_dim = len(self.manager.get_extended_observation_vector())
        obs_low = np.zeros(self.obs_dim, dtype=np.float32)
        obs_high = np.ones(self.obs_dim, dtype=np.float32) * np.inf
        self.observation_space = gym.spaces.Box(
            low=obs_low, high=obs_high, dtype=np.float32
        )

        # Simplified action space (0=nothing, 1-6=shovels, 7=crusher, 8=dump)
        self.action_space = gym.spaces.Discrete(9)

        self.valid_action_mask: np.ndarray = np.zeros(9, dtype=np.float32)
        self.running_stats = RunningStats(self.obs_dim)
        self.last_processed = 0.0
        self.last_dumped = 0.0
        self.last_mineral_lost = 0.0
        self.last_waste_wrong = 0.0
        self.last_hang_time = 0.0

    def _init_pygame(self):
        """Initialize pygame and the visualizer."""
        import pygame
        from core.visualizer import Visualizer

        pygame.init()
        self.clock = pygame.time.Clock()
        self.visualizer = Visualizer(self.manager)

    def _handle_pygame_events(self):
        """Process and respond to pygame events."""
        import pygame

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                # Switch to headless mode gracefully
                pygame.quit()
                self.visualizer = None
                self.render_mode = "headless"
                self.clock = None
                break
            else:
                if self.visualizer:
                    self.visualizer.handle_input(event)

    # ------------------------------------------------------------------
    # Environment core functions
    # ------------------------------------------------------------------
    def reset(self, *, seed: int | None = None, options: Dict[str, Any] | None = None):
        super().reset(seed=seed)
        # Recreate manager to reset state
        self.manager = FMSManager()
        # Recompute observation space in case fleet size changed
        self.obs_dim = len(self.manager.get_extended_observation_vector())
        self.observation_space = gym.spaces.Box(
            low=np.zeros(self.obs_dim, dtype=np.float32),
            high=np.ones(self.obs_dim, dtype=np.float32) * np.inf,
            dtype=np.float32,
        )
        self.step_count = 0
        if self.visualizer:
            # Reuse existing visualizer instance with new manager
            self.visualizer.sim = self.manager
        self.running_stats = RunningStats(self.obs_dim)
        self.last_processed = 0.0
        self.last_dumped = 0.0
        self.last_mineral_lost = 0.0
        self.last_waste_wrong = 0.0
        self.last_hang_time = 0.0
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
        if self.visualizer and not self._visual_paused:
            import pygame

            self.clock.tick(60)
            self._handle_pygame_events()
            try:
                self.visualizer.draw()
            except pygame.error:
                pygame.quit()
                self.visualizer = None
                self.render_mode = "headless"
                self.clock = None
        obs = self._get_observation()
        reward = self._calculate_reward()
        self.step_count += 1
        production = (
            self.manager.crusher.total_processed + self.manager.dump.total_dumped
        )
        terminated = production >= self.target_production
        truncated = self.step_count >= self.max_steps
        info = {
            "action_mask": self.valid_action_mask,
            "throughput": production,
            "fleet_utilization": np.mean(
                [1.0 if not t.is_available() else 0.0 for t in self.manager.trucks]
            ),
            "lost_mineral": self.manager.dump.total_mineral_dumped,
            "waste_in_crusher": self.manager.crusher.total_waste_dumped,
            "hang_time": sum(s.hang_time for s in self.manager.shovels),
        }
        return obs, reward, terminated, truncated, info

    def render(self):
        stats = self.manager.get_statistics()
        logger.info(stats)

    def pause_visualizer(self):
        """Temporarily disable visual updates."""
        self._visual_paused = True

    def resume_visualizer(self):
        """Re-enable visual updates if available."""
        self._visual_paused = False

    def close(self):
        if self.visualizer:
            import pygame

            pygame.quit()
            self.visualizer = None
            self.clock = None

    # ------------------------------------------------------------------
    # Helper functions
    # ------------------------------------------------------------------
    def _calculate_reward(self) -> float:
        """Balanced reward with production deltas and penalties."""
        delta_mineral = self.manager.crusher.total_processed - self.last_processed
        delta_waste = self.manager.dump.total_dumped - self.last_dumped
        delta_lost = self.manager.dump.total_mineral_dumped - self.last_mineral_lost
        delta_wrong = self.manager.crusher.total_waste_dumped - self.last_waste_wrong
        delta_hang = sum(s.hang_time for s in self.manager.shovels) - self.last_hang_time

        self.last_processed = self.manager.crusher.total_processed
        self.last_dumped = self.manager.dump.total_dumped
        self.last_mineral_lost = self.manager.dump.total_mineral_dumped
        self.last_waste_wrong = self.manager.crusher.total_waste_dumped
        self.last_hang_time = sum(s.hang_time for s in self.manager.shovels)

        production = delta_waste + 2.0 * delta_mineral

        working = np.mean(
            [1.0 if not t.is_available() else 0.0 for t in self.manager.trucks]
        )
        queue_penalty = (
            len(self.manager.crusher.queue)
            + len(self.manager.dump.queue)
            + sum(len(s.queue) for s in self.manager.shovels)
        )
        penalty = 0.1 * queue_penalty
        penalty += 0.5 * delta_hang
        penalty += 2.0 * delta_lost
        penalty += 1.0 * delta_wrong
        return production + working - penalty

    def _get_observation(self) -> np.ndarray:
        raw_obs = np.array(
            self.manager.get_extended_observation_vector(), dtype=np.float32
        )
        self.running_stats.update(raw_obs[None, :])
        obs = self.running_stats.normalize(raw_obs)

        self._update_action_mask()
        return obs

    # ------------------------------------------------------------------
    # Running stats utilities
    # ------------------------------------------------------------------
    def save_running_stats(self, path: str):
        """Save running normalisation statistics to a file."""
        np.savez(
            path,
            mean=self.running_stats.mean,
            var=self.running_stats.var,
            count=self.running_stats.count,
        )

    def load_running_stats_from_file(self, path: str):
        """Load running normalisation statistics from ``path``."""
        data = np.load(path)
        self.running_stats.mean = data["mean"]
        self.running_stats.var = data["var"]
        self.running_stats.count = data["count"].item() if hasattr(data["count"], "item") else data["count"]

    def get_normalised_observation(self) -> np.ndarray:
        """Return current observation using existing running stats without updating them."""
        raw_obs = np.array(
            self.manager.get_extended_observation_vector(), dtype=np.float32
        )
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
