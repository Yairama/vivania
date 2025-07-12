# Open Pit Mining Fleet Management System (FMS) Simulator

Un simulador avanzado de Fleet Management System (FMS) para operaciones mineras de rajo abierto desarrollado en Python con pygame. El sistema modela el comportamiento completo de carga y acarreo de material, enfocándose en la optimización de asignación de destinos de camiones mediante algoritmos de aprendizaje por refuerzo.

## 🎯 Objetivo Principal

El simulador permite analizar y optimizar operaciones mineras mediante la simulación realista de:
- **Fleet Management System (FMS)**: Sistema de gestión de flota que controla asignación de destinos
- **Ciclos de carga y acarreo**: Modelado completo del comportamiento de camiones mineros
- **Gestión de colas y tráfico**: Simulación de hang time, queue time y bottlenecks
  con control de velocidad según distancia entre camiones
- **Optimización por RL**: Entrenamiento de agentes de reinforcement learning para maximizar throughput

### Objetivo Final: Sistema de Reinforcement Learning
- **Algoritmos**: A2C (Advantage Actor-Critic) y Deep Q-Learning (DQN)
- **Meta**: Aprender a operar el FMS para maximizar material movido y minimizar tiempos muertos
- **Control**: Asignación inteligente de destinos de camiones en tiempo real

## 🏗️ Arquitectura del Sistema FMS

### Componentes Principales del FMS

#### **Equipos Móviles**
- **Trucks (Camiones)**: Flota de camiones CAT 797 con capacidades de 200-400t
  - Estados: waiting_assignment, moving_to_shovel, loading, moving_to_dump, dumping, returning
  - Atributos: efficiency (0.7-0.95), capacidad, velocidad por segmento
  - Métricas: cycle time, payload efficiency, utilization

#### **Equipos Fijos**
- **Shovels (Palas)**: 6 palas cargadoras con diferentes características
  - Tipos: Mineral (c3, c4, c5) y Waste (c1, c2, c6)
  - Capacidad: 35-47 toneladas por pase
  - Eficiencia: 0.7-0.92
  - Tiempo de carga: configurable (default 5 ticks)

- **Crusher (Chancador)**: Procesamiento de mineral
  - Throughput: 200 t/h
  - Tiempo de proceso: 4 ticks
  - Capacidad de cola: máximo 2 camiones

- **Dump (Botadero)**: Descarga de material estéril
  - Tiempo de descarga: 4 ticks
  - Capacidad de cola: máximo 2 camiones

#### **Infraestructura Vial**
- **Nodes (Nodos)**: 25 puntos de conexión en la red vial
- **Segments (Segmentos)**: Conexiones bidireccionales con velocidades diferenciadas
  - Velocidad vacío: 18-40 km/h según tipo de ruta
  - Velocidad cargado: 60% de velocidad vacío
  - Tipos: rutas principales, secundarias, acceso a palas

### Sistema de Control FMS

#### **Único Punto de Control**
- **Asignación de Destinos**: El único elemento controlable del sistema
- **Decision Making**: ¿A qué pala enviar camiones vacíos? ¿Crusher o dump para descarga?
- **Optimización**: Balanceo de colas, minimización de hang time

#### **Estados del Sistema Monitoreados**
- Cola en cada pala (0-3 camiones máximo)
- Estado de equipos fijos (busy/idle)
- Posición y estado de todos los camiones
- Throughput acumulado por tipo de material
- Tiempos de ciclo y utilización

## 🚀 Instalación y Ejecución

### Prerrequisitos
```bash
pip install pygame numpy
```

### Ejecución del Simulador

**Modo Visual Completo (Recomendado):**
```bash
python main.py --visual
```

**Modo Headless (para entrenamiento RL):**
```bash
python main.py
```

### Controles Interactivos
- **S**: Toggle velocidades en segmentos
- **R**: Toggle rutas de camiones
- **ESC**: Salir
- **Redimensionar**: Ventana adaptable con auto-escalado

## 📁 Estructura del Proyecto Avanzado

```
mining_simulation/
├── core/
│   ├── simulation.py       # Motor principal FMS con lógica de asignación
│   ├── truck.py           # Comportamiento avanzado de camiones con velocidades
│   ├── shovel.py          # Palas con diferentes materiales y eficiencias
│   ├── crusher.py         # Chancador con throughput y métricas
│   ├── dump.py            # Botadero con capacidad y estadísticas
│   ├── mine_map.py        # Red vial con velocidades diferenciadas
│   ├── node.py            # Nodos de conexión
│   ├── segment.py         # Segmentos con velocidades loaded/empty
│   ├── dijkstra.py        # Pathfinding para navegación óptima
│   └── visualizer.py      # Visualización avanzada y adaptable
├── rl/                    # [PENDIENTE] Sistema de Reinforcement Learning
│   ├── environment.py     # Gym environment wrapper
│   ├── agents/
│   │   ├── a2c_agent.py   # Advantage Actor-Critic
│   │   └── dqn_agent.py   # Deep Q-Network
│   ├── rewards.py         # Sistema de recompensas
│   └── training.py        # Scripts de entrenamiento
├── config.py              # Configuración del sistema
├── main.py                # Punto de entrada
├── run_headless.py        # Ejecución para entrenamiento
├── run_visual.py          # Ejecución con visualización
└── README.md              # Esta documentación
```

## 🔧 Configuración Avanzada

### Parámetros del Simulador (config.py):
- `SCREEN_WIDTH/HEIGHT`: Resolución (1920x1080 default)
- `FPS`: 60 FPS para simulación fluida
- `FOLLOW_DISTANCE`: distancia mínima entre camiones en un mismo segmento
- Tiempos configurables por equipo

### Flota y Equipos:
- **6 Camiones CAT 797**: Eficiencia variable (0.85 base)
- **6 Palas**: 3 mineral + 3 waste con características únicas
- **Red Vial**: 25 nodos, 40+ segmentos con velocidades realistas

### Velocidades por Tipo de Ruta:
- **Rutas Principales**: 30-40 km/h (vacío), 18-25 km/h (cargado)
- **Rutas Secundarias**: 25-35 km/h (vacío), 15-20 km/h (cargado)  
- **Acceso a Palas**: 18-25 km/h (vacío), 10-15 km/h (cargado)

## 📊 Métricas y KPIs del FMS

### Métricas de Rendimiento Implementadas:
- **Throughput**: Toneladas procesadas por tipo (mineral/waste)
- **Cycle Time**: Tiempo completo por ciclo de camión
- **Queue Time**: Tiempo en colas por equipo
- **Hang Time**: Tiempo de equipos inactivos
- **Utilization**: % de utilización por equipo
- **Fleet Efficiency**: Eficiencia promedio de la flota

### Dashboard Visual en Tiempo Real:
- Estado de colas por equipo
- Camiones en movimiento con velocidades
- Producción acumulada
- Rutas activas de camiones
- Código de colores por estado/velocidad

## 🤖 Sistema de Reinforcement Learning (En Desarrollo)

### Estado Actual: Simulador Completo ✅
- [x] Simulación completa del FMS
- [x] Modelado realista de equipos y rutas
- [x] Sistema de colas y tráfico
- [x] Métricas de rendimiento
- [x] Visualización avanzada
- [x] Pathfinding con Dijkstra

### Próximos Desarrollos: Sistema RL

#### **1. Environment Wrapper (Prioritario)**
```python
# Pendiente: rl/environment.py
class MiningFMSEnv(gym.Env):
    - observation_space: Estado del sistema FMS
    - action_space: Asignación de destinos
    - reward_function: Maximizar throughput, minimizar hang
    - step(): Ejecutar acción y obtener nuevo estado
```

#### **2. Agentes de RL**
```python
# Pendiente: rl/agents/
- A2C Agent: Actor-Critic para acciones continuas
- DQN Agent: Q-Learning para acciones discretas
- Arquitecturas de red neuronal optimizadas
```

#### **3. Sistema de Recompensas**
- **Positivas**: Throughput, eficiencia de carga, ciclos completos
- **Negativas**: Hang time, queue excesivo, camiones idle
- **Balanceadas**: Mineral vs waste según demanda

#### **4. Entrenamiento y Evaluación**
- Scripts de entrenamiento automático
- Métricas de convergencia
- Comparación con reglas heurísticas
- Transferencia a escenarios complejos

## 🎮 Funcionalidades Avanzadas Actuales

### **Sistema de Asignación Inteligente**
- Balanceo automático entre mineral/waste
- Consideración de colas y capacidades
- Pathfinding óptimo con Dijkstra
- Asignación basada en distancia y eficiencia

### **Simulación Realista**
- Velocidades diferenciadas por carga y ruta
- Eficiencia variable por camión
- Tiempos de proceso realistas
- Gestión de colas FIFO

### **Visualización Profesional**
- Auto-escalado para cualquier resolución
- Ventana redimensionable
- Información en tiempo real
- Códigos de color intuitivos
- Rutas y velocidades visuales

### **Análisis de Rendimiento**
- Detección de bottlenecks automática
- Estadísticas de producción
- Tracking de camiones atascados
- Debug information detallado

## 📈 Casos de Uso y Aplicaciones

### **1. Optimización FMS Tradicional**
- Evaluación de reglas de asignación heurísticas
- Análisis de sensibilidad de parámetros
- Identificación de bottlenecks operacionales

### **2. Entrenamiento de RL (Objetivo Principal)**
- Desarrollo de políticas de asignación inteligentes
- Comparación RL vs reglas tradicionales
- Adaptación a condiciones cambiantes

### **3. Análisis de Escenarios**
- Pruebas de diferentes configuraciones de flota
- Evaluación de impacto de rutas alternativas
- Simulación de mantenimientos programados

### **4. Investigación y Desarrollo**
- Benchmarking de algoritmos de FMS
- Validación de estrategias operacionales
- Plataforma para nuevos algoritmos

## 🔮 Roadmap de Desarrollo

### **Fase 1: Completar RL System (Próximo)**
- [ ] Implementar environment wrapper
- [ ] Desarrollar agentes A2C y DQN  
- [ ] Sistema de recompensas balanceado
- [ ] Scripts de entrenamiento básico

### **Fase 2: Optimización y Métricas**
- [ ] Métricas avanzadas de FMS
- [ ] Hyperparameter tuning automático
- [ ] Comparación con benchmarks industriales
- [ ] Exportación de datos para análisis

### **Fase 3: Funcionalidades Avanzadas**
- [ ] Mantenimiento programado de equipos
- [ ] Condiciones climáticas variables
- [ ] Múltiples tipos de mineral
- [ ] Prioridades dinámicas de producción

### **Fase 4: Validación Industrial**
- [ ] Calibración con datos reales
- [ ] Integración con sistemas FMS existentes
- [ ] Validación en minas piloto
- [ ] Transferencia a producción

## 🛠️ Personalización del Sistema

### **Modificar Flota:**
```python
# En simulation.py
self.trucks = [
    Truck(i, capacity=200, position=start_node, efficiency=0.85) 
    for i in range(8)  # Cambiar número de camiones
]
```

### **Agregar Nuevas Palas:**
```python
# En simulation.py  
new_shovel = Shovel(
    id=7, 
    node=self.map.nodes["new_location"],
    material_type='mineral',
    ton_per_pass=50,
    efficiency=0.9
)
```

### **Configurar Red Vial:**
```python
# En mine_map.py
# Velocidades personalizadas por segmento
connect(node1, node2, empty_speed=35, loaded_speed=20)
```

## 📝 Notas Técnicas Importantes

### **Arquitectura del Simulador**
- **Tick-based system**: Actualizaciones discretas cada tick
- **Pathfinding**: Dijkstra para rutas óptimas entre nodos
- **State Management**: Estados complejos para todos los equipos
- **Scalable Design**: Fácil extensión para nuevos equipos/algoritmos

### **Consideraciones de Performance**
- Optimizado para entrenamiento RL (modo headless)
- Visualización opcional sin impacto en lógica
- Escalado automático para diferentes resoluciones
- Debug information configurable

### **Validación del Modelo**
- Verificación de conectividad automática
- Detección de camiones atascados
- Balanceo de tipos de material
- Métricas de sanity check

## 🤝 Contribuciones y Extensiones

### **Áreas Prioritarias para Contribuir:**
1. **Sistema de RL**: Implementación de agentes y training loops
2. **Métricas Avanzadas**: KPIs adicionales del FMS
3. **Algoritmos de Optimización**: Nuevas estrategias de asignación
4. **Validación**: Casos de prueba y benchmarks

### **Extensiones Propuestas:**
- Multi-objetivo optimization (throughput + consumo + desgaste)
- Uncertainty modeling (fallas de equipos, clima)
- Real-time adaptation capabilities
- Integration APIs para sistemas reales

---

**Simulador FMS desarrollado como plataforma de investigación para Fleet Management Systems mineros con capacidades de Reinforcement Learning integradas.**

*Objetivo: Revolucionar la operación de FMS mediante IA que aprende y optimiza automáticamente las decisiones de asignación de flota en tiempo real.*