# core/simulation.py (Corregido)
from core.mine_map import MineMap
from core.truck import Truck
from core.shovel import Shovel
from core.crusher import Crusher
from core.dump import Dump
from core.dijkstra import Dijkstra
import random

class Simulation:
    def __init__(self):
        self.map = MineMap()
        self.dijkstra = Dijkstra(self.map.nodes)
        
        # Crear flota de camiones (reducida para debug)
        self.trucks = [
            Truck(i, 200, self.map.nodes["parking"], efficiency=0.85) 
            for i in range(6)  # Reducido de 8 a 6
        ]
        
        # Crear shovels con diferentes características
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
        
        # Estadísticas
        self.tick_count = 0
        self.total_cycles = 0
        
        print(f"Simulación inicializada:")
        print(f"- {len(self.trucks)} camiones")
        print(f"- {len(self.shovels)} palas")
        print(f"- Palas de mineral: {[s.id for s in self.shovels if s.material_type == 'mineral']}")
        print(f"- Palas de waste: {[s.id for s in self.shovels if s.material_type == 'waste']}")
        
        # Verificar conectividad
        self._verify_connectivity()
        
    def _verify_connectivity(self):
        """Verifica que todos los nodos importantes estén conectados"""
        critical_routes = [
            ("parking", "c1"),
            ("parking", "c3"), 
            ("c1", "dump_zone"),
            ("c3", "crusher"),
        ]
        
        print("\nVerificando conectividad:")
        for start, end in critical_routes:
            route = self.dijkstra.get_shortest_path(start, end)
            if route:
                print(f"✓ {start} -> {end}: {len(route)} nodos")
            else:
                print(f"✗ ERROR: No hay ruta de {start} a {end}")
        
    def update(self):
        self.tick_count += 1
        
        # Actualizar equipos
        for shovel in self.shovels:
            shovel.update()
        self.crusher.update()
        self.dump.update()
        
        # Actualizar camiones
        for truck in self.trucks:
            truck.update_movement(self.map, self.trucks)
            
            # Lógica de asignación de tareas
            if truck.is_available():
                self._assign_truck_task(truck)
            elif truck.task == "waiting_shovel":
                self._handle_truck_at_shovel(truck)
            elif truck.task == "waiting_dump":
                self._handle_truck_at_dump(truck)
                
        # Debug cada 100 ticks
        if self.tick_count % 100 == 0:
            self._print_debug_info()
                
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
                if route and len(route) > 1:
                    truck.assign_route(route)
                    truck.task = "moving_to_shovel"
                    print(f"Camión {truck.id} asignado a pala {best_shovel.id} ({best_shovel.material_type})")
                else:
                    print(f"ERROR: No se encontró ruta de {truck.position.name} a {best_shovel.node.name}")
        else:
            # Camión cargado - asignar destino de descarga
            self._assign_dump_destination(truck)
                        
    def _assign_dump_destination(self, truck):
        """Asigna destino de descarga para camión cargado"""
        destination = None
        
        if truck.material_type == 'mineral':
            # Mineral va preferentemente al crusher
            if self.crusher.can_accept_truck():
                destination = "crusher"
            elif self.dump.can_accept_truck():
                destination = "dump_zone"  # Overflow al dump
        else:
            # Waste va al dump
            if self.dump.can_accept_truck():
                destination = "dump_zone"
                
        if destination:
            route = self.dijkstra.get_shortest_path(truck.position.name, destination)
            if route and len(route) > 1:
                truck.assign_route(route)
                truck.task = "moving_to_dump"
                print(f"Camión {truck.id} va a descargar {truck.material_type} en {destination}")
            else:
                print(f"ERROR: No se encontró ruta de {truck.position.name} a {destination}")
        else:
            print(f"Camión {truck.id}: No hay capacidad de descarga disponible")
        
    def _find_best_shovel(self):
        """Encuentra la mejor pala disponible"""
        available_shovels = [s for s in self.shovels if s.can_accept_truck()]
        if not available_shovels:
            print("No hay palas disponibles")
            return None
            
        # Balancear entre mineral y waste
        mineral_shovels = [s for s in available_shovels if s.material_type == 'mineral']
        waste_shovels = [s for s in available_shovels if s.material_type == 'waste']
        
        # Preferir palas de mineral si hay menos mineral procesado
        if mineral_shovels and (not waste_shovels or self.crusher.total_processed < self.dump.total_dumped):
            best = min(mineral_shovels, key=lambda s: len(s.queue))
        else:
            best = min(available_shovels, key=lambda s: len(s.queue))
            
        return best
        
    def _handle_truck_at_shovel(self, truck):
        """Maneja camión esperando en pala"""
        for shovel in self.shovels:
            if (shovel.node.name == truck.position.name and 
                truck not in shovel.queue and 
                shovel.current_truck != truck):
                shovel.request_load(truck)
                print(f"Camión {truck.id} se une a cola de pala {shovel.id}")
                return
                
    def _handle_truck_at_dump(self, truck):
        """Maneja camión esperando en punto de descarga"""
        if truck.position.name == "crusher":
            if truck not in self.crusher.queue and self.crusher.current_truck != truck:
                self.crusher.request_dump(truck)
                print(f"Camión {truck.id} se une a cola del crusher")
                return
        elif truck.position.name == "dump_zone":
            if truck not in self.dump.queue and self.dump.current_truck != truck:
                self.dump.request_dump(truck)
                print(f"Camión {truck.id} se une a cola del dump")
                return
                
        # Si no pudo unirse a ninguna cola, regresar al parking
        print(f"Camión {truck.id} no pudo unirse a cola, regresando")
        route = self.dijkstra.get_shortest_path(truck.position.name, "parking")
        if route and len(route) > 1:
            truck.assign_route(route)
            truck.task = "returning"
                
    def _print_debug_info(self):
        """Imprime información de debug"""
        print(f"\n=== TICK {self.tick_count} ===")
        
        # Estado de camiones
        task_counts = {}
        for truck in self.trucks:
            task_counts[truck.task] = task_counts.get(truck.task, 0) + 1
        print(f"Estados de camiones: {task_counts}")
        
        # Detalles de camiones en movimiento
        moving_trucks = [t for t in self.trucks if t.is_moving()]
        if moving_trucks:
            print("Camiones en movimiento:")
            for truck in moving_trucks:
                info = truck.get_status_info()
                print(f"  T{info['id']}: {info['position']} -> {info['target']} (timer: {info['timer']})")
        
        # Estado de colas
        print(f"Colas - Shovels: {[(s.id, len(s.queue)) for s in self.shovels]}")
        print(f"Colas - Crusher: {len(self.crusher.queue)}, Dump: {len(self.dump.queue)}")
        
        # Producción
        print(f"Mineral procesado: {self.crusher.total_processed:.1f} tons")
        print(f"Waste descargado: {self.dump.total_dumped:.1f} tons")
        
        # Verificar camiones atascados
        stuck_trucks = [t for t in self.trucks if t.is_moving() and t.movement_timer > 100]
        if stuck_trucks:
            print(f"⚠️  Camiones posiblemente atascados: {[t.id for t in stuck_trucks]}")
                
    def get_statistics(self):
        """Obtiene estadísticas de la simulación"""
        return {
            'tick_count': self.tick_count,
            'mineral_processed': self.crusher.total_processed,
            'waste_dumped': self.dump.total_dumped,
            'trucks_moving': len([t for t in self.trucks if t.is_moving()]),
            'trucks_waiting': len([t for t in self.trucks if 'waiting' in t.task]),
            'average_queue_length': sum(len(s.queue) for s in self.shovels) / len(self.shovels)
        }