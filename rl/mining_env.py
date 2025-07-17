import gymnasium as gym
import numpy as np
from typing import Dict, Any

from core.fms_manager import FMSManager
from logger import get_logger





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
        max_steps: int = 1000000,
        target_production: float = 8000.0,
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

        # Structured observation space
        self._setup_observation_space()

        # Hybrid discrete action space: [truck_index, command]
        self.action_space = gym.spaces.MultiDiscrete(
            [len(self.manager.trucks), 9]
        )
        self.last_processed = 0.0
        self.last_dumped = 0.0
        self.last_mineral_lost = 0.0
        self.last_waste_wrong = 0.0
        self.last_hang_time = 0.0

    def _setup_observation_space(self):
        """Create a structured observation space using :class:`gym.spaces.Dict`."""
        n_shovels = len(self.manager.shovels)
        n_trucks = len(self.manager.trucks)

        self.observation_space = gym.spaces.Dict(
            {
                "global": gym.spaces.Box(low=-np.inf, high=np.inf, shape=(5,), dtype=np.float32),
                "equipment": gym.spaces.Box(
                    low=-np.inf,
                    high=np.inf,
                    shape=(4 + 2 * n_shovels,),
                    dtype=np.float32,
                ),
                "trucks": gym.spaces.Box(
                    low=-np.inf,
                    high=np.inf,
                    shape=(2 * n_trucks,),
                    dtype=np.float32,
                ),
                "aggregates": gym.spaces.Box(low=-np.inf, high=np.inf, shape=(3,), dtype=np.float32),
            }
        )

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
        self._setup_observation_space()
        self.step_count = 0
        if self.visualizer:
            # Reuse existing visualizer instance with new manager
            self.visualizer.sim = self.manager
        self.last_processed = 0.0
        self.last_dumped = 0.0
        self.last_mineral_lost = 0.0
        self.last_waste_wrong = 0.0
        self.last_hang_time = 0.0
        obs = self._get_observation()
        info = {}
        return obs, info

    def step(self, action: np.ndarray):
        truck_idx, cmd = int(action[0]), int(action[1])
        if cmd == 0:
            pass
        elif 1 <= cmd <= 6:
            truck = self.manager.trucks[truck_idx]
            if truck.is_available() and not truck.loading:
                self.manager.dispatch_shovel(truck.id, cmd)
        elif cmd == 7:
            truck = self.manager.trucks[truck_idx]
            if truck.is_available() and truck.loading:
                self.manager.dispatch_dump(truck.id, True)
        elif cmd == 8:
            truck = self.manager.trucks[truck_idx]
            if truck.is_available() and truck.loading:
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
            "throughput": production,
            "fleet_utilization": np.mean(
                [1.0 if not t.is_available() else 0.0 for t in self.manager.trucks]
            ),
            "lost_mineral": self.manager.dump.total_mineral_dumped,
            "waste_in_crusher": self.manager.crusher.total_waste_dumped,
            "hang_time": sum(s.hang_time for s in self.manager.shovels),
            # Additional metrics for detailed monitoring
            "mineral_in_crusher": self.manager.crusher.total_processed,
            "mineral_in_dump": self.manager.dump.total_mineral_dumped,
            "waste_in_dump": self.manager.dump.total_dumped,
            "wrong_assignments": self.manager.count_wrong_dump_assignments(),
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

        working = np.sum(
            [1.0 if t.is_available() else 0.0 for t in self.manager.trucks]
        )
        queue_penalty = (
            len(self.manager.crusher.queue)
            + len(self.manager.dump.queue)
            + sum(len(s.queue) for s in self.manager.shovels)
        )
        wrong_dump_penalty = self.manager.count_wrong_dump_assignments()
        penalty = 0.0
        penalty = 0.1 * queue_penalty
        penalty += 0.5 * delta_hang
        penalty += 2.0 * delta_lost
        penalty += 1.0 * delta_wrong

        # penalty += 200.0 * wrong_dump_penalty
        # print(f"Production: {production}, Penalty: {penalty}")
        print(f"working: {working}")
        return production - penalty - working

    def _get_observation(self) -> Dict[str, np.ndarray]:
        """Return a structured observation matching :attr:`observation_space`."""

        raw = self.manager.get_extended_observation_vector()

        idx = 0
        global_len = 5
        global_obs = np.array(raw[idx : idx + global_len], dtype=np.float32)
        idx += global_len

        equipment_len = 4 + 2 * len(self.manager.shovels)
        equipment_obs = np.array(raw[idx : idx + equipment_len], dtype=np.float32)
        idx += equipment_len

        trucks_len = 2 * len(self.manager.trucks)
        trucks_obs = np.array(raw[idx : idx + trucks_len], dtype=np.float32)
        idx += trucks_len

        aggregates_obs = np.array(raw[idx : idx + 3], dtype=np.float32)

        return {
            "global": global_obs,
            "equipment": equipment_obs,
            "trucks": trucks_obs,
            "aggregates": aggregates_obs,
        }

