import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE

class Visualizer:
    def __init__(self, simulation):
        self.sim = simulation
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Open Pit Mining Simulation")

    def draw(self):
        self.screen.fill((30, 30, 30))
        font = pygame.font.SysFont(None, 20)

        # Dibujar segmentos (conexiones)
        for node in self.sim.map.nodes.values():
            for segment in node.segments:
                start = (segment.origin.x, segment.origin.y)
                end = (segment.destination.x, segment.destination.y)
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

            pygame.draw.circle(self.screen, color, (node.x, node.y), 10)
            text = font.render(name, True, (200, 200, 200))
            self.screen.blit(text, (node.x + 5, node.y - 20))

        # Dibujar información de colas
        y_offset = 10
        for i, shovel in enumerate(self.sim.shovels):
            queue_text = f"Shovel {shovel.id}: {len(shovel.queue)} en cola"
            text = font.render(queue_text, True, (255, 255, 255))
            self.screen.blit(text, (10, y_offset + i * 25))
        
        crusher_text = f"Crusher: {len(self.sim.crusher.queue)} en cola"
        text = font.render(crusher_text, True, (255, 255, 255))
        self.screen.blit(text, (10, y_offset + len(self.sim.shovels) * 25))
        
        dump_text = f"Dump: {len(self.sim.dump.queue)} en cola"
        text = font.render(dump_text, True, (255, 255, 255))
        self.screen.blit(text, (10, y_offset + (len(self.sim.shovels) + 1) * 25))

        # Dibujar camiones
        for truck in self.sim.trucks:
            if truck.task == "waiting_shovel":
                color = (200, 200, 0)
            elif truck.task == "driving":
                color = (0, 255, 0)
            elif truck.task == "waiting_dumping":
                color = (255, 0, 255)
            elif truck.task == "returning":
                color = (0, 0, 255)
            else:
                color = (100, 100, 100)
            
            pygame.draw.rect(self.screen, color, pygame.Rect(truck.position.x - 5, truck.position.y - 5, 10, 10))
            
            # Mostrar ID del camión
            truck_text = font.render(str(truck.id), True, (255, 255, 255))
            self.screen.blit(truck_text, (truck.position.x + 8, truck.position.y - 8))

        pygame.display.flip()