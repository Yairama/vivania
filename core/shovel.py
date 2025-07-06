# core/shovel.py (Mejorado)
class Shovel:
    def __init__(self, id, node, load_time=5, ton_per_pass=47, efficiency=0.91, material_type='waste'):
        self.id = id
        self.node = node
        self.load_time = load_time
        self.ton_per_pass = ton_per_pass
        self.efficiency = efficiency
        self.material_type = material_type
        
        self.queue = []
        self.current_truck = None
        self.timer = 0
        
    def update(self):
        if not self.current_truck and self.queue:
            self.current_truck = self.queue.pop(0)
            self.current_truck.start_loading(self.material_type, self.ton_per_pass)
            self.timer = self.load_time
            
        if self.current_truck:
            self.timer -= 1
            if self.timer <= 0:
                self.current_truck.finish_loading()
                self.current_truck = None
                
    def request_load(self, truck):
        if truck not in self.queue and truck.task == "waiting_shovel":
            self.queue.append(truck)
            
    def can_accept_truck(self):
        """Verifica si la pala puede aceptar más camiones"""
        return len(self.queue) < 3  # Máximo 3 camiones en cola

