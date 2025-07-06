from core.mine_map import MineMap
from core.truck import Truck
from core.shovel import Shovel
from core.crusher import Crusher
from core.dump import Dump
import random

class Simulation:
    def __init__(self):
        self.map = MineMap()
        # Corregir los nombres de nodos para que coincidan con mine_map.py
        self.trucks = [
            Truck(i, 100, self.map.nodes["parking"]) for i in range(3)
        ]
        # Crear shovels en diferentes nodos de carga (c1, c2, c3, etc.)
        self.shovels = [
            Shovel(1, self.map.nodes["c1"]),
            Shovel(2, self.map.nodes["c2"]),
            Shovel(3, self.map.nodes["c3"])
        ]
        self.crusher = Crusher(self.map.nodes["crusher"])
        self.dump = Dump(self.map.nodes["dump_zone"])

    def update(self):
        # Actualizar shovels y descargadores
        for shovel in self.shovels:
            shovel.update()
        self.crusher.update()
        self.dump.update()

        for truck in self.trucks:
            if truck.task == "waiting_shovel":
                # Buscar el shovel más cercano o con menos cola
                best_shovel = min(self.shovels, key=lambda s: len(s.queue))
                if truck not in best_shovel.queue:
                    truck.move_to(best_shovel.node)
                    best_shovel.request_load(truck)

            elif truck.task == "driving":
                # Decidir aleatoriamente entre crusher y dump
                if truck.loading:  # Si está cargado
                    destination = random.choice([self.map.nodes["crusher"], self.map.nodes["dump_zone"]])
                    truck.move_to(destination)
                    truck.task = "waiting_dumping"

            elif truck.task == "waiting_dumping":
                if truck.position.name == "crusher":
                    if truck not in self.crusher.queue:
                        self.crusher.request_dump(truck)
                elif truck.position.name == "dump_zone":
                    if truck not in self.dump.queue:
                        self.dump.request_dump(truck)

            elif truck.task == "returning":
                truck.move_to(self.map.nodes["parking"])
                truck.task = "waiting_shovel"