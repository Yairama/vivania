# core/dijkstra.py
from copy import copy
import numpy as np
import heapq


class Dijkstra:
    def __init__(self, nodes_dict: dict):
        """Build an adjacency list from the provided ``nodes_dict``.

        ``nodes_dict`` should map node names to ``Node`` objects. In some rare
        situations the input may contain non-string keys (for example when
        loading malformed data).  To make the structure robust we coerce all
        keys and neighbour names to ``str`` so that they can safely be used as
        dictionary keys.
        """
        self.graph: dict[str, list[tuple[str, float]]] = {}

        for key, node in nodes_dict.items():
            key = str(key)
            connections: list[tuple[str, float]] = []
            for segment in node.segments:
                neighbor = str(segment.destination.name)
                distance = float(segment.distance)
                connections.append((neighbor, distance))
            self.graph[key] = connections

    def get_graph(self):
        return self.graph

    def naive_dijkstra(self, root):
        """Classic Dijkstra using a priority queue for stability."""
        graph = self.graph

        dist = {node: np.inf for node in graph.keys()}
        path = {node: [] for node in graph.keys()}
        visited = set()

        dist[root] = 0
        queue = [(0.0, root)]

        while queue:
            d, u = heapq.heappop(queue)
            if u in visited:
                continue
            visited.add(u)

            for v, l in graph[u]:
                new_d = d + l
                if new_d < dist[v]:
                    dist[v] = new_d
                    path[v] = path[u] + [v]
                    heapq.heappush(queue, (new_d, v))

        return dist, path

    def get_shortest_path(self, start, end):
        """Obtiene la ruta más corta entre dos nodos"""
        if start not in self.graph or end not in self.graph:
            return []
            
        dist, path = self.naive_dijkstra(start)
        
        if end not in path or dist[end] == np.inf:
            return []
            
        # Construir la ruta completa
        route = [start] + path[end]
        return route
