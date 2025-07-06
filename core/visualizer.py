# core/visualizer.py (Mejorado con información de velocidades)
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE

class Visualizer:
    def __init__(self, simulation):
        self.sim = simulation
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Open Pit Mining Simulation")
        pygame.font.init()
        self.show_speed_info = False  # Toggle para mostrar info de velocidades

    def draw(self):
        self.screen.fill((30, 30, 30))
        font = pygame.font.SysFont(None, 18)
        small_font = pygame.font.SysFont(None, 14)
        tiny_font = pygame.font.SysFont(None, 12)

        # Dibujar segmentos con colores según velocidad
        for node in self.sim.map.nodes.values():
            for segment in node.segments:
                start = (int(segment.origin.x), int(segment.origin.y))
                end = (int(segment.destination.x), int(segment.destination.y))
                
                # Color basado en velocidad vacío
                if segment.empty_speed >= 30:
                    color = (0, 150, 0)  # Verde para rutas rápidas
                elif segment.empty_speed >= 25:
                    color = (150, 150, 0)  # Amarillo para rutas medias
                else:
                    color = (150, 0, 0)  # Rojo para rutas lentas
                
                pygame.draw.line(self.screen, color, start, end, 2)
                
                # Mostrar velocidad en el segmento si está activado
                if self.show_speed_info:
                    mid_x = (start[0] + end[0]) // 2
                    mid_y = (start[1] + end[1]) // 2
                    speed_text = f"{segment.empty_speed:.0f}/{segment.loaded_speed:.0f}"
                    text_surface = tiny_font.render(speed_text, True, (255, 255, 255))
                    self.screen.blit(text_surface, (mid_x, mid_y))

        # Dibujar nodos
        for name, node in self.sim.map.nodes.items():
            color = (255, 255, 255)  # por defecto
            
            # Verificar si es un nodo de shovel
            shovel_nodes = [shovel.node for shovel in self.sim.shovels]
            if node in shovel_nodes:
                color = (255, 165, 0)  # naranja para shovels
            elif node == self.sim.crusher.node:
                color = (0, 255, 255)  # cyan para crusher
            elif node == self.sim.dump.node:
                color = (255, 0, 0)    # rojo para dump
            elif name == "parking":
                color = (0, 255, 0)    # verde para parking

            pygame.draw.circle(self.screen, color, (int(node.x), int(node.y)), 8)
            text = small_font.render(name, True, (200, 200, 200))
            self.screen.blit(text, (node.x + 10, node.y - 15))

        # Panel principal de información (izquierda)
        y_offset = 10
        info_bg = pygame.Rect(5, 5, 280, 250)
        pygame.draw.rect(self.screen, (50, 50, 50), info_bg)
        pygame.draw.rect(self.screen, (100, 100, 100), info_bg, 2)
        
        # Título
        title_text = font.render("ESTADO DEL SISTEMA", True, (255, 255, 255))
        self.screen.blit(title_text, (10, y_offset))
        y_offset += 25
        
        # Información de shovels
        for i, shovel in enumerate(self.sim.shovels):
            queue_text = f"Pala {shovel.id} ({shovel.material_type}): {len(shovel.queue)} cola"
            if shovel.current_truck:
                queue_text += f" | Cargando: T{shovel.current_truck.id}"
            text = small_font.render(queue_text, True, (255, 200, 100))
            self.screen.blit(text, (10, y_offset + i * 15))
        
        y_offset += len(self.sim.shovels) * 15 + 10
        
        # Información de descarga
        crusher_text = f"Crusher: {len(self.sim.crusher.queue)} cola"
        if self.sim.crusher.current_truck:
            crusher_text += f" | Proc: T{self.sim.crusher.current_truck.id}"
        text = small_font.render(crusher_text, True, (0, 255, 255))
        self.screen.blit(text, (10, y_offset))
        
        dump_text = f"Dump: {len(self.sim.dump.queue)} cola"
        if self.sim.dump.current_truck:
            dump_text += f" | Desc: T{self.sim.dump.current_truck.id}"
        text = small_font.render(dump_text, True, (255, 100, 100))
        self.screen.blit(text, (10, y_offset + 15))
        
        # Estadísticas
        y_offset += 40
        stats_text = f"Mineral: {self.sim.crusher.total_processed:.0f}t"
        text = small_font.render(stats_text, True, (100, 255, 100))
        self.screen.blit(text, (10, y_offset))
        
        waste_text = f"Waste: {self.sim.dump.total_dumped:.0f}t"
        text = small_font.render(waste_text, True, (255, 255, 100))
        self.screen.blit(text, (10, y_offset + 15))
        
        # Información de velocidades promedio
        y_offset += 35
        speed_title = small_font.render("VELOCIDADES ACTIVAS:", True, (200, 200, 255))
        self.screen.blit(speed_title, (10, y_offset))
        
        moving_trucks = [t for t in self.sim.trucks if t.is_moving()]
        if moving_trucks:
            avg_speed = sum(t.get_current_speed() for t in moving_trucks) / len(moving_trucks)
            speed_text = f"Promedio: {avg_speed:.1f} km/h"
            text = small_font.render(speed_text, True, (200, 255, 200))
            self.screen.blit(text, (10, y_offset + 15))

        # Panel de camiones en movimiento (derecha)
        if moving_trucks:
            panel_x = SCREEN_WIDTH - 300
            truck_bg = pygame.Rect(panel_x, 5, 295, min(200, len(moving_trucks) * 20 + 30))
            pygame.draw.rect(self.screen, (40, 40, 60), truck_bg)
            pygame.draw.rect(self.screen, (80, 80, 120), truck_bg, 2)
            
            trucks_title = small_font.render("CAMIONES EN MOVIMIENTO:", True, (255, 255, 255))
            self.screen.blit(trucks_title, (panel_x + 5, 10))
            
            for i, truck in enumerate(moving_trucks[:8]):  # Máximo 8 camiones
                info = truck.get_status_info()
                truck_info = f"T{info['id']}: {info['speed']:.1f}km/h"
                if info['loading']:
                    truck_info += f" ({info['load']:.0f}t {info['material']})"
                else:
                    truck_info += " (vacío)"
                    
                color = (0, 255, 0) if info['loading'] else (150, 150, 255)
                text = small_font.render(truck_info, True, color)
                self.screen.blit(text, (panel_x + 5, 30 + i * 20))

        # Dibujar camiones
        for truck in self.sim.trucks:
            # Color según estado
            if truck.task == "waiting_shovel":
                color = (255, 255, 0)  # amarillo
            elif truck.task == "loading":
                color = (255, 150, 0)  # naranja
            elif truck.task in ["moving_to_shovel", "moving_to_dump", "returning"]:
                if truck.loading:
                    color = (0, 255, 0)  # verde (cargado)
                else:
                    color = (0, 150, 255)  # azul claro (vacío)
            elif truck.task == "waiting_dump":
                color = (255, 0, 255)  # magenta
            elif truck.task == "dumping":
                color = (150, 0, 255)  # púrpura
            else:
                color = (150, 150, 150)  # gris
            
            # Dibujar camión
            truck_rect = pygame.Rect(int(truck.x - 6), int(truck.y - 6), 12, 12)
            pygame.draw.rect(self.screen, color, truck_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), truck_rect, 1)
            
            # Mostrar ID del camión
            truck_text = small_font.render(str(truck.id), True, (255, 255, 255))
            self.screen.blit(truck_text, (truck.x + 8, truck.y - 8))
            
            # Mostrar velocidad actual si está en movimiento
            if truck.is_moving() and truck.get_current_speed() > 0:
                speed_text = f"{truck.get_current_speed():.0f}"
                speed_surface = tiny_font.render(speed_text, True, (255, 255, 0))
                self.screen.blit(speed_surface, (truck.x - 10, truck.y + 10))
            
            # Mostrar ruta si está en movimiento
            if truck.route and len(truck.route) > 1:
                route_points = []
                for node_name in truck.route:
                    node = self.sim.map.nodes[node_name]
                    route_points.append((int(node.x), int(node.y)))
                
                if len(route_points) > 1:
                    pygame.draw.lines(self.screen, (100, 100, 255), False, route_points, 1)

        # Leyenda de colores y velocidades
        legend_y = SCREEN_HEIGHT - 150
        legend_bg = pygame.Rect(5, legend_y - 5, 250, 150)
        pygame.draw.rect(self.screen, (40, 40, 40), legend_bg)
        pygame.draw.rect(self.screen, (80, 80, 80), legend_bg, 1)
        
        # Leyenda de camiones
        legend_title = small_font.render("LEYENDA CAMIONES:", True, (255, 255, 255))
        self.screen.blit(legend_title, (10, legend_y))
        
        legend_items = [
            ("Esperando pala", (255, 255, 0)),
            ("Cargando", (255, 150, 0)),
            ("Viajando cargado", (0, 255, 0)),
            ("Viajando vacío", (0, 150, 255)),
            ("Esperando descarga", (255, 0, 255)),
            ("Descargando", (150, 0, 255))
        ]
        
        for i, (text, color) in enumerate(legend_items):
            y = legend_y + 15 + i * 15
            pygame.draw.rect(self.screen, color, (10, y, 10, 10))
            legend_text = small_font.render(text, True, (200, 200, 200))
            self.screen.blit(legend_text, (25, y - 2))
            
        # Leyenda de rutas (velocidades)
        route_legend_y = legend_y + 100
        route_title = small_font.render("RUTAS POR VELOCIDAD:", True, (255, 255, 255))
        self.screen.blit(route_title, (10, route_legend_y))
        
        route_items = [
            ("Rápidas (≥30 km/h)", (0, 150, 0)),
            ("Medias (25-30 km/h)", (150, 150, 0)),
            ("Lentas (<25 km/h)", (150, 0, 0))
        ]
        
        for i, (text, color) in enumerate(route_items):
            y = route_legend_y + 15 + i * 12
            pygame.draw.line(self.screen, color, (10, y + 5), (20, y + 5), 3)
            legend_text = tiny_font.render(text, True, (200, 200, 200))
            self.screen.blit(legend_text, (25, y))

        # Instrucciones
        instructions_y = SCREEN_HEIGHT - 20
        instructions = tiny_font.render("Presiona 'S' para mostrar/ocultar velocidades en segmentos", True, (150, 150, 150))
        self.screen.blit(instructions, (10, instructions_y))

        pygame.display.flip()
        
    def handle_input(self, event):
        """Maneja entradas del usuario"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                self.show_speed_info = not self.show_speed_info
                print(f"Información de velocidades: {'ON' if self.show_speed_info else 'OFF'}")