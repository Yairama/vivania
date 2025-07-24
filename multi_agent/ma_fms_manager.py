from __future__ import annotations
from typing import Dict, List, Tuple
import numpy as np

from core.fms_manager import FMSManager


class MultiAgentFMSManager(FMSManager):
    """Extension of :class:`FMSManager` for multi-agent experiments.

    The manager exposes per-agent observations, supports executing a
    dictionary of actions and tracks individual rewards. The goal of this
    class is to provide a light-weight wrapper around the existing single
    agent logic without modifying it.
    """

    def __init__(self):
        super().__init__()
        # Previous task of each truck for reward bookkeeping
        self._prev_tasks: Dict[int, str] = {t.id: t.task for t in self.trucks}
        # Record load and material when a truck starts dumping
        self._dump_records: Dict[int, Tuple[float, str | None]] = {}
        # Accumulated rewards for each agent since last call
        self._agent_rewards: Dict[int, float] = {t.id: 0.0 for t in self.trucks}

    # ------------------------------------------------------------------
    # Action interface
    # ------------------------------------------------------------------
    def execute_multi_actions(self, actions: Dict[int, int]):
        """Execute a dictionary of actions keyed by truck id."""
        n_shovels = len(self.shovels)
        for truck_id, cmd in actions.items():
            truck = next((t for t in self.trucks if t.id == truck_id), None)
            if truck is None:
                continue
            if cmd == 0:
                continue
            elif 1 <= cmd <= n_shovels:
                if truck.is_available() and not truck.loading:
                    self.dispatch_shovel(truck.id, cmd)
            elif cmd == n_shovels + 1:
                if truck.is_available() and truck.loading:
                    self.dispatch_dump(truck.id, True)
            elif cmd == n_shovels + 2:
                if truck.is_available() and truck.loading:
                    self.dispatch_dump(truck.id, False)

    # ------------------------------------------------------------------
    # Observations
    # ------------------------------------------------------------------
    def get_agent_observation(self, truck_id: int) -> List[float]:
        """Return observation vector for a single truck."""
        truck = next((t for t in self.trucks if t.id == truck_id), None)
        if truck is None:
            return []
        local = self._get_local_state(truck)
        coord = self._get_coordination_state(truck)
        global_state = self._get_global_state()
        return local + coord + global_state

    def _get_local_state(self, truck) -> List[float]:
        load_ratio = truck.current_load / truck.capacity
        task_enc = self._encode_task(truck.task)
        mat_enc = self._encode_material_type(truck.material_type)
        dist_shovel = self.get_distance_between(truck.position.name, self._nearest_shovel_name(truck.position.name))
        dist_crusher = self.get_distance_between(truck.position.name, "crusher")
        dist_dump = self.get_distance_between(truck.position.name, "dump_zone")
        speed = truck.get_current_speed()
        waiting = 1.0 if "waiting" in truck.task else 0.0
        local = [
            truck.position.x,
            truck.position.y,
            load_ratio,
            float(truck.loading),
            task_enc,
            mat_enc,
            dist_shovel,
            dist_crusher,
            dist_dump,
            speed,
            waiting,
            truck.efficiency,
        ]
        return local

    def _get_coordination_state(self, truck) -> List[float]:
        # Count trucks on same segment or node
        same_segment = len([
            t for t in self.trucks
            if t is not truck and t.current_segment == truck.current_segment and t.current_segment is not None
        ])
        same_node = len([
            t for t in self.trucks
            if t is not truck and t.position == truck.position and t.current_segment is None
        ])
        crusher_q = len(self.crusher.queue)
        dump_q = len(self.dump.queue)
        shovel_q = [len(s.queue) for s in self.shovels]
        congestion = float(same_segment + same_node)
        coord = [same_segment, same_node, crusher_q, dump_q] + shovel_q[:4]
        while len(coord) < 8:
            coord.append(0.0)
        coord[4] = congestion  # simple congestion indicator
        return coord[:8]

    def _get_global_state(self) -> List[float]:
        throughput = self.crusher.total_processed + self.dump.total_dumped
        free_trucks = len([t for t in self.trucks if t.is_available()])
        busy_shovels = sum(1 for s in self.shovels if s.current_truck)
        busy_crusher = 1 if self.crusher.current_truck else 0
        busy_dump = 1 if self.dump.current_truck else 0
        return [throughput, free_trucks, busy_shovels, busy_crusher, busy_dump]

    # ------------------------------------------------------------------
    # Reward tracking
    # ------------------------------------------------------------------
    def update(self):
        """Update simulation and compute per-agent rewards."""
        super().update()
        self._update_agent_rewards()

    def _update_agent_rewards(self):
        for truck in self.trucks:
            prev_task = self._prev_tasks[truck.id]
            # Detect start of dumping to record load and material
            if truck.task == "dumping" and prev_task != "dumping":
                self._dump_records[truck.id] = (truck.current_load, truck.material_type)
            # Detect end of dumping to assign reward
            if truck.task == "waiting_assignment" and prev_task == "dumping":
                load, mat = self._dump_records.get(truck.id, (0.0, None))
                reward = load if mat == "mineral" else load
                self._agent_rewards[truck.id] += reward
                if truck.id in self._dump_records:
                    del self._dump_records[truck.id]
            self._prev_tasks[truck.id] = truck.task

    def get_individual_rewards(self) -> Dict[int, float]:
        """Return and reset accumulated rewards for all agents."""
        rewards = {k: v for k, v in self._agent_rewards.items()}
        for k in rewards.keys():
            self._agent_rewards[k] = 0.0
        return rewards
