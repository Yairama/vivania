from core.simulation import Simulation
from core.visualizer import Visualizer
import pygame

def run():
    pygame.init()
    sim = Simulation()
    visualizer = Visualizer(sim)

    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        sim.update()
        visualizer.draw()

    pygame.quit()
