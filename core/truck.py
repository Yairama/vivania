# core/truck.py (Completamente rediseñado)
import math

class Truck:
    def __init__(self, id, capacity, position, efficiency=0.85):
        self.id = id
        self.capacity = capacity
        self.position = position
        self.efficiency = efficiency
        
        # Estado de carga
        self.loading = False  # True = cargado, False = vacío
        self.current_load = 0
        self.material_type = None  # 'mineral', 'waste', None
        
        # Estado de movimiento
        self.route = []  # Lista de nodos a seguir
        self.current_route_index = 0
        self.target_node = None
        self.progress = 0.0  # Progreso en el segmento actual (0.0 a 1.0)
        self.speed = 0.0  # Velocidad actual
        
        # Estados del camión
        self.task = "waiting_assignment"  # waiting_assignment, moving_to_shovel, waiting_shovel, loading, moving_to_dump, waiting_dump, dumping, returning
        self.wait_time = 0
        
        # Posición exacta para visualización
        self.x = position.x
        self.y = position.y
        
    def assign_route(self, route):
        """Asigna una nueva ruta al camión"""
        if len(route) > 1:
            self.route = route
            self.current_route_index = 0
            self.target_node = None
            self.progress = 0.0
            self._set_next_target()
    
    def _set_next_target(self):
        """Establece el siguiente nodo objetivo en la ruta"""
        if self.current_route_index < len(self.route) - 1:
            self.target_node = self.route[self.current_route_index + 1]
            self.current_route_index += 1
        else:
            self.target_node = None
            
    def update_movement(self, mine_map, dt=1.0):
        """Actualiza el movimiento del camión"""
        if not self.target_node or self.task in ["waiting_shovel", "loading", "waiting_dump", "dumping"]:
            return
            
        current_node = self.route[self.current_route_index - 1] if self.current_route_index > 0 else self.position
        
        # Encontrar el segmento actual
        current_segment = None
        for segment in mine_map.nodes[current_node.name if hasattr(current_node, 'name') else current_node].segments:
            if segment.destination.name == self.target_node:
                current_segment = segment
                break
                
        if not current_segment:
            return
            
        # Calcular velocidad y movimiento
        self.speed = current_segment.get_speed(self.loading)
        movement_distance = self.speed * dt / 3600  # Convertir a unidades de distancia por tick
        
        # Actualizar progreso
        self.progress += movement_distance / current_segment.distance
        
        # Actualizar posición visual
        start_node = current_segment.origin
        end_node = current_segment.destination
        
        self.x = start_node.x + (end_node.x - start_node.x) * self.progress
        self.y = start_node.y + (end_node.y - start_node.y) * self.progress
        
        # Verificar si llegó al nodo objetivo
        if self.progress >= 1.0:
            self.progress = 0.0
            self.position = mine_map.nodes[self.target_node]
            self.x = self.position.x
            self.y = self.position.y
            
            # Configurar siguiente objetivo
            if self.current_route_index < len(self.route) - 1:
                self._set_next_target()
            else:
                # Llegó al destino
                self.target_node = None
                self.route = []
                self._arrived_at_destination()
                
    def _arrived_at_destination(self):
        """Maneja la llegada al destino"""
        if self.task == "moving_to_shovel":
            self.task = "waiting_shovel"
        elif self.task == "moving_to_dump":
            self.task = "waiting_dump"
        elif self.task == "returning":
            self.task = "waiting_assignment"
            
    def start_loading(self, material_type, load_amount):
        """Inicia el proceso de carga"""
        self.task = "loading"
        self.material_type = material_type
        self.current_load = min(load_amount * self.efficiency, self.capacity)
        
    def finish_loading(self):
        """Finaliza el proceso de carga"""
        self.loading = True
        self.task = "waiting_assignment"
        
    def start_dumping(self):
        """Inicia el proceso de descarga"""
        self.task = "dumping"
        
    def finish_dumping(self):
        """Finaliza el proceso de descarga"""
        self.loading = False
        self.current_load = 0
        self.material_type = None
        self.task = "waiting_assignment"
        
    def is_moving(self):
        """Verifica si el camión está en movimiento"""
        return self.task in ["moving_to_shovel", "moving_to_dump", "returning"]
        
    def is_available(self):
        """Verifica si el camión está disponible para asignación"""
        return self.task == "waiting_assignment"

