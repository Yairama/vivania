class Node:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.segments = []

    def connect(self, segment):
        self.segments.append(segment)
