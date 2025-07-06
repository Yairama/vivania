class Segment:
    def __init__(self, origin, destination, distance):
        self.origin = origin
        self.destination = destination
        self.distance = distance
        origin.connect(self)
