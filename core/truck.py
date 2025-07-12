# core/truck.py (Mejorado con velocidades por segmento)
import math
from config import FOLLOW_DISTANCE
from logger import get_logger

logger = get_logger(__name__)

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
        
        # Estado de movimiento - MEJORADO
        self.route = []  # Lista de nodos a seguir
        self.route_index = 0  # Índice actual en la ruta
        self.target_node_name = None
        self.movement_timer = 0  # Timer para simular movimiento
        self.current_segment = None  # Segmento actual
        
        # Estados del camión
        self.task = "waiting_assignment"
        self.wait_time = 0
        
        # Posición exacta para visualización
        self.x = position.x
        self.y = position.y
        self._last_progress = 0.0
        self.current_speed = 0.0
        
    def assign_route(self, route):
        """Asigna una nueva ruta al camión"""
        if len(route) > 1:
            self.route = route
            self.route_index = 0
            self.target_node_name = route[1] if len(route) > 1 else None
            self.current_segment = None
            self.movement_timer = 0
    
    def update_movement(self, mine_map, all_trucks=None, dt=1.0, follow_distance=FOLLOW_DISTANCE):
        """Actualiza el movimiento del camión usando velocidades de segmento y control de tráfico"""
        if not self.target_node_name or self.task in ["waiting_shovel", "loading", "waiting_dump", "dumping"]:
            return
            
        # Obtener el segmento actual si no lo tenemos
        if self.current_segment is None:
            self.current_segment = self._find_segment(mine_map)
            if self.current_segment:
                # Calcular tiempo de viaje basado en velocidad del segmento y eficiencia del camión
                base_travel_time = self.current_segment.get_travel_time(self.loading)
                # Aplicar eficiencia del camión (más eficiencia = más rápido)
                speed_factor = self.efficiency + 0.3  # Factor entre 0.3 y 1.3
                actual_travel_time = base_travel_time / speed_factor
                # Convertir a ticks (asumiendo 1 tick = 0.1 horas)
                self.movement_timer = int(actual_travel_time * 10)
                self._original_timer = self.movement_timer  # Guardar para cálculo de progreso
                logger.debug(
                    f"Camión {self.id}: Viajando por segmento, tiempo: {self.movement_timer} ticks"
                )
        
        # Decrementar timer de movimiento considerando tráfico
        if self.movement_timer > 0:
            progress_step = 1.0 / self._original_timer
            old_progress = 1.0 - (self.movement_timer / self._original_timer)

            if all_trucks and self.current_segment:
                my_progress = 1.0 - (self.movement_timer / self._original_timer)
                limit_progress = 1.0
                for other in all_trucks:
                    if other is self:
                        continue
                    if other.current_segment == self.current_segment:
                        other_progress = 1.0 - (other.movement_timer / other._original_timer) if other._original_timer else 1.0
                        if other_progress > my_progress:
                            allowed = other_progress - (follow_distance / self.current_segment.distance)
                            if allowed < limit_progress:
                                limit_progress = allowed
                if limit_progress < 1.0:
                    progress_step = min(progress_step, max(0.0, limit_progress - my_progress))

            self.movement_timer -= progress_step * self._original_timer
            new_progress = 1.0 - (self.movement_timer / self._original_timer)
            if self.current_segment:
                self.current_speed = ((new_progress - old_progress) * self.current_segment.distance) / 0.1
            self._last_progress = new_progress

            # Interpolar posición visual
            self._update_visual_position(mine_map)
        
        # Verificar si llegó al nodo objetivo
        if self.movement_timer <= 0:
            self._advance_to_next_node(mine_map)
            
    def _find_segment(self, mine_map):
        """Encuentra el segmento entre el nodo actual y el objetivo"""
        if not self.target_node_name:
            return None
            
        current_node = mine_map.nodes[self.route[self.route_index]]
        
        # Buscar el segmento que conecta con el nodo objetivo
        for segment in current_node.segments:
            if segment.destination.name == self.target_node_name:
                return segment
        return None
    
    def _update_visual_position(self, mine_map):
        """Actualiza la posición visual del camión"""
        if self.route_index < len(self.route) and self.current_segment:
            current_node = mine_map.nodes[self.route[self.route_index]]
            target_node = mine_map.nodes[self.target_node_name]
            
            # Calcular progreso basado en el timer original vs actual
            if hasattr(self, '_original_timer') and self._original_timer > 0:
                progress = 1.0 - (self.movement_timer / self._original_timer)
                progress = max(0.0, min(1.0, progress))
                
                # Interpolación lineal de posición
                self.x = current_node.x + (target_node.x - current_node.x) * progress
                self.y = current_node.y + (target_node.y - current_node.y) * progress
                
    def _advance_to_next_node(self, mine_map):
        """Avanza al siguiente nodo en la ruta"""
        if self.target_node_name:
            # Actualizar posición actual
            self.position = mine_map.nodes[self.target_node_name]
            self.x = self.position.x
            self.y = self.position.y
            self.route_index += 1
            self.current_segment = None  # Reset para el siguiente segmento
            self.current_speed = 0.0
            
            # Verificar si hay más nodos en la ruta
            if self.route_index < len(self.route) - 1:
                # Hay más nodos, continuar movimiento
                self.target_node_name = self.route[self.route_index + 1]
                self.movement_timer = 0  # Se calculará en el próximo update
            else:
                # Llegó al destino final
                self.target_node_name = None
                self.route = []
                self.route_index = 0
                self._arrived_at_destination()
                
    def _arrived_at_destination(self):
        """Maneja la llegada al destino"""
        self.current_speed = 0.0
        if self.task == "moving_to_shovel":
            self.task = "waiting_shovel"
            logger.debug(
                f"Camión {self.id} llegó a pala en {self.position.name}"
            )
        elif self.task == "moving_to_dump":
            self.task = "waiting_dump"
            logger.debug(
                f"Camión {self.id} llegó a punto de descarga en {self.position.name}"
            )
        elif self.task == "returning":
            self.task = "waiting_assignment"
            logger.debug(f"Camión {self.id} regresó a {self.position.name}")
            
    def start_loading(self, material_type, load_amount):
        """Inicia el proceso de carga"""
        self.task = "loading"
        self.material_type = material_type
        self.current_load = min(load_amount * self.efficiency, self.capacity)
        logger.info(
            f"Camión {self.id} cargando {self.current_load:.1f}t de {material_type}"
        )
        
    def finish_loading(self):
        """Finaliza el proceso de carga"""
        self.loading = True
        self.task = "waiting_assignment"
        logger.info(
            f"Camión {self.id} terminó de cargar, peso: {self.current_load:.1f}t"
        )
        
    def start_dumping(self):
        """Inicia el proceso de descarga"""
        self.task = "dumping"
        logger.info(
            f"Camión {self.id} descargando {self.current_load:.1f}t de {self.material_type}"
        )
        
    def finish_dumping(self):
        """Finaliza el proceso de descarga"""
        self.loading = False
        self.current_load = 0
        self.material_type = None
        self.task = "waiting_assignment"
        logger.info(f"Camión {self.id} terminó de descargar")
        
    def is_moving(self):
        """Verifica si el camión está en movimiento"""
        return self.task in ["moving_to_shovel", "moving_to_dump", "returning"]
        
    def is_available(self):
        """Verifica si el camión está disponible para asignación"""
        return self.task == "waiting_assignment"
        
    def get_current_speed(self):
        """Obtiene la velocidad actual del camión"""
        return self.current_speed
        
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
            'timer': self.movement_timer,
            'speed': self.get_current_speed(),
            'efficiency': self.efficiency
        }