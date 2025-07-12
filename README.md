# Open Pit Mining Fleet Management System (FMS) Simulator

Un simulador completo de Fleet Management System (FMS) para operaciones mineras de rajo abierto desarrollado en Python con pygame. El sistema modela el comportamiento completo de carga y acarreo de material, enfocándose en la optimización de asignación de destinos mediante algoritmos de aprendizaje por refuerzo.

## 🎯 Objetivo Principal

El simulador permite analizar y optimizar operaciones mineras mediante la simulación realista de:
- **Fleet Management System (FMS)**: Sistema de gestión de flota que controla asignación de destinos
- **Ciclos de carga y acarreo**: Modelado completo del comportamiento de camiones mineros
- **Gestión de colas y tráfico**: Simulación de hang time, queue time y bottlenecks con control de velocidad según distancia entre camiones
- **Optimización por RL**: Entrenamiento de agentes de reinforcement learning para maximizar throughput

### Control Único: Asignación de Destinos
El único elemento controlable del simulador es **la asignación de destinos de camiones**:
- ¿A qué pala enviar camiones vacíos?
- ¿Crusher o dump para descarga de material?
- Todo lo demás (movimiento, carga, descarga, colas) es simulado automáticamente

## 🏗️ Arquitectura del Sistema FMS

### Componentes Principales

#### **Equipos Móviles**
- **Trucks (Camiones)**: Flota de 6 camiones CAT 797 con capacidades de 200t
  - Estados: `waiting_assignment`, `moving_to_shovel`, `loading`, `moving_to_dump`, `dumping`, `returning`
  - Atributos: efficiency (0.75-0.90), velocidad variable por segmento
  - Control de tráfico: distancia mínima entre camiones (30m)
  - Pathfinding automático con algoritmo Dijkstra

#### **Equipos Fijos**
- **Shovels (Palas)**: 6 palas cargadoras con diferentes características
  - **Mineral**: c3 (40t, 85%), c4 (45t, 90%), c5 (47t, 92%)
  - **Waste**: c1 (35t, 70%), c2 (37t, 80%), c6 (47t, 88%)
  - Tiempo de carga: 5 ticks
  - Capacidad de cola: máximo 3 camiones

- **Crusher (Chancador)**: Procesamiento exclusivo de mineral
  - Throughput: 200 t/h
  - Tiempo de proceso: 4 ticks
  - Capacidad de cola: máximo 2 camiones

- **Dump (Botadero)**: Descarga de material estéril y mineral excedente
  - Tiempo de descarga: 4 ticks
  - Capacidad de cola: máximo 2 camiones

#### **Red Vial Inteligente**
- **25 Nodos** de conexión estratégicamente ubicados
- **Segmentos bidireccionales** con velocidades diferenciadas:
  - **Velocidad vacío**: 18-40 km/h según tipo de ruta
  - **Velocidad cargado**: ~60% de velocidad vacío
  - **Rutas principales**: 30-40 km/h (parking ↔ crusher/dump)
  - **Rutas secundarias**: 25-35 km/h (conexiones internas)
  - **Acceso a palas**: 18-25 km/h (maniobras lentas)

### Sistema de Control FMS

#### **FMSManager: Núcleo del Sistema**
La clase `FMSManager` centraliza toda la lógica de control y ofrece:
- **Control de asignación**: Único punto de decisión del sistema
- **Estados del sistema**: Monitoreo completo de equipos y colas
- **Interfaz RL**: Funciones optimizadas para entrenamiento
  - `get_system_state()`: Estado completo del sistema
  - `get_available_actions()`: Acciones válidas disponibles
  - `execute_action()`: Ejecutar decisión de asignación
  - `calculate_reward()`: Función de recompensa para RL

#### **Lógica de Asignación Inteligente**
El simulador incluye heurísticas avanzadas para asignación automática:
- **Balanceo mineral/waste**: Prioriza mineral cuando crusher está disponible
- **Gestión de colas**: Evita sobresaturar equipos
- **Eficiencia de distancia**: Considera rutas óptimas
- **Control de tráfico**: Previene congestión en segmentos

## 🚀 Instalación y Ejecución

### Prerrequisitos
```bash
pip install -r requirements.txt
```

**Dependencias principales:**
- `pygame>=2.1.0` - Visualización
- `numpy>=1.21.0` - Cálculos numéricos

**Dependencias RL (opcionales):**
- `gymnasium>=0.21.0` - Environment wrapper
- `stable-baselines3>=1.6.0` - Algoritmos RL
- `torch>=1.12.0` - Deep learning

### Ejecución del Simulador

**Modo Visual Completo (Recomendado para análisis):**
```bash
python main.py --visual
```

**Modo Headless (Optimizado para entrenamiento RL):**
```bash
python main.py
```

### Controles Interactivos
- **S**: Toggle información de velocidades en segmentos
- **R**: Toggle rutas activas de camiones
- **ESC**: Salir del simulador
- **Redimensionar ventana**: Auto-escalado automático

## 📁 Estructura del Proyecto

```
mining_simulation/
├── core/                          # Motor principal del simulador
│   ├── simulation.py             # Simulador con heurísticas de asignación
│   ├── fms_manager.py            # Núcleo FMS con interfaz RL
│   ├── truck.py                  # Comportamiento avanzado de camiones
│   ├── shovel.py                 # Palas con materiales y eficiencias
│   ├── crusher.py                # Chancador con throughput
│   ├── dump.py                   # Botadero con estadísticas
│   ├── mine_map.py               # Red vial con velocidades variables
│   ├── dijkstra.py               # Pathfinding óptimo
│   ├── node.py & segment.py      # Infraestructura de red
│   └── visualizer.py             # Visualización avanzada adaptable
├── rl/                           # Sistema de Reinforcement Learning
│   ├── mining_env.py             # Gym environment wrapper ✅
│   └── __init__.py
├── docs/                         # Documentación técnica
│   └── rl_env.md                 # Especificación del environment
├── tests/                        # Tests del sistema
│   └── test_env.py               # Validación del environment RL
├── train_agents.py               # Script de entrenamiento RL ✅
├── run_visual.py                 # Ejecución con visualización
├── run_headless.py               # Ejecución sin interfaz
├── config.py                     # Configuración del sistema
├── logger.py                     # Sistema de logging
├── requirements.txt              # Dependencias del proyecto
└── main.py                       # Punto de entrada principal
```

## 🎮 Funcionalidades Implementadas

### ✅ **Sistema de Simulación Completo**
- [x] Modelado realista de equipos mineros
- [x] Red vial con velocidades diferenciadas
- [x] Control de tráfico y distancias mínimas
- [x] Gestión de colas FIFO con capacidades limitadas
- [x] Pathfinding automático con Dijkstra
- [x] Sistema de estados avanzado para camiones

### ✅ **Visualización Profesional**
- [x] Interfaz pygame redimensionable
- [x] Auto-escalado para cualquier resolución
- [x] Información en tiempo real (colas, velocidades, producción)
- [x] Códigos de color intuitivos por estado
- [x] Visualización de rutas activas
- [x] Panel de estadísticas detallado

### ✅ **Sistema de Reinforcement Learning**
- [x] Environment Gymnasium compatible (`MiningEnv`)
- [x] Observation space de 11 dimensiones
- [x] Action space discreto con action masking
- [x] Función de recompensa balanceada
- [x] Script de entrenamiento con A2C, PPO, DQN
- [x] Callbacks de evaluación y checkpoints

### ✅ **Métricas y Análisis**
- [x] Throughput por tipo de material (mineral/waste)
- [x] Tiempo en colas por equipo
- [x] Utilización de equipos fijos
- [x] Estados de camiones en tiempo real
- [x] Detección automática de bottlenecks

## 🤖 Sistema de Reinforcement Learning

### Environment: `MiningEnv`

**Observation Space** (11 dimensiones normalizadas):
1. Tick de simulación
2. Mineral procesado total
3. Waste descargado total
4. Cola del crusher
5. Cola del dump
6-11. Colas de las 6 palas

**Action Space**:
- Espacio discreto con action masking
- Acciones válidas: asignación de destinos para camiones disponibles
- Máximo 36 acciones posibles (6 camiones × 6 destinos)

**Reward Function**:
```python
reward = throughput + truck_efficiency - queue_penalties
```

### Entrenamiento de Agentes

**Entrenar con PPO (recomendado):**
```bash
python train_agents.py --algo ppo --timesteps 10000 --mode headless
```

**Entrenar con visualización (debug):**
```bash
python train_agents.py --algo ppo --timesteps 5000 --mode visual
```

**Algoritmos disponibles:**
- **PPO**: Proximal Policy Optimization (recomendado)
- **A2C**: Advantage Actor-Critic
- **DQN**: Deep Q-Network

## 📊 Configuración Avanzada

### Parámetros del Simulador (`config.py`):
```python
SCREEN_WIDTH = 1920         # Resolución de pantalla
SCREEN_HEIGHT = 1080
FPS = 60                    # Frames por segundo
FOLLOW_DISTANCE = 30        # Distancia mínima entre camiones (metros)
```

### Características de la Flota:
- **6 Camiones**: Capacidad 200t, eficiencia variable (0.75-0.90)
- **6 Palas**: 3 mineral + 3 waste, diferentes capacidades y eficiencias
- **Red Vial**: 25 nodos, 40+ segmentos con velocidades realistas

### Velocidades por Tipo de Ruta:
| Tipo de Ruta | Velocidad Vacío | Velocidad Cargado |
|--------------|----------------|-------------------|
| Rutas Principales | 30-40 km/h | 18-25 km/h |
| Rutas Secundarias | 25-35 km/h | 15-20 km/h |
| Acceso a Palas | 18-25 km/h | 10-15 km/h |

## 📈 Métricas de Rendimiento

### KPIs Implementados:
- **Throughput**: Toneladas procesadas por tipo
- **Queue Time**: Tiempo promedio en colas
- **Utilization**: % de utilización por equipo
- **Cycle Time**: Tiempo completo por ciclo
- **Fleet Efficiency**: Eficiencia promedio de camiones

### Dashboard en Tiempo Real:
- Estado de colas por equipo (visual)
- Camiones en movimiento con velocidades
- Producción acumulada (mineral vs waste)
- Rutas activas con códigos de color
- Detección automática de congestión

## 🛠️ Casos de Uso

### **1. Análisis Operacional**
- Identificación de bottlenecks en el sistema
- Evaluación de configuraciones de flota
- Análisis de impacto de rutas alternativas
- Optimización de capacidades de equipos

### **2. Entrenamiento de RL**
- Desarrollo de políticas de asignación inteligentes
- Comparación RL vs heurísticas tradicionales
- Adaptación a condiciones cambiantes
- Benchmarking de algoritmos

### **3. Investigación y Desarrollo**
- Plataforma para nuevos algoritmos FMS
- Validación de estrategias operacionales
- Testing de equipos virtuales
- Análisis de sensibilidad de parámetros

## 🔧 Personalización del Sistema

### **Modificar Configuración de Flota:**
```python
# En fms_manager.py
self.trucks = [
    Truck(i, capacity=300, position=start_node, efficiency=0.90) 
    for i in range(8)  # Cambiar número y características
]
```

### **Agregar Nuevas Palas:**
```python
new_shovel = Shovel(
    id=7, 
    node=self.map.nodes["new_location"],
    material_type='mineral',
    ton_per_pass=50,
    efficiency=0.95
)
self.shovels.append(new_shovel)
```

### **Personalizar Red Vial:**
```python
# En mine_map.py - Velocidades por segmento
connect(node1, node2, empty_speed=35, loaded_speed=20)
```

## 🔮 Roadmap de Desarrollo

### **Próximas Mejoras Prioritarias:**
- [ ] **Métricas avanzadas**: KPIs adicionales del FMS
- [ ] **Algoritmos de optimización**: Nuevas estrategias de asignación
- [ ] **Multi-objetivo**: Optimización de múltiples objetivos simultáneos
- [ ] **Mantenimiento programado**: Simulación de paradas por mantención

### **Extensiones a Largo Plazo:**
- [ ] **Uncertainty modeling**: Fallas de equipos, clima, variabilidad
- [ ] **Real-time adaptation**: Capacidades de adaptación en tiempo real
- [ ] **Integration APIs**: Conectores para sistemas FMS reales
- [ ] **Calibración con datos reales**: Validación con operaciones mineras

## 📝 Notas Técnicas

### **Arquitectura del Simulador**
- **Tick-based system**: Actualizaciones discretas (1 tick ≈ 0.1 horas)
- **Event-driven**: Estados y transiciones bien definidos
- **Modular design**: Fácil extensión y modificación
- **Performance optimized**: Modo headless para entrenamiento intensivo

### **Validación del Modelo**
- Verificación automática de conectividad de red
- Detección de camiones atascados
- Balanceo automático de tipos de material
- Métricas de sanity check integradas

### **Consideraciones de Performance**
- Visualización opcional sin impacto en lógica de simulación
- Escalado automático para diferentes resoluciones
- Logging configurable por nivel
- Optimizado para entrenamiento RL continuo

## 🤝 Contribuciones

### **Áreas de Contribución:**
1. **Algoritmos RL**: Nuevos agentes y estrategias de entrenamiento
2. **Métricas**: KPIs adicionales y análisis avanzados
3. **Optimización**: Mejoras de performance y escalabilidad
4. **Validación**: Casos de prueba y benchmarks industriales

### **Guías de Desarrollo:**
- Seguir la arquitectura modular existente
- Mantener compatibilidad con el sistema RL
- Documentar nuevas funcionalidades
- Incluir tests para cambios críticos

---

**Simulador FMS desarrollado como plataforma de investigación para Fleet Management Systems mineros con capacidades completas de Reinforcement Learning.**

*Objetivo: Proporcionar una plataforma robusta para el desarrollo y evaluación de algoritmos de asignación inteligente en operaciones mineras, combinando simulación realista con técnicas de IA avanzadas.*