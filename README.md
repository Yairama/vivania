# Open Pit Mining Simulation

Un simulador de operaciones mineras de rajo abierto desarrollado en Python con pygame, que modela el comportamiento completo de carga y acarreo de material en una mina.

## 🎯 Objetivo

El simulador permite analizar y optimizar operaciones mineras mediante la simulación de:
- Ciclos de carga y acarreo de camiones
- Gestión de colas en equipos de carga y descarga
- Optimización de rutas y tiempos
- Análisis de productividad y cuellos de botella

## 🏗️ Arquitectura del Sistema

### Componentes Principales

- **Trucks (Camiones)**: Entidades móviles que transportan material
- **Shovel (Pala)**: Equipo de carga que llena los camiones
- **Crusher (Chancador)**: Punto de descarga para procesamiento
- **Dump (Botadero)**: Punto de descarga para material estéril
- **Nodes (Nodos)**: Puntos de conexión en la red vial
- **Segments (Segmentos)**: Conexiones entre nodos con distancias

### Estados del Sistema

#### Estados de Camiones:
- `waiting_shovel`: Esperando carga en la pala
- `loading`: En proceso de carga
- `driving`: Transportando material
- `waiting_dumping`: Esperando descarga
- `dumping`: En proceso de descarga
- `returning`: Regresando al punto de carga

## 🚀 Instalación y Ejecución

### Prerrequisitos
```bash
pip install pygame
```

### Ejecución

**Modo Visual (con interfaz gráfica):**
```bash
python main.py --visual
```

**Modo Headless (sin interfaz):**
```bash
python main.py
```

## 📁 Estructura del Proyecto

```
mining_simulation/
├── core/
│   ├── crusher.py          # Lógica del chancador
│   ├── dump.py             # Lógica del botadero
│   ├── mine_map.py         # Mapa de la mina y conectividad
│   ├── node.py             # Nodos de la red vial
│   ├── segment.py          # Segmentos entre nodos
│   ├── shovel.py           # Lógica de la pala cargadora
│   ├── simulation.py       # Motor principal de simulación
│   ├── truck.py            # Comportamiento de camiones
│   └── visualizer.py       # Renderizado visual
├── config.py               # Configuración del sistema
├── main.py                 # Punto de entrada
├── run_headless.py         # Ejecución sin interfaz
└── run_visual.py           # Ejecución con interfaz
```

## 🔧 Configuración

### Parámetros Modificables (config.py):
- `SCREEN_WIDTH`: Ancho de pantalla (800px)
- `SCREEN_HEIGHT`: Alto de pantalla (600px)
- `TILE_SIZE`: Tamaño base de elementos (50px)
- `FPS`: Frames por segundo (60)

### Tiempos de Proceso:
- **Shovel**: 5 unidades de tiempo (configurable)
- **Crusher/Dump**: 4 unidades de tiempo (configurable)

## 🎮 Interfaz Visual

### Códigos de Color:
- **Nodos**:
  - Blanco: Nodos regulares
  - Naranja: Pala cargadora
  - Cyan: Chancador
  - Rojo: Botadero

- **Camiones**:
  - Amarillo: Esperando carga
  - Verde: Transportando material
  - Magenta: Esperando descarga
  - Azul: Regresando vacío
  - Gris: Estado indefinido

### Elementos Visuales:
- Líneas grises: Conexiones viales
- Círculos: Nodos de la red
- Rectángulos: Camiones en diferentes estados

## 📊 Funcionalidades de Simulación

### Gestión de Colas
- **Queue Management**: Sistema de colas FIFO para equipos
- **Wait Times**: Tracking de tiempos de espera
- **Bottleneck Analysis**: Identificación automática de cuellos de botella

### Lógica de Routing
- **Pathfinding**: Navegación entre nodos
- **Load Balancing**: Distribución de carga entre crusher y dump
- **Traffic Management**: Prevención de congestión

### Métricas de Rendimiento
- Tiempo total de ciclo por camión
- Utilización de equipos
- Throughput del sistema
- Tiempos de espera promedio

## 🛠️ Personalización

### Agregar Nuevos Nodos:
```python
# En mine_map.py
nodes['nuevo_nodo'] = Node('nuevo_nodo', x, y)
```

### Modificar Conectividad:
```python
# En mine_map.py
connections.append(('nodo1', 'nodo2'))
```

### Ajustar Flota:
```python
# En simulation.py
self.trucks = [Truck(i, 100, self.map.nodes["Pit"]) for i in range(N)]
```

## 📈 Casos de Uso

1. **Análisis de Productividad**: Evaluar throughput del sistema
2. **Optimización de Flota**: Determinar número óptimo de camiones
3. **Planificación de Rutas**: Optimizar caminos de transporte
4. **Análisis de Cuellos de Botella**: Identificar limitaciones operacionales
5. **Simulación de Escenarios**: Probar diferentes configuraciones

## 🔮 Futuras Mejoras

- [ ] Implementar algoritmos de pathfinding (A*, Dijkstra)
- [ ] Agregar sistema de prioridades para camiones
- [ ] Incorporar mantenimiento programado de equipos
- [ ] Métricas de consumo de combustible
- [ ] Análisis estadístico avanzado
- [ ] Exportación de datos de simulación
- [ ] Interfaz web para configuración remota

## 📝 Notas Técnicas

- La simulación usa un tick-based system para actualizaciones discretas
- Los tiempos están en unidades arbitrarias (pueden representar segundos, minutos, etc.)
- El mapa está hardcodeado pero puede ser fácilmente parametrizado
- La visualización es opcional y no afecta la lógica de simulación

## 🤝 Contribuciones

Este proyecto está diseñado para ser extensible. Las áreas principales para contribuir incluyen:
- Algoritmos de optimización
- Nuevos tipos de equipos
- Métricas adicionales
- Mejoras en la visualización
- Casos de prueba automatizados

---

*Simulador desarrollado para análisis y optimización de operaciones mineras de rajo abierto.*