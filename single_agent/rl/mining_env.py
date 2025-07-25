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

        # Multi-discrete action space: command for each truck
        # Each truck receives an integer command in the range [0, 8]
        # TODO: Find a way to make assignations only in available trucks.
        self.action_space = gym.spaces.MultiDiscrete([9] * len(self.manager.trucks))
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
                "action_mask": gym.spaces.Box(
                    low=0,
                    high=1,
                    shape=(9 * n_trucks,),
                    dtype=np.int8,
                ),
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
        info = {"action_mask": self._get_action_mask()}
        return obs, info

    def step(self, action: np.ndarray):
        """Execute one step of the environment.

        Parameters
        ----------
        action : np.ndarray
            Array with one command per truck. Each command is an integer in
            ``[0, 8]``:

            ``0`` - no-op
            ``1-6`` - dispatch to shovel ``cmd``
            ``7`` - dispatch loaded truck to crusher
            ``8`` - dispatch loaded truck to dump site
        """

        for truck_idx, cmd in enumerate(action):
            cmd = int(cmd)
            truck = self.manager.trucks[truck_idx]

            if cmd == 0:
                continue
            elif 1 <= cmd <= len(self.manager.shovels):
                if truck.is_available() and not truck.loading:
                    self.manager.dispatch_shovel(truck.id, cmd)
            elif cmd == 7:
                if truck.is_available() and truck.loading:
                    self.manager.dispatch_dump(truck.id, True)
            elif cmd == 8:
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
            "fleet_utilization": np.sum(
                [1.0 if t.is_available() else 0.0 for t in self.manager.trucks]
            ),
            "lost_mineral": self.manager.dump.total_mineral_dumped,
            "waste_in_crusher": self.manager.crusher.total_waste_dumped,
            "hang_time": sum(s.hang_time for s in self.manager.shovels),
            # Additional metrics for detailed monitoring
            "mineral_in_crusher": self.manager.crusher.total_processed,
            "mineral_in_dump": self.manager.dump.total_mineral_dumped,
            "waste_in_dump": self.manager.dump.total_dumped,
            "wrong_assignments": self.manager.count_wrong_dump_assignments(),
            "action_mask": self._get_action_mask(),
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

    def _get_action_mask(self) -> np.ndarray:
        """Return a binary mask for valid actions for each truck."""
        mask = []
        n_shovels = len(self.manager.shovels)
        for truck in self.manager.trucks:
            local = [1]  # no-op is always valid
            if truck.is_available() and not truck.loading:
                local.extend([1] * n_shovels)
            else:
                local.extend([0] * n_shovels)

            if truck.is_available() and truck.loading:
                local.extend([1, 1])
            else:
                local.extend([0, 0])

            mask.extend(local)

        return np.array(mask, dtype=np.int8)

    # This method name is expected by MaskablePPO
    def action_masks(self) -> np.ndarray:
        return self._get_action_mask()

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
        # penalty += 0.5 * delta_hang
        penalty += 2.0 * delta_lost
        penalty += 1.0 * delta_wrong

        # penalty += 200.0 * wrong_dump_penalty
        # print(f"Production: {production}, Penalty: {penalty}")
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
            "action_mask": self._get_action_mask(),
        }

