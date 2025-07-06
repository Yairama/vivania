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
        graph = self.graph
        n = len(graph)
        
        keys = list(graph.keys())
        dist = {}
        visited = {}
        path = {}
        
        for key in keys:
            dist[key] = np.inf
            visited[key] = False
            path[key] = []
            
        dist[root] = 0
        
        for _ in range(n):
            u = -1
            for i in range(n):
                if not visited[keys[i]] and (u == -1 or dist[keys[i]] < dist[keys[u]]):
                    u = i
                    
            if dist[keys[u]] == np.inf:
                break
                
            visited[keys[u]] = True
            
            for v, l in graph[keys[u]]:
                if dist[keys[u]] + l < dist[v]:
                    dist[v] = dist[keys[u]] + l
                    t_path = copy(path[keys[u]])
                    t_path.append(v)
                    path[v] = t_path
                    
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
