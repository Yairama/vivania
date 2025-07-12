from core.simulation import Simulation
import time

def run():
    sim = Simulation()

    for _ in range(100):  # 100 simulation steps
        sim.update()
        time.sleep(0.1)  # Just to simulate time passing


