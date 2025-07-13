# core/dijkstra.py (Versión defensiva simple)
import numpy as np
import heapq
from logger import get_logger

logger = get_logger(__name__)

class Dijkstra:
    def __init__(self, nodes_dict: dict):
        self.graph: dict[str, list[tuple[str, float]]] = {}
        
        for key, node in nodes_dict.items():
            key = str(key)
            connections: list[tuple[str, float]] = []
            
            for segment in node.segments:
                neighbor_name = str(segment.destination.name)
                distance = float(segment.distance)
                
                # VALIDACIÓN CRÍTICA: Asegurar orden correcto
                if isinstance(neighbor_name, str) and isinstance(distance, (int, float)):
                    connections.append((neighbor_name, distance))
                else:
                    logger.error(f"❌ Datos inválidos: neighbor='{neighbor_name}' distance='{distance}'")
                    
            self.graph[key] = connections

    def naive_dijkstra(self, root):
        """Dijkstra con validación defensiva en cada iteración."""
        if root not in self.graph:
            return {}, {}
            
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

            if u not in graph:
                continue

            for connection in graph[u]:
                # VALIDACIÓN DEFENSIVA CRÍTICA
                if not isinstance(connection, tuple) or len(connection) != 2:
                    logger.error(f"❌ Conexión malformada desde {u}: {connection}")
                    continue
                    
                v, l = connection
                
                # VALIDAR TIPOS EXPLÍCITAMENTE
                if not isinstance(v, str):
                    logger.error(f"❌ Neighbor no es string: {v} (tipo: {type(v)}) desde {u}")
                    continue
                    
                if not isinstance(l, (int, float)):
                    logger.error(f"❌ Distancia no es numérica: {l} (tipo: {type(l)}) entre {u} y {v}")
                    continue
                    
                # VALIDAR QUE EL VECINO EXISTE
                if v not in dist:
                    logger.error(f"❌ Vecino {v} no existe en dist desde {u}")
                    continue

                new_d = d + l
                if new_d < dist[v]:
                    dist[v] = new_d
                    path[v] = path[u] + [v]
                    heapq.heappush(queue, (new_d, v))

        return dist, path

    def get_shortest_path(self, start, end):
        """Ruta más corta con manejo de errores."""
        if start not in self.graph or end not in self.graph:
            return []
            
        try:
            dist, path = self.naive_dijkstra(start)
            
            if end not in path or dist[end] == np.inf:
                return []
                
            route = [start] + path[end]
            return route
            
        except Exception as e:
            logger.error(f"❌ Error en get_shortest_path({start}, {end}): {e}")
            return []

    def debug_graph_integrity(self):
        """Función de debug para verificar integridad del grafo"""
        logger.info("🔍 Verificando integridad del grafo...")
        
        for node, connections in self.graph.items():
            for i, connection in enumerate(connections):
                if not isinstance(connection, tuple) or len(connection) != 2:
                    logger.error(f"❌ Conexión malformada en {node}[{i}]: {connection}")
                    continue
                    
                neighbor, distance = connection
                if not isinstance(neighbor, str):
                    logger.error(f"❌ Neighbor inválido en {node}: {neighbor} (tipo: {type(neighbor)})")
                    
                if not isinstance(distance, (int, float)):
                    logger.error(f"❌ Distancia inválida en {node}->{neighbor}: {distance} (tipo: {type(distance)})")
                    
        logger.info(f"✅ Verificación completa. Nodos: {len(self.graph)}")