# core/mine_map.py (Mejorado con velocidades variables)
import random
from core.node import Node
from core.segment import Segment
from logger import get_logger

logger = get_logger(__name__)

class MineMap:
    def __init__(self):
        self.nodes = {}
        self._create_map()

    def _create_map(self):
        def connect(n1, n2, empty_speed=None, loaded_speed=None):
            """Conecta dos nodos con velocidades específicas"""
            if (n1.name, n2.name) not in [(s.origin.name, s.destination.name) for s in n1.segments]:
                # Calcular distancia euclidiana
                distance = ((n2.x - n1.x)**2 + (n2.y - n1.y)**2)**0.5
                
                # Asignar velocidades basadas en el tipo de ruta si no se especifican
                if empty_speed is None or loaded_speed is None:
                    empty_speed, loaded_speed = self._get_route_speeds(n1.name, n2.name, distance)
                
                Segment(n1, n2, distance, empty_speed, loaded_speed)

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

        # Conexiones con velocidades específicas por tipo de ruta
        connections = [
            # Rutas principales (más rápidas)
            ('parking', 'n2', 35, 20),
            ('n1', 'n2', 40, 25),
            ('crusher', 'n1', 30, 18),
            
            # Rutas secundarias (velocidad media)
            ('n2', 'n3', 28, 16),
            ('n3', 'n4', 25, 15),
            ('n4', 'n5', 30, 18),
            ('n5', 'dump_zone', 35, 20),
            
            # Rutas de acceso a palas (más lentas por maniobras)
            ('n5', 'c1', 20, 12),
            ('n8', 'c2', 18, 10),
            ('n9', 'c3', 22, 13),
            ('n13', 'c4', 20, 12),
            ('n16', 'c5', 18, 11),
            ('n16', 'c6', 19, 11),
            
            # Rutas internas (velocidad variable)
            ('n5', 'n6', 32, 19),
            ('n6', 'n7', 28, 17),
            ('n7', 'n8', 26, 15),
            ('n8', 'n9', 30, 18),
            ('n9', 'n10', 24, 14),
            ('n10', 'n11', 27, 16),
            ('n11', 'n12', 29, 17),
            ('n12', 'n13', 31, 18),
            ('n12', 'n14', 25, 15),
            ('n14', 'n15', 28, 16),
            ('n15', 'n16', 26, 15),
        ]

        # Crear conexiones bidireccionales
        for connection in connections:
            if len(connection) == 3:
                n1_name, n2_name, speed = connection
                empty_speed = speed
                loaded_speed = int(speed * 0.6)  # Cargado es 60% de la velocidad vacío
            elif len(connection) == 4:
                n1_name, n2_name, empty_speed, loaded_speed = connection
            else:
                n1_name, n2_name = connection
                empty_speed, loaded_speed = None, None
                
            connect(nodes[n1_name], nodes[n2_name], empty_speed, loaded_speed)
            connect(nodes[n2_name], nodes[n1_name], empty_speed, loaded_speed)

        self.nodes = nodes
        
        # Imprimir información de velocidades para debug
        self._print_speed_info()

    def _get_route_speeds(self, node1_name, node2_name, distance):
        """Determina velocidades basadas en el tipo de ruta"""
        
        # Rutas hacia/desde palas (más lentas)
        if any(name.startswith('c') for name in [node1_name, node2_name]):
            empty_speed = random.uniform(18, 25)
            loaded_speed = random.uniform(10, 15)
        
        # Rutas principales (parking, crusher, dump_zone)
        elif any(name in ['parking', 'crusher', 'dump_zone'] for name in [node1_name, node2_name]):
            empty_speed = random.uniform(30, 40)
            loaded_speed = random.uniform(18, 25)
        
        # Rutas internas (velocidad media)
        else:
            empty_speed = random.uniform(25, 35)
            loaded_speed = random.uniform(15, 20)
            
        return empty_speed, loaded_speed

    def _print_speed_info(self):
        """Imprime información de velocidades para debug"""
        logger.info("\n=== INFORMACIÓN DE VELOCIDADES ===")
        
        # Categorizar segmentos por velocidad
        fast_segments = []
        medium_segments = []
        slow_segments = []
        
        for node in self.nodes.values():
            for segment in node.segments:
                speed_info = {
                    'route': f"{segment.origin.name} -> {segment.destination.name}",
                    'empty_speed': segment.empty_speed,
                    'loaded_speed': segment.loaded_speed,
                    'distance': segment.distance
                }
                
                if segment.empty_speed >= 30:
                    fast_segments.append(speed_info)
                elif segment.empty_speed >= 25:
                    medium_segments.append(speed_info)
                else:
                    slow_segments.append(speed_info)
        
        logger.info(
            f"Rutas rápidas ({len(fast_segments)}): velocidad vacío ≥ 30 km/h"
        )
        for seg in fast_segments[:5]:  # Mostrar solo primeras 5
            logger.info(
                f"  {seg['route']}: {seg['empty_speed']:.1f}/{seg['loaded_speed']:.1f} km/h"
            )
        
        logger.info(f"Rutas medias ({len(medium_segments)}): 25-30 km/h")
        for seg in medium_segments[:3]:
            logger.info(
                f"  {seg['route']}: {seg['empty_speed']:.1f}/{seg['loaded_speed']:.1f} km/h"
            )
            
        logger.info(
            f"Rutas lentas ({len(slow_segments)}): velocidad vacío < 25 km/h"
        )
        for seg in slow_segments[:3]:
            logger.info(
                f"  {seg['route']}: {seg['empty_speed']:.1f}/{seg['loaded_speed']:.1f} km/h"
            )
            
    def get_segment_between(self, node1_name, node2_name):
        """Obtiene el segmento entre dos nodos"""
        node1 = self.nodes.get(node1_name)
        if not node1:
            return None
            
        for segment in node1.segments:
            if segment.destination.name == node2_name:
                return segment
        return None