from core.fms_manager import FMSManager

class Simulation:
    """Simulador que avanza el tiempo delegando la logica al FMSManager."""

    def __init__(self):
        self.manager = FMSManager()

        # Exponer referencias utiles para compatibilidad con el visualizador
        self.map = self.manager.map
        self.trucks = self.manager.trucks
        self.shovels = self.manager.shovels
        self.crusher = self.manager.crusher
        self.dump = self.manager.dump
        self.tick_count = 0

    def update(self):
        self.manager.update()
        self.tick_count = self.manager.tick_count

    def get_statistics(self):
        return self.manager.get_statistics()
