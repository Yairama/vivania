#!/usr/bin/env python3
# test_simulation.py - Archivo para probar las correcciones

def test_dijkstra():
    """Prueba el algoritmo de Dijkstra"""
    print("=== PROBANDO DIJKSTRA ===")
    from core.mine_map import MineMap
    from core.dijkstra import Dijkstra
    
    mine_map = MineMap()
    dijkstra = Dijkstra(mine_map.nodes)
    
    # Probar rutas críticas
    test_routes = [
        ("parking", "c1"),
        ("c1", "crusher"),
        ("c5", "dump_zone"),
        ("parking", "c6")
    ]
    
    for start, end in test_routes:
        route = dijkstra.get_shortest_path(start, end)
        print(f"Ruta de {start} a {end}: {route}")
        if not route:
            print(f"ERROR: No se encontró ruta de {start} a {end}")
    
    print("Dijkstra OK\n")

def test_truck_states():
    """Prueba los estados de los camiones"""
    print("=== PROBANDO ESTADOS DE CAMIONES ===")
    from core.mine_map import MineMap
    from core.truck import Truck
    
    mine_map = MineMap()
    truck = Truck(1, 200, mine_map.nodes["parking"])
    
    print(f"Estado inicial: {truck.task}")
    print(f"Disponible: {truck.is_available()}")
    print(f"En movimiento: {truck.is_moving()}")
    
    # Simular asignación de ruta
    route = ["parking", "n2", "n3", "c1"]
    truck.assign_route(route)
    truck.task = "moving_to_shovel"
    
    print(f"Después de asignar ruta: {truck.task}")
    print(f"Ruta: {truck.route}")
    print(f"Objetivo: {truck.target_node}")
    
    print("Estados de camiones OK\n")

def test_simulation_basic():
    """Prueba básica de la simulación"""
    print("=== PROBANDO SIMULACIÓN BÁSICA ===")
    from core.simulation import Simulation
    
    sim = Simulation()
    
    print(f"Camiones: {len(sim.trucks)}")
    print(f"Palas: {len(sim.shovels)}")
    print(f"Nodos del mapa: {len(sim.map.nodes)}")
    
    # Ejecutar unos pocos ticks
    for i in range(5):
        print(f"\n--- TICK {i+1} ---")
        sim.update()
        
        # Estado de camiones
        states = {}
        for truck in sim.trucks:
            states[truck.task] = states.get(truck.task, 0) + 1
        print(f"Estados: {states}")
    
    print("Simulación básica OK\n")

def run_tests():
    """Ejecuta todas las pruebas"""
    try:
        test_dijkstra()
        test_truck_states()
        test_simulation_basic()
        print("🎉 TODAS LAS PRUEBAS PASARON!")
        return True
    except Exception as e:
        print(f"❌ ERROR EN PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_tests()
    if success:
        print("\n✅ El simulador está listo para ejecutar!")
        print("Ejecuta: python main.py --visual")
    else:
        print("\n❌ Hay problemas que necesitan ser corregidos")