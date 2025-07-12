from core.mine_map import MineMap
from core.truck import Truck
from core.shovel import Shovel
from core.crusher import Crusher
from core.dump import Dump
from core.dijkstra import Dijkstra
from typing import List, Tuple, Dict, Any
from logger import get_logger

logger = get_logger(__name__)

class FMSManager:
    """Gestiona la flota y provee utilidades para entrenamiento RL."""

    def __init__(self):
        self.map = MineMap()
        self.dijkstra = Dijkstra(self.map.nodes)

        # Crear flota de camiones
        self.trucks = [
            Truck(1, 200, self.map.nodes["parking"], efficiency=0.85),
            Truck(2, 200, self.map.nodes["parking"], efficiency=0.75),
            Truck(3, 200, self.map.nodes["parking"], efficiency=0.90),
            Truck(4, 200, self.map.nodes["parking"], efficiency=0.88),
            Truck(5, 200, self.map.nodes["parking"], efficiency=0.82),
            Truck(6, 200, self.map.nodes["parking"], efficiency=0.78),
        ]

        # Crear palas
        self.shovels = [
            Shovel(1, self.map.nodes["c1"], material_type='waste', ton_per_pass=35, efficiency=0.7),
            Shovel(2, self.map.nodes["c2"], material_type='waste', ton_per_pass=37, efficiency=0.8),
            Shovel(3, self.map.nodes["c3"], material_type='mineral', ton_per_pass=40, efficiency=0.85),
            Shovel(4, self.map.nodes["c4"], material_type='mineral', ton_per_pass=45, efficiency=0.9),
            Shovel(5, self.map.nodes["c5"], material_type='mineral', ton_per_pass=47, efficiency=0.92),
            Shovel(6, self.map.nodes["c6"], material_type='waste', ton_per_pass=47, efficiency=0.88)
        ]

        self.crusher = Crusher(self.map.nodes["crusher"])
        self.dump = Dump(self.map.nodes["dump_zone"])

        self.tick_count = 0
        self._verify_connectivity()

    # ------------------------------------------------------------------
    # Actualizacion del estado (sin logica de asignacion)
    # ------------------------------------------------------------------
    def update(self):
        self.tick_count += 1

        # Actualizar equipos fijos
        for shovel in self.shovels:
            shovel.update()
        self.crusher.update()
        self.dump.update()

        # Actualizar camiones
        for truck in self.trucks:
            truck.update_movement(self.map, self.trucks)

            if truck.task == "waiting_shovel":
                self._handle_truck_at_shovel(truck)
            elif truck.task == "waiting_dump":
                self._handle_truck_at_dump(truck)

        if self.tick_count % 100 == 0:
            self._print_debug_info()


    def _handle_truck_at_shovel(self, truck: Truck):
        for shovel in self.shovels:
            if (shovel.node.name == truck.position.name and
                truck not in shovel.queue and
                shovel.current_truck != truck):
                shovel.request_load(truck)
                return

    def _handle_truck_at_dump(self, truck: Truck):
        if truck.position.name == "crusher":
            if truck not in self.crusher.queue and self.crusher.current_truck != truck:
                self.crusher.request_dump(truck)
                return
        elif truck.position.name == "dump_zone":
            if truck not in self.dump.queue and self.dump.current_truck != truck:
                self.dump.request_dump(truck)
                return
        route = self.dijkstra.get_shortest_path(truck.position.name, "parking")
        if route and len(route) > 1:
            truck.assign_route(route)
            truck.task = "returning"

    # ------------------------------------------------------------------
    # Funciones de soporte / debug
    # ------------------------------------------------------------------
    def _verify_connectivity(self):
        critical_routes = [
            ("parking", "c1"),
            ("parking", "c3"),
            ("c1", "dump_zone"),
            ("c3", "crusher"),
        ]
        for start, end in critical_routes:
            route = self.dijkstra.get_shortest_path(start, end)
            if not route:
                logger.warning(f"⚠️  Sin ruta de {start} a {end}")

    def _print_debug_info(self):
        task_counts: Dict[str, int] = {}
        for truck in self.trucks:
            task_counts[truck.task] = task_counts.get(truck.task, 0) + 1
        logger.info(f"\n=== TICK {self.tick_count} ===")
        logger.info(f"Estados de camiones: {task_counts}")
        logger.info(
            f"Mineral procesado: {self.crusher.total_processed:.1f}t"
        )
        logger.info(f"Waste descargado: {self.dump.total_dumped:.1f}t")

    # ------------------------------------------------------------------
    # Funciones para Reinforcement Learning
    # ------------------------------------------------------------------
    def get_system_state(self) -> Dict[str, Any]:
        return {
            'tick': self.tick_count,
            'mineral_processed': self.crusher.total_processed,
            'waste_dumped': self.dump.total_dumped,
            'truck_states': [t.get_status_info() for t in self.trucks],
            'shovel_queues': [len(s.queue) for s in self.shovels],
            'crusher_queue': len(self.crusher.queue),
            'dump_queue': len(self.dump.queue)
        }

    def get_observation_vector(self) -> List[float]:
        state = self.get_system_state()
        obs = [state['tick'], state['mineral_processed'], state['waste_dumped'],
               state['crusher_queue'], state['dump_queue']]
        obs.extend(state['shovel_queues'])
        return obs

    def get_available_actions(self) -> List[Tuple[str, int, int]]:
        actions = []
        for truck in self.trucks:
            if truck.is_available():
                if truck.loading:
                    actions.append(('dispatch_dump', truck.id, 0))  # crusher
                    actions.append(('dispatch_dump', truck.id, 1))  # dump zone
                else:
                    for shovel in self.shovels:
                        actions.append(('dispatch_shovel', truck.id, shovel.id))
        return actions

    def execute_action(self, action: Tuple[str, int, int]):
        if not action:
            return
        act, truck_id, target_id = action
        truck = next((t for t in self.trucks if t.id == truck_id), None)
        if not truck:
            return
        if act == 'dispatch_shovel':
            shovel = next((s for s in self.shovels if s.id == target_id), None)
            if shovel:
                route = self.dijkstra.get_shortest_path(truck.position.name, shovel.node.name)
                if route and len(route) > 1:
                    truck.assign_route(route)
                    truck.task = 'moving_to_shovel'
        elif act == 'dispatch_dump':
            destination = 'crusher' if target_id == 0 else 'dump_zone'
            route = self.dijkstra.get_shortest_path(truck.position.name, destination)
            if route and len(route) > 1:
                truck.assign_route(route)
                truck.task = 'moving_to_dump'

    def calculate_reward(self) -> float:
        return self.crusher.total_processed + self.dump.total_dumped

    def get_statistics(self):
        return {
            'tick_count': self.tick_count,
            'mineral_processed': self.crusher.total_processed,
            'waste_dumped': self.dump.total_dumped,
            'trucks_moving': len([t for t in self.trucks if t.is_moving()]),
            'trucks_waiting': len([t for t in self.trucks if 'waiting' in t.task])
        }
