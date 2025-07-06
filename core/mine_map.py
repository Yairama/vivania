import random
from core.node import Node
from core.segment import Segment

class MineMap:
    def __init__(self):
        self.nodes = {}
        self._create_map()

    def _create_map(self):
        def connect(n1, n2):
            if (n1.name, n2.name) not in [(s.origin.name, s.destination.name) for s in n1.segments]:
                Segment(n1, n2, random.uniform(24., 30.))

        nodes = {
            'parking': Node('parking', 91, 926),
            'n1': Node('n1', 223, 993),
            'crusher': Node('crusher', 314, 936),
            'n2': Node('n2', 100, 823),
            'n3': Node('n3', 180, 682),
            'n4': Node('n4', 201, 457),
            'n5': Node('n5', 320, 302),
            'c1': Node('c1', 548, 293),
            'dump_zone': Node('dump_zone', 81, 256),
            'n6': Node('n6', 521, 319),
            'n7': Node('n7', 569, 417),
            'n8': Node('n8', 593, 600),
            'c2': Node('c2', 612, 751),
            'n9': Node('n9', 446, 804),
            'c3': Node('c3', 331, 846),
            'n10': Node('n10', 323, 801),
            'n11': Node('n11', 280, 689),
            'n12': Node('n12', 286, 537),
            'n13': Node('n13', 305, 404),
            'c4': Node('c4', 426, 377),
            'n14': Node('n14', 354, 440),
            'n15': Node('n15', 472, 473),
            'n16': Node('n16', 485, 549),
            'c5': Node('c5', 413, 727),
            'c6': Node('c6', 359, 618)
        }

        connections = [
            ('parking', 'n2'), ('n1', 'n2'), ('crusher', 'n1'),
            ('n2', 'n3'), ('n3', 'n4'), ('n4', 'n5'),
            ('n5', 'dump_zone'), ('n5', 'c1'), ('n5', 'n6'),
            ('n6', 'n7'), ('n7', 'n8'), ('n8', 'n9'), ('n8', 'c2'),
            ('n9', 'c3'), ('n9', 'n10'), ('n10', 'n11'),
            ('n11', 'n12'), ('n12', 'n13'), ('n12', 'n14'),
            ('n13', 'c4'), ('n14', 'n15'), ('n15', 'n16'),
            ('n16', 'c5'), ('n16', 'c6')
        ]

        for n1, n2 in connections:
            connect(nodes[n1], nodes[n2])
            connect(nodes[n2], nodes[n1])  # bidireccional

        self.nodes = nodes
