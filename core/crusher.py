# core/crusher.py (Mejorado)
class Crusher:
    def __init__(self, node, process_time=4, throughput=200):
        self.node = node
        self.process_time = process_time
        self.throughput = throughput
        
        self.queue = []
        self.current_truck = None
        self.timer = 0
        self.total_processed = 0
        # Track waste incorrectly dumped here
        self.total_waste_dumped = 0
        
    def update(self):
        if not self.current_truck and self.queue:
            self.current_truck = self.queue.pop(0)
            self.current_truck.start_dumping()
            self.timer = self.process_time
            
        if self.current_truck:
            self.timer -= 1
            if self.timer <= 0:
                # Procesar material
                if self.current_truck.material_type == 'mineral':
                    self.total_processed += self.current_truck.current_load
                else:
                    self.total_waste_dumped += self.current_truck.current_load

                self.current_truck.finish_dumping()
                self.current_truck = None
                
    def request_dump(self, truck):
        """Encola el camión para descarga sin restricciones."""
        self.queue.append(truck)
