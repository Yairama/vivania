# core/visualizer.py (Mejorado con auto-escalado y ventana redimensionable)
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from logger import get_logger

logger = get_logger(__name__)

class Visualizer:
    def __init__(self, simulation):
        self.sim = simulation
        
        # Hacer la ventana redimensionable
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Open Pit Mining Simulation - Fleet Management")
        pygame.font.init()
        
        self.show_speed_info = False
        self.show_truck_paths = True
        
        # Calcular escalado automático del mapa
        self._calculate_map_bounds()
        self._update_scaling()
        
    def _calculate_map_bounds(self):
        """Calcula los límites del mapa para escalado automático"""
        if not self.sim.map.nodes:
            return
            
        xs = [node.x for node in self.sim.map.nodes.values()]
        ys = [node.y for node in self.sim.map.nodes.values()]
        
        self.map_min_x = min(xs)
        self.map_max_x = max(xs)
        self.map_min_y = min(ys)
        self.map_max_y = max(ys)
        
        self.map_width = self.map_max_x - self.map_min_x
        self.map_height = self.map_max_y - self.map_min_y
        
    def _update_scaling(self):
        """Actualiza el escalado basado en el tamaño de ventana actual"""
        current_width, current_height = self.screen.get_size()
        
        # Reservar espacio para paneles de información
        available_width = current_width - 320  # 320px para paneles laterales
        available_height = current_height - 200  # 200px para paneles superior e inferior
        
        # Calcular escalas para X e Y
        if self.map_width > 0 and self.map_height > 0:
            scale_x = available_width / self.map_width
            scale_y = available_height / self.map_height
            
            # Usar la escala menor para mantener proporciones
            self.scale = min(scale_x, scale_y) * 0.9  # 90% para margen
        else:
            self.scale = 1.0
            
        # Calcular offset para centrar el mapa
        scaled_width = self.map_width * self.scale
        scaled_height = self.map_height * self.scale
        
        self.offset_x = (current_width - scaled_width) / 2 - self.map_min_x * self.scale
        self.offset_y = (current_height - scaled_height) / 2 - self.map_min_y * self.scale
        
    def _transform_coords(self, x, y):
        """Transforma coordenadas del mapa a coordenadas de pantalla"""
        screen_x = x * self.scale + self.offset_x
        screen_y = y * self.scale + self.offset_y
        return int(screen_x), int(screen_y)
        
    def handle_resize(self, new_size):
        """Maneja el redimensionamiento de la ventana"""
        self.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
        self._update_scaling()

    def draw(self):
        current_width, current_height = self.screen.get_size()
        self.screen.fill((20, 25, 30))  # Fondo más oscuro y profesional
        
        # Fuentes adaptables al tamaño de ventana
        font_size = max(14, int(current_width / 60))
        small_font_size = max(12, int(current_width / 70))
        tiny_font_size = max(10, int(current_width / 80))
        
        font = pygame.font.SysFont(None, font_size)
        small_font = pygame.font.SysFont(None, small_font_size)
        tiny_font = pygame.font.SysFont(None, tiny_font_size)

        # Dibujar segmentos (rutas) con grosor adaptable
        line_width = max(1, int(self.scale / 10))
        for node in self.sim.map.nodes.values():
            for segment in node.segments:
                start = self._transform_coords(segment.origin.x, segment.origin.y)
                end = self._transform_coords(segment.destination.x, segment.destination.y)
                
                # Color basado en velocidad vacío
                if segment.empty_speed >= 30:
                    color = (0, 180, 50)  # Verde brillante para rutas rápidas
                elif segment.empty_speed >= 25:
                    color = (200, 180, 0)  # Amarillo para rutas medias
                else:
                    color = (180, 60, 60)  # Rojo para rutas lentas
                
                pygame.draw.line(self.screen, color, start, end, line_width)
                
                # Mostrar velocidad en el segmento si está activado
                if self.show_speed_info and self.scale > 0.5:
                    mid_x = (start[0] + end[0]) // 2
                    mid_y = (start[1] + end[1]) // 2
                    speed_text = f"{segment.empty_speed:.0f}/{segment.loaded_speed:.0f}"
                    text_surface = tiny_font.render(speed_text, True, (255, 255, 255))
                    text_rect = text_surface.get_rect(center=(mid_x, mid_y))
                    
                    # Fondo semi-transparente para legibilidad
                    bg_rect = text_rect.inflate(4, 2)
                    bg_surface = pygame.Surface(bg_rect.size)
                    bg_surface.set_alpha(128)
                    bg_surface.fill((0, 0, 0))
                    self.screen.blit(bg_surface, bg_rect)
                    self.screen.blit(text_surface, text_rect)

        # Dibujar nodos con tamaño adaptable
        node_radius = max(6, int(self.scale * 8))
        label_offset = node_radius + 2
        
        for name, node in self.sim.map.nodes.items():
            pos = self._transform_coords(node.x, node.y)
            
            # Color del nodo según tipo
            color = (255, 255, 255)  # blanco por defecto
            
            # Verificar si es un nodo de shovel
            shovel_nodes = [shovel.node for shovel in self.sim.shovels]
            if node in shovel_nodes:
                # Color según tipo de material de la pala
                shovel = next(s for s in self.sim.shovels if s.node == node)
                if shovel.material_type == 'mineral':
                    color = (255, 215, 0)  # Dorado para palas de mineral
                else:
                    color = (255, 140, 0)  # Naranja para palas de waste
            elif node == self.sim.crusher.node:
                color = (0, 255, 255)  # cyan para crusher
            elif node == self.sim.dump.node:
                color = (255, 100, 100)    # rojo claro para dump
            elif name == "parking":
                color = (100, 255, 100)    # verde claro para parking

            # Dibujar nodo con borde
            pygame.draw.circle(self.screen, color, pos, node_radius)
            pygame.draw.circle(self.screen, (255, 255, 255), pos, node_radius, 2)
            
            # Etiqueta del nodo (solo si hay espacio)
            if self.scale > 0.3:
                text = small_font.render(name, True, (220, 220, 220))
                text_rect = text.get_rect()
                text_rect.topleft = (pos[0] + label_offset, pos[1] - text_rect.height // 2)
                
                # Fondo semi-transparente para la etiqueta
                bg_rect = text_rect.inflate(4, 2)
                bg_surface = pygame.Surface(bg_rect.size)
                bg_surface.set_alpha(160)
                bg_surface.fill((40, 40, 40))
                self.screen.blit(bg_surface, bg_rect)
                self.screen.blit(text, text_rect)

        # Dibujar camiones con tamaño adaptable
        truck_size = max(8, int(self.scale * 12))
        
        for truck in self.sim.trucks:
            truck_pos = self._transform_coords(truck.x, truck.y)
            
            # Color según estado del camión
            if truck.task == "waiting_shovel":
                color = (255, 255, 100)  # amarillo brillante
            elif truck.task == "loading":
                color = (255, 180, 0)  # naranja
            elif truck.task in ["moving_to_shovel", "moving_to_dump", "returning"]:
                if truck.loading:
                    color = (100, 255, 100)  # verde brillante (cargado)
                else:
                    color = (100, 150, 255)  # azul claro (vacío)
            elif truck.task == "waiting_dump":
                color = (255, 100, 255)  # magenta
            elif truck.task == "dumping":
                color = (200, 100, 255)  # púrpura
            else:
                color = (150, 150, 150)  # gris
            
            # Dibujar camión como rectángulo redondeado
            truck_rect = pygame.Rect(truck_pos[0] - truck_size//2, truck_pos[1] - truck_size//2, 
                                   truck_size, truck_size)
            pygame.draw.rect(self.screen, color, truck_rect, border_radius=2)
            pygame.draw.rect(self.screen, (255, 255, 255), truck_rect, 2, border_radius=2)
            
            # ID del camión (solo si hay espacio)
            if self.scale > 0.4:
                truck_text = tiny_font.render(str(truck.id), True, (255, 255, 255))
                text_rect = truck_text.get_rect(center=(truck_pos[0], truck_pos[1] + truck_size + 8))
                self.screen.blit(truck_text, text_rect)
            
            # Mostrar velocidad actual si está en movimiento
            if truck.is_moving() and truck.get_current_speed() > 0 and self.scale > 0.5:
                speed_text = f"{truck.get_current_speed():.0f}"
                speed_surface = tiny_font.render(speed_text, True, (255, 255, 100))
                speed_rect = speed_surface.get_rect(center=(truck_pos[0], truck_pos[1] - truck_size - 8))
                self.screen.blit(speed_surface, speed_rect)
            
            # Mostrar ruta si está activa y habilitada
            if (self.show_truck_paths and truck.route and len(truck.route) > 1 and 
                truck.is_moving() and self.scale > 0.3):
                route_points = []
                for node_name in truck.route:
                    node = self.sim.map.nodes[node_name]
                    route_points.append(self._transform_coords(node.x, node.y))
                
                if len(route_points) > 1:
                    # Línea punteada para la ruta
                    self._draw_dashed_line(route_points, (150, 150, 255), 2)

        # Panel de información principal (adaptable)
        self._draw_info_panel(font, small_font, tiny_font)
        
        # Panel de camiones en movimiento
        self._draw_trucks_panel(small_font, tiny_font)
        
        # Leyenda de colores
        self._draw_legend(small_font, tiny_font)
        
        # Instrucciones y controles
        self._draw_controls(tiny_font)

        pygame.display.flip()
        
    def _draw_dashed_line(self, points, color, width):
        """Dibuja una línea punteada a través de múltiples puntos"""
        if len(points) < 2:
            return
            
        for i in range(len(points) - 1):
            start = points[i]
            end = points[i + 1]
            
            # Calcular la distancia y los segmentos
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            distance = (dx*dx + dy*dy)**0.5
            
            if distance > 0:
                dash_length = 8
                gap_length = 4
                total_length = dash_length + gap_length
                
                num_segments = int(distance / total_length)
                
                for j in range(num_segments):
                    t1 = j * total_length / distance
                    t2 = (j * total_length + dash_length) / distance
                    
                    if t2 > 1.0:
                        t2 = 1.0
                        
                    point1 = (start[0] + dx * t1, start[1] + dy * t1)
                    point2 = (start[0] + dx * t2, start[1] + dy * t2)
                    
                    pygame.draw.line(self.screen, color, point1, point2, width)
        
    def _draw_info_panel(self, font, small_font, tiny_font):
        """Dibuja el panel principal de información"""
        current_width, current_height = self.screen.get_size()
        panel_width = min(300, current_width // 3)
        
        info_bg = pygame.Rect(10, 10, panel_width, min(340, current_height - 20))
        pygame.draw.rect(self.screen, (40, 45, 50), info_bg)
        pygame.draw.rect(self.screen, (80, 90, 100), info_bg, 2)
        
        y_offset = 20
        
        # Título
        title_text = font.render("ESTADO DEL SISTEMA", True, (255, 255, 255))
        self.screen.blit(title_text, (20, y_offset))
        y_offset += 30
        
        # Información de shovels
        for i, shovel in enumerate(self.sim.shovels):
            queue_text = f"Pala {shovel.id} ({shovel.material_type[:3]}): {len(shovel.queue)}"
            if shovel.current_truck:
                queue_text += f" | T{shovel.current_truck.id}"
            
            color = (255, 215, 100) if shovel.material_type == 'mineral' else (255, 160, 100)
            text = small_font.render(queue_text, True, color)
            self.screen.blit(text, (20, y_offset + i * 18))
        
        y_offset += len(self.sim.shovels) * 18 + 15
        
        # Información de descarga
        crusher_text = f"Crusher: {len(self.sim.crusher.queue)}"
        if self.sim.crusher.current_truck:
            crusher_text += f" | T{self.sim.crusher.current_truck.id}"
        text = small_font.render(crusher_text, True, (100, 255, 255))
        self.screen.blit(text, (20, y_offset))
        
        dump_text = f"Dump: {len(self.sim.dump.queue)}"
        if self.sim.dump.current_truck:
            dump_text += f" | T{self.sim.dump.current_truck.id}"
        text = small_font.render(dump_text, True, (255, 120, 120))
        self.screen.blit(text, (20, y_offset + 18))
        
        # Estadísticas de producción
        y_offset += 45
        stats_text = f"Mineral: {self.sim.crusher.total_processed:.0f}t"
        text = small_font.render(stats_text, True, (150, 255, 150))
        self.screen.blit(text, (20, y_offset))
        
        waste_text = f"Desmonte: {self.sim.dump.total_dumped:.0f}t"
        text = small_font.render(waste_text, True, (255, 255, 150))
        self.screen.blit(text, (20, y_offset + 18))

        mineral_lost = f"Mineral a botadero: {self.sim.dump.total_mineral_dumped:.0f}t"
        text = small_font.render(mineral_lost, True, (255, 120, 120))
        self.screen.blit(text, (20, y_offset + 36))

        waste_wrong = f"Desmonte a chancadora: {self.sim.crusher.total_waste_dumped:.0f}t"
        text = small_font.render(waste_wrong, True, (255, 120, 120))
        self.screen.blit(text, (20, y_offset + 54))

        wrong_assign = f"Asig. erróneas: {self.sim.manager.wrong_assignment_count}"
        text = small_font.render(wrong_assign, True, (255, 100, 100))
        self.screen.blit(text, (20, y_offset + 72))

        # Ticks de simulación
        tick_text = f"Ticks: {self.sim.tick_count}"
        text = small_font.render(tick_text, True, (200, 200, 200))
        self.screen.blit(text, (20, y_offset + 90))

    def _draw_trucks_panel(self, small_font, tiny_font):
        """Dibuja el panel de camiones en movimiento"""
        current_width, current_height = self.screen.get_size()
        moving_trucks = [t for t in self.sim.trucks if t.is_moving()]
        
        if not moving_trucks:
            return
            
        panel_width = min(320, current_width // 3)
        panel_x = current_width - panel_width - 10
        panel_height = min(250, len(moving_trucks) * 22 + 40)
        
        truck_bg = pygame.Rect(panel_x, 10, panel_width, panel_height)
        pygame.draw.rect(self.screen, (45, 40, 60), truck_bg)
        pygame.draw.rect(self.screen, (90, 80, 120), truck_bg, 2)
        
        trucks_title = small_font.render("CAMIONES EN MOVIMIENTO:", True, (255, 255, 255))
        self.screen.blit(trucks_title, (panel_x + 10, 20))
        
        for i, truck in enumerate(moving_trucks[:10]):  # Máximo 10 camiones
            info = truck.get_status_info()
            
            # Línea 1: ID, velocidad y estado de carga
            truck_info = f"T{info['id']}: {info['speed']:.1f}km/h"
            if info['loading']:
                truck_info += f" ({info['load']:.0f}t {info['material'][:3]})"
            else:
                truck_info += " (vacío)"
                
            color = (100, 255, 100) if info['loading'] else (150, 150, 255)
            text = small_font.render(truck_info, True, color)
            self.screen.blit(text, (panel_x + 10, 40 + i * 22))

    def _draw_legend(self, small_font, tiny_font):
        """Dibuja la leyenda de colores"""
        current_width, current_height = self.screen.get_size()
        legend_width = min(280, current_width // 4)
        legend_height = 180
        legend_y = current_height - legend_height - 10
        
        legend_bg = pygame.Rect(10, legend_y, legend_width, legend_height)
        pygame.draw.rect(self.screen, (35, 35, 45), legend_bg)
        pygame.draw.rect(self.screen, (70, 70, 90), legend_bg, 1)
        
        # Leyenda de camiones
        legend_title = small_font.render("LEYENDA:", True, (255, 255, 255))
        self.screen.blit(legend_title, (20, legend_y + 10))
        
        legend_items = [
            ("Esperando pala", (255, 255, 100)),
            ("Cargando", (255, 180, 0)),
            ("Viajando cargado", (100, 255, 100)),
            ("Viajando vacío", (100, 150, 255)),
            ("Esperando descarga", (255, 100, 255)),
            ("Descargando", (200, 100, 255))
        ]
        
        for i, (text, color) in enumerate(legend_items):
            y = legend_y + 25 + i * 16
            pygame.draw.rect(self.screen, color, (20, y, 12, 12))
            legend_text = tiny_font.render(text, True, (200, 200, 200))
            self.screen.blit(legend_text, (35, y - 1))
            
        # Leyenda de rutas
        route_y = legend_y + 130
        route_items = [
            ("Rápidas (≥30)", (0, 180, 50)),
            ("Medias (25-30)", (200, 180, 0)),
            ("Lentas (<25)", (180, 60, 60))
        ]
        
        for i, (text, color) in enumerate(route_items):
            y = route_y + i * 14
            pygame.draw.line(self.screen, color, (20, y + 6), (32, y + 6), 3)
            legend_text = tiny_font.render(text, True, (200, 200, 200))
            self.screen.blit(legend_text, (35, y))

    def _draw_controls(self, tiny_font):
        """Dibuja los controles disponibles"""
        current_width, current_height = self.screen.get_size()
        controls = [
            "S: Velocidades en segmentos",
            "R: Rutas de camiones",
            "ESC: Salir"
        ]
        
        for i, control in enumerate(controls):
            text = tiny_font.render(control, True, (150, 150, 150))
            y_pos = current_height - (len(controls) - i) * 15 - 5
            self.screen.blit(text, (current_width - 200, y_pos))
        
    def handle_input(self, event):
        """Maneja entradas del usuario"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                self.show_speed_info = not self.show_speed_info
                logger.info(
                    f"Información de velocidades: {'ON' if self.show_speed_info else 'OFF'}"
                )
            elif event.key == pygame.K_r:
                self.show_truck_paths = not self.show_truck_paths
                logger.info(
                    f"Rutas de camiones: {'ON' if self.show_truck_paths else 'OFF'}"
                )
        elif event.type == pygame.VIDEORESIZE:
            self.handle_resize(event.size)