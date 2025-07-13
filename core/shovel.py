# core/shovel.py (Mejorado)
import math
import random
class Shovel:
    def __init__(self, id, node, load_time=5, ton_per_pass=47, efficiency=0.91, material_type='waste'):
        """Create a new shovel.

        Parameters
        ----------
        load_time : int
            Time (in ticks) of a single loading pass. Total loading time will
            depend on the number of passes required for each truck.
        ton_per_pass : float
            Nominal tonnage moved in a single pass.
        """

        self.id = id
        self.node = node
        self.load_time = load_time
        self.ton_per_pass = ton_per_pass
        self.efficiency = efficiency
        self.material_type = material_type

        self.queue = []
        self.current_truck = None
        self.timer = 0
        self.passes_required = 0
        self.passes_done = 0
        self.total_hang_time = 0
        
    def update(self):
        """Process loading logic for the shovel."""
        if not self.current_truck and not self.queue:
            self.total_hang_time += 1

        if not self.current_truck and self.queue:
            # Start loading the next truck in queue
            self.current_truck = self.queue.pop(0)
            self.current_truck.start_loading(self.material_type)

            effective_per_pass = (
                self.ton_per_pass * self.efficiency * self.current_truck.efficiency
            )
            self.passes_required = max(
                1, int(math.ceil(self.current_truck.capacity / effective_per_pass))
            )
            self.passes_done = 0
            self.timer = self.load_time

        if self.current_truck:
            self.timer -= 1
            if self.timer <= 0:
                # Execute one loading pass with variability
                base = self.ton_per_pass * self.efficiency
                variation = base * random.uniform(-0.1, 0.1)
                tonnage = base + variation
                self.current_truck.add_load(tonnage)
                self.passes_done += 1

                if (
                    self.current_truck.current_load >= self.current_truck.capacity
                    or self.passes_done >= self.passes_required
                ):
                    self.current_truck.finish_loading()
                    self.current_truck = None
                else:
                    # Prepare next pass
                    self.timer = self.load_time
                
    def request_load(self, truck):
        if truck not in self.queue and truck.task == "waiting_shovel":
            self.queue.append(truck)
            
    def can_accept_truck(self):
        """Verifica si la pala puede aceptar más camiones"""
        return len(self.queue) < 3  # Máximo 3 camiones en cola

    def get_hang_time(self) -> int:
        """Return accumulated hang time of this shovel."""
        return self.total_hang_time

