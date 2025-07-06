# core/truck.py (Corregido)
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
        
        # Estado de movimiento - SIMPLIFICADO
        self.route = []  # Lista de nodos a seguir
        self.route_index = 0  # Índice actual en la ruta
        self.target_node_name = None
        self.movement_timer = 0  # Timer para simular movimiento
        
        # Estados del camión
        self.task = "waiting_assignment"
        self.wait_time = 0
        
        # Posición exacta para visualización
        self.x = position.x
        self.y = position.y
        

        
    def assign_route(self, route):
        """Asigna una nueva ruta al camión"""
        if len(route) > 1:
            self.route = route
            self.route_index = 0
            self.target_node_name = route[1] if len(route) > 1 else None
            self.movement_timer = 30  # Tiempo fijo para llegar al siguiente nodo

    
    def update_movement(self, mine_map, dt=1.0):
        """Actualiza el movimiento del camión"""
        if not self.target_node_name or self.task in ["waiting_shovel", "loading", "waiting_dump", "dumping"]:
            return
            
        # Decrementar timer de movimiento
        self.movement_timer -= 1
        
        # Interpolar posición visual
        if self.movement_timer > 0 and self.route_index < len(self.route):
            current_node = mine_map.nodes[self.route[self.route_index]]
            target_node = mine_map.nodes[self.target_node_name]
            
            # Progreso del movimiento (0.0 a 1.0)
            progress = 1.0 - (self.movement_timer / 30.0)
            progress = max(0.0, min(1.0, progress))
            
            # Interpolación lineal de posición
            self.x = current_node.x + (target_node.x - current_node.x) * progress
            self.y = current_node.y + (target_node.y - current_node.y) * progress
        
        # Verificar si llegó al nodo objetivo
        if self.movement_timer <= 0:
            self._advance_to_next_node(mine_map)
                
    def _advance_to_next_node(self, mine_map):
        """Avanza al siguiente nodo en la ruta"""
        if self.target_node_name:
            # Actualizar posición actual
            self.position = mine_map.nodes[self.target_node_name]
            self.x = self.position.x
            self.y = self.position.y
            self.route_index += 1
            

            
            # Verificar si hay más nodos en la ruta
            if self.route_index < len(self.route) - 1:
                # Hay más nodos, continuar movimiento
                self.target_node_name = self.route[self.route_index + 1]
                self.movement_timer = 30  # Tiempo para el siguiente segmento

            else:
                # Llegó al destino final
                self.target_node_name = None
                self.route = []
                self.route_index = 0
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
        
    def get_status_info(self):
        """Obtiene información de estado para debug"""
        return {
            'id': self.id,
            'task': self.task,
            'position': self.position.name,
            'target': self.target_node_name,
            'loading': self.loading,
            'material': self.material_type,
            'load': self.current_load,
            'route': self.route,
            'timer': self.movement_timer
        }