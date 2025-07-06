import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE

class Visualizer:
    def __init__(self, simulation):
        self.sim = simulation
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Open Pit Mining Simulation")
        pygame.font.init()

    def draw(self):
        self.screen.fill((30, 30, 30))
        font = pygame.font.SysFont(None, 18)
        small_font = pygame.font.SysFont(None, 14)

        # Dibujar segmentos (conexiones)
        for node in self.sim.map.nodes.values():
            for segment in node.segments:
                start = (int(segment.origin.x), int(segment.origin.y))
                end = (int(segment.destination.x), int(segment.destination.y))
                pygame.draw.line(self.screen, (70, 70, 70), start, end, 2)

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

        # Dibujar información de colas en panel izquierdo
        y_offset = 10
        info_bg = pygame.Rect(5, 5, 250, 200)
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
            
            # Mostrar ruta si está en movimiento
            if truck.route and len(truck.route) > 1:
                route_points = []
                for node_name in truck.route:
                    node = self.sim.map.nodes[node_name]
                    route_points.append((int(node.x), int(node.y)))
                
                if len(route_points) > 1:
                    pygame.draw.lines(self.screen, (100, 100, 255), False, route_points, 1)

        # Leyenda de colores
        legend_y = SCREEN_HEIGHT - 120
        legend_bg = pygame.Rect(5, legend_y - 5, 200, 120)
        pygame.draw.rect(self.screen, (40, 40, 40), legend_bg)
        pygame.draw.rect(self.screen, (80, 80, 80), legend_bg, 1)
        
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

        pygame.display.flip()