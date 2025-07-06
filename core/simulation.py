# core/simulation.py (Completamente rediseñado)
from core.mine_map import MineMap
from core.truck import Truck
from core.shovel import Shovel
from core.crusher import Crusher
from core.dump import Dump
from core.dijkstra import Dijkstra
import random
import numpy as np

class Simulation:
    def __init__(self):
        self.map = MineMap()
        self.dijkstra = Dijkstra(self.map.nodes)
        
        # Crear flota de camiones
        self.trucks = [
            Truck(i, 200, self.map.nodes["parking"], efficiency=random.uniform(0.7, 0.95)) 
            for i in range(8)
        ]
        
        # Crear shovels con diferentes características
        self.shovels = [
            Shovel(1, self.map.nodes["c1"], material_type='waste', ton_per_pass=35, efficiency=0.7),
            Shovel(2, self.map.nodes["c2"], material_type='waste', ton_per_pass=37, efficiency=0.8),
            Shovel(3, self.map.nodes["c3"], material_type='waste', ton_per_pass=40, efficiency=0.82),
            Shovel(4, self.map.nodes["c4"], material_type='waste', ton_per_pass=45, efficiency=0.89),
            Shovel(5, self.map.nodes["c5"], material_type='mineral', ton_per_pass=47, efficiency=0.92),
            Shovel(6, self.map.nodes["c6"], material_type='mineral', ton_per_pass=47, efficiency=0.91)
        ]
        
        self.crusher = Crusher(self.map.nodes["crusher"])
        self.dump = Dump(self.map.nodes["dump_zone"])
        
        # Estadísticas
        self.total_cycles = 0
        self.total_mineral_processed = 0
        self.total_waste_dumped = 0
        
    def update(self):
        # Actualizar equipos
        for shovel in self.shovels:
            shovel.update()
        self.crusher.update()
        self.dump.update()
        
        # Actualizar camiones
        for truck in self.trucks:
            truck.update_movement(self.map)
            
            # Lógica de asignación de tareas
            if truck.is_available():
                self._assign_truck_task(truck)
            elif truck.task == "waiting_shovel":
                self._handle_truck_at_shovel(truck)
            elif truck.task == "waiting_dump":
                self._handle_truck_at_dump(truck)
                
    def _assign_truck_task(self, truck):
        """Asigna una tarea al camión disponible"""
        if not truck.loading:
            # Camión vacío - asignar a shovel
            best_shovel = self._find_best_shovel()
            if best_shovel:
                route = self.dijkstra.get_shortest_path(
                    truck.position.name, 
                    best_shovel.node.name
                )
                if route:
                    truck.assign_route(route)
                    truck.task = "moving_to_shovel"
        else:
            # Camión cargado - asignar destino de descarga
            if truck.material_type == 'mineral':
                if self.crusher.can_accept_truck():
                    route = self.dijkstra.get_shortest_path(
                        truck.position.name, 
                        self.crusher.node.name
                    )
                    if route:
                        truck.assign_route(route)
                        truck.task = "moving_to_dump"
                elif self.dump.can_accept_truck():
                    # Si crusher está lleno, enviar a dump
                    route = self.dijkstra.get_shortest_path(
                        truck.position.name, 
                        self.dump.node.name
                    )
                    if route:
                        truck.assign_route(route)
                        truck.task = "moving_to_dump"
            else:
                # Material waste va al dump
                if self.dump.can_accept_truck():
                    route = self.dijkstra.get_shortest_path(
                        truck.position.name, 
                        self.dump.node.name
                    )
                    if route:
                        truck.assign_route(route)
                        truck.task = "moving_to_dump"
                        
    def _find_best_shovel(self):
        """Encuentra la mejor pala disponible"""
        available_shovels = [s for s in self.shovels if s.can_accept_truck()]
        if not available_shovels:
            return None
            
        # Priorizar palas con menos cola
        return min(available_shovels, key=lambda s: len(s.queue))
        
    def _handle_truck_at_shovel(self, truck):
        """Maneja camión esperando en pala"""
        for shovel in self.shovels:
            if (shovel.node.name == truck.position.name and 
                truck not in shovel.queue and 
                shovel.current_truck != truck):
                shovel.request_load(truck)
                break
                
    def _handle_truck_at_dump(self, truck):
        """Maneja camión esperando en punto de descarga"""
        if truck.position.name == "crusher":
            if truck not in self.crusher.queue and self.crusher.current_truck != truck:
                self.crusher.request_dump(truck)
        elif truck.position.name == "dump_zone":
            if truck not in self.dump.queue and self.dump.current_truck != truck:
                self.dump.request_dump(truck)
                
    def get_statistics(self):
        """Obtiene estadísticas de la simulación"""
        return {
            'total_cycles': self.total_cycles,
            'mineral_processed': self.crusher.total_processed,
            'waste_dumped': self.dump.total_dumped,
            'trucks_moving': len([t for t in self.trucks if t.is_moving()]),
            'trucks_waiting': len([t for t in self.trucks if 'waiting' in t.task]),
            'average_queue_length': sum(len(s.queue) for s in self.shovels) / len(self.shovels)
        }