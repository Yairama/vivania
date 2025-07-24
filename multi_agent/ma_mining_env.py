from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
from gymnasium import spaces
from pettingzoo.utils import ParallelEnv

from .ma_fms_manager import MultiAgentFMSManager


class MiningParallelEnv(ParallelEnv):
    """PettingZoo parallel environment wrapping :class:`MultiAgentFMSManager`."""

    metadata = {"name": "MiningParallel-v0"}

    def __init__(
        self,
        max_steps: int = 100000,
        target_production: float = 8000.0,
        render_mode: str = "headless",
    ):
        self.max_steps = max_steps
        self.target_production = target_production
        self.render_mode = render_mode
        self.manager = MultiAgentFMSManager()
        self.step_count = 0
        self.possible_agents = [f"truck_{i}" for i in range(len(self.manager.trucks))]
        self.agents = list(self.possible_agents)
        self.visualizer = None
        self.clock = None
        if self.render_mode == "visual":
            self._init_pygame()

        obs_dim = len(self.manager.get_agent_observation(self.manager.trucks[0].id))
        n_actions = len(self.manager.shovels) + 3
        self.observation_spaces = {
            a: spaces.Box(low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32)
            for a in self.possible_agents
        }
        self.action_spaces = {a: spaces.Discrete(n_actions) for a in self.possible_agents}

    def _get_action_mask(self, truck) -> np.ndarray:
        mask = [1]
        n_shovels = len(self.manager.shovels)
        if truck.is_available() and not truck.loading:
            mask.extend([1] * n_shovels)
        else:
            mask.extend([0] * n_shovels)
        if truck.is_available() and truck.loading:
            mask.extend([1, 1])
        else:
            mask.extend([0, 0])
        return np.array(mask, dtype=np.int8)

    def _get_masks(self) -> Dict[str, np.ndarray]:
        return {
            f"truck_{i}": self._get_action_mask(truck)
            for i, truck in enumerate(self.manager.trucks)
        }

    # ------------------------------------------------------------------
    # Pygame helpers
    # ------------------------------------------------------------------
    def _init_pygame(self):
        import pygame
        from core.visualizer import Visualizer

        pygame.init()
        self.clock = pygame.time.Clock()
        self.visualizer = Visualizer(self.manager)

    def _handle_pygame_events(self):
        import pygame

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                self.visualizer = None
                self.render_mode = "headless"
                self.clock = None
                break
            else:
                if self.visualizer:
                    self.visualizer.handle_input(event)
    # ------------------------------------------------------------------
    # ParallelEnv API
    # ------------------------------------------------------------------
    def reset(self, seed: int | None = None, options: Dict | None = None) -> Tuple[Dict, Dict]:
        self.manager = MultiAgentFMSManager()
        self.step_count = 0
        self.agents = list(self.possible_agents)
        if self.visualizer:
            self.visualizer.sim = self.manager
        observations = {
            a: np.array(self.manager.get_agent_observation(i + 1), dtype=np.float32)
            for i, a in enumerate(self.agents)
        }
        infos = {a: {"action_mask": self._get_action_mask(self.manager.trucks[i])} for i, a in enumerate(self.agents)}
        return observations, infos

    def step(self, actions: Dict[str, int]):
        actions_dict = {i + 1: int(actions.get(a, 0)) for i, a in enumerate(self.agents)}
        self.manager.execute_multi_actions(actions_dict)
        self.manager.update()
        self.step_count += 1
        if self.render_mode == "visual" and self.visualizer:
            self._handle_pygame_events()
            self.visualizer.draw()
            if self.clock:
                self.clock.tick(60)

        observations = {
            a: np.array(self.manager.get_agent_observation(i + 1), dtype=np.float32)
            for i, a in enumerate(self.agents)
        }
        reward_dict = self.manager.get_individual_rewards()
        rewards = {f"truck_{i}": reward_dict.get(i + 1, 0.0) for i in range(len(self.agents))}

        production = self.manager.crusher.total_processed + self.manager.dump.total_dumped
        terminated = production >= self.target_production
        truncated = self.step_count >= self.max_steps

        terminations = {a: terminated for a in self.agents}
        truncations = {a: truncated for a in self.agents}
        terminations["__all__"] = terminated or truncated
        truncations["__all__"] = terminated or truncated

        infos = {a: {"action_mask": self._get_action_mask(self.manager.trucks[i])} for i, a in enumerate(self.agents)}

        if terminations["__all__"]:
            self.agents = []

        return observations, rewards, terminations, truncations, infos

    def render(self):
        if self.visualizer:
            self._handle_pygame_events()
            self.visualizer.draw()
            if self.clock:
                self.clock.tick(60)

    def close(self):
        self.agents = []
        if self.visualizer:
            import pygame

            pygame.quit()
            self.visualizer = None
            self.clock = None
        