class Dump:
    def __init__(self, node, process_time=4):
        self.node = node
        self.queue = []
        self.current_truck = None
        self.timer = 0
        self.process_time = process_time

    def update(self):
        if not self.current_truck and self.queue:
            self.current_truck = self.queue.pop(0)
            self.timer = self.process_time

        if self.current_truck:
            self.timer -= 1
            if self.timer <= 0:
                self.current_truck.loading = False
                self.current_truck.task = "returning"
                self.current_truck = None

    def request_dump(self, truck):
        self.queue.append(truck)
