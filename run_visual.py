# run_visual.py (Actualizado)
from core.simulation import Simulation
from core.visualizer import Visualizer
import pygame

def run():
    pygame.init()
    sim = Simulation()
    visualizer = Visualizer(sim)

    clock = pygame.time.Clock()
    running = True

    print("\n=== CONTROLES ===")
    print("S - Mostrar/ocultar velocidades en segmentos")
    print("ESC - Salir")

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    visualizer.handle_input(event)

        sim.update()
        visualizer.draw()

    pygame.quit()

