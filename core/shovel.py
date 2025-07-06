class Shovel:
    def __init__(self, id, node, load_time=5):
        self.id = id
        self.node = node
        self.queue = []
        self.load_time = load_time
        self.current_truck = None
        self.timer = 0

    def update(self):
        if not self.current_truck and self.queue:
            self.current_truck = self.queue.pop(0)
            self.timer = self.load_time

        if self.current_truck:
            self.timer -= 1
            if self.timer <= 0:
                self.current_truck.loading = True  # Ahora está cargado
                self.current_truck.task = "driving"
                self.current_truck = None

    def request_load(self, truck):
        if truck not in self.queue:
            self.queue.append(truck)
            truck.task = "waiting_shovel"