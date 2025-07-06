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
                    
                self.current_truck.finish_dumping()
                self.current_truck = None
                
    def request_dump(self, truck):
        if truck not in self.queue and truck.task == "waiting_dump":
            self.queue.append(truck)
            
    def can_accept_truck(self):
        """Verifica si el crusher puede aceptar más camiones"""
        return len(self.queue) < 2