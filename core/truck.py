class Truck:
    def __init__(self, id, capacity, position):
        self.id = id
        self.capacity = capacity
        self.position = position
        self.loading = False  # False = vacío, True = cargado
        self.route = []
        self.task = "waiting_shovel"  # estados: waiting_shovel, driving, waiting_dumping, returning
        self.wait_time = 0
        self.progress = 0

    def move_to(self, node):
        """Simula el movimiento del camión a otro nodo"""
        self.position = node

    def assign_route(self, path):
        """Asigna una ruta al camión"""
        self.route = path

    def reset_for_new_cycle(self):
        """Reinicia el camión para un nuevo ciclo"""
        self.loading = False
        self.task = "waiting_shovel"
        self.wait_time = 0
        self.progress = 0