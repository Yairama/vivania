from core.fms_manager import FMSManager

class Simulation:
    """Simulador que decide acciones y las ejecuta a traves del FMSManager."""

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
        """Aplica la logica de asignacion y actualiza el sistema."""
        for truck in self.trucks:
            if truck.is_available():
                if truck.loading:
                    dest = self._select_dump_destination(truck)
                    if dest:
                        dest_id = 0 if dest == 'crusher' else 1
                        self.manager.execute_action(('dispatch_dump', truck.id, dest_id))
                else:
                    shovel = self._find_best_shovel()
                    if shovel:
                        self.manager.execute_action(('dispatch_shovel', truck.id, shovel.id))

        self.manager.update()
        self.tick_count = self.manager.tick_count

    # ------------------------------------------------------------------
    # Decision logic (heuristics)
    # ------------------------------------------------------------------
    def _select_dump_destination(self, truck):
        """Selecciona destino de descarga sin considerar capacidad."""
        if truck.material_type == 'mineral':
            return 'crusher'
        return 'dump_zone'

    def _find_best_shovel(self):
        if not self.shovels:
            return None

        mineral = [s for s in self.shovels if s.material_type == 'mineral']
        waste = [s for s in self.shovels if s.material_type == 'waste']

        if mineral and (not waste or self.crusher.total_processed < self.dump.total_dumped):
            return min(mineral, key=lambda s: len(s.queue))
        return min(self.shovels, key=lambda s: len(s.queue))

    def get_statistics(self):
        return self.manager.get_statistics()
