
# core/segment.py (Mejorado)
import math

class Segment:
    def __init__(self, origin, destination, distance, empty_speed=25.0, loaded_speed=15.0):
        self.origin = origin
        self.destination = destination
        self.distance = distance
        self.empty_speed = empty_speed  # km/h cuando está vacío
        self.loaded_speed = loaded_speed  # km/h cuando está cargado
        origin.connect(self)
        
    def get_travel_time(self, is_loaded=False):
        """Calcula el tiempo de viaje en este segmento"""
        speed = self.loaded_speed if is_loaded else self.empty_speed
        return self.distance / speed  # tiempo en horas
        
    def get_speed(self, is_loaded=False):
        """Obtiene la velocidad para este segmento"""
        return self.loaded_speed if is_loaded else self.empty_speed
