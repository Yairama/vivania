# core/dijkstra.py
from copy import copy
import numpy as np
import heapq


class Dijkstra:
    def __init__(self, nodes_dict: dict):
        self.graph = {}
        
        for key in nodes_dict.keys():
            connections_dict = []
            for segment in nodes_dict[key].segments:
                neighbor_name = segment.destination.name
                distance = segment.distance
                connections_dict.append((neighbor_name, distance))
            self.graph[key] = connections_dict

    def get_graph(self):
        return self.graph

    def naive_dijkstra(self, root):
        """Classic Dijkstra using a priority queue for stability."""
        graph = self.graph

        dist = {node: np.inf for node in graph}
        path = {node: [] for node in graph}
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
