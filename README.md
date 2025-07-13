# Open Pit Mining Fleet Management System (FMS) Simulator

Un simulador completo de Fleet Management System (FMS) para operaciones mineras de rajo abierto desarrollado en Python con pygame. El sistema modela el comportamiento completo de carga y acarreo de material, enfocándose en la optimización de asignación de destinos mediante algoritmos de aprendizaje por refuerzo.

## 🎯 Objetivo Principal

El simulador permite analizar y optimizar operaciones mineras mediante la simulación realista de:
- **Fleet Management System (FMS)**: Sistema de gestión de flota que controla asignación de destinos
- **Ciclos de carga y acarreo**: Modelado completo del comportamiento de camiones mineros
- **Gestión de colas y tráfico**: Simulación de hang time, queue time y bottlenecks
- **Optimización por RL**: Entrenamiento de agentes de reinforcement learning para maximizar throughput

### Control Único: Asignación de Destinos
El único elemento controlable del simulador es **la asignación de destinos de camiones**:
- ¿A qué pala enviar camiones vacíos?
- ¿Crusher o dump para descarga de material?
- Todo lo demás (movimiento, carga, descarga, colas) es simulado automáticamente

## 🏗️ Arquitectura del Sistema FMS

### Componentes Principales

#### **Equipos Móviles**
- **Trucks (Camiones)**: Flota de 20 camiones (6 de 200t y 14 de 180t) con eficiencia individual
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

#### **Simulation: Lógica de Asignación Heurística**
La clase `Simulation` implementa heurísticas avanzadas para asignación automática:
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

**Dependencias RL:**
- `gymnasium>=0.21.0` - Environment wrapper
- `stable-baselines3>=1.6.0` - Algoritmos RL
- `torch>=1.12.0` - Deep learning
- `tensorboard>=2.9.0` - Monitoreo de entrenamiento

### Ejecución del Simulador

**Modo Visual Completo (Análisis y debug):**
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
│   ├── fms_manager.py            # Núcleo FMS con interfaz RL completa
│   ├── simulation.py             # Simulador con heurísticas de asignación
│   ├── truck.py                  # Comportamiento avanzado de camiones
│   ├── shovel.py                 # Palas con materiales y eficiencias
│   ├── crusher.py                # Chancador con throughput
│   ├── dump.py                   # Botadero con estadísticas
│   ├── mine_map.py               # Red vial con velocidades variables
│   ├── dijkstra.py               # Pathfinding óptimo
│   ├── node.py & segment.py      # Infraestructura de red
│   └── visualizer.py             # Visualización avanzada adaptable
├── rl/                           # Sistema de Reinforcement Learning
│   ├── mining_env.py             # Gym environment wrapper
│   └── __init__.py
├── docs/                         # Documentación técnica
│   └── rl_env.md                 # Especificación del environment
├── tests/                        # Tests del sistema
│   └── test_env.py               # Validación del environment RL
├── train_agents.py               # Script de entrenamiento RL
├── run_visual.py                 # Ejecución con visualización
├── run_headless.py               # Ejecución sin interfaz
├── config.py                     # Configuración del sistema
├── logger.py                     # Sistema de logging
├── requirements.txt              # Dependencias del proyecto
└── main.py                       # Punto de entrada principal
```

## 🤖 Sistema de Reinforcement Learning

### Environment: `MiningEnv`

**Observation Space** (124 dimensiones normalizadas):
- Estado global: tick, producción total, camiones disponibles
- Colas y estado de crusher, dump y palas
- Estado detallado de cada camión (task, carga, eficiencia, distancias)
- Agregados espaciales: distancias promedio y utilización de flota

**Action Space**:
- 9 acciones discretas con action masking
- 0: No-op
- 1-6: Enviar camión vacío a cada pala
- 7: Enviar camión cargado al crusher
- 8: Enviar camión cargado al dump

**Reward Function**:
```python
reward = (delta_waste + 2 * delta_mineral) + fleet_utilisation - 0.1 * queue_penalty
```

### Entrenamiento de Agentes

**Entrenar con PPO (recomendado):**
```bash
python train_agents.py --algo ppo --timesteps 100000 --mode headless
```

**Entrenar con visualización (debug):**
```bash
python train_agents.py --algo ppo --timesteps 10000 --mode visual
```

**Algoritmos disponibles:**
- **PPO**: Proximal Policy Optimization (recomendado)
- **A2C**: Advantage Actor-Critic
- **DQN**: Deep Q-Network

**Características del entrenamiento:**
- Evaluación cada 5,000 timesteps
- Checkpoints automáticos cada 10,000 timesteps
- Early stopping si no hay mejora en 5 evaluaciones
- Logs de TensorBoard para métricas personalizadas
- Guardado automático del mejor modelo

### Monitoreo con TensorBoard

```bash
tensorboard --logdir training_logs/tb
```

Métricas disponibles:
- `rollout/throughput`: Producción total acumulada
- `rollout/utilization`: Utilización de la flota
- `rollout/ep_rew_mean`: Recompensa promedio por episodio
- `rollout/ep_len_mean`: Duración promedio de episodios

## 📊 Configuración del Sistema

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
- **Throughput**: Toneladas procesadas por tipo (mineral prioritario 2x)
- **Queue Time**: Tiempo promedio en colas por equipo
- **Fleet Utilization**: % de camiones trabajando vs disponibles
- **Spatial Efficiency**: Distancias promedio a destinos clave

### Dashboard en Tiempo Real:
- Estado de colas por equipo (visual)
- Camiones en movimiento con velocidades actuales
- Producción acumulada (mineral vs waste)
- Rutas activas con códigos de color por velocidad
- Detección automática de congestión de tráfico

## 🎮 Casos de Uso

### **1. Análisis Operacional**
```bash
python main.py --visual
```
- Visualización en tiempo real del comportamiento del sistema
- Identificación de bottlenecks y patrones de congestión
- Evaluación de configuraciones de flota
- Análisis de impacto de diferentes rutas

### **2. Entrenamiento de RL**
```bash
python train_agents.py --algo ppo --timesteps 100000
```
- Desarrollo de políticas de asignación inteligentes
- Comparación RL vs heurísticas tradicionales
- Optimización automática de throughput
- Monitoreo continuo vía TensorBoard

### **3. Evaluación de Modelos**
```bash
# Cargar modelo entrenado y evaluar
python -c "
from stable_baselines3 import PPO
from rl.mining_env import MiningEnv

model = PPO.load('training_logs/best/best_model')
env = MiningEnv(render_mode='visual')
obs, _ = env.reset()

for _ in range(1000):
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, done, truncated, info = env.step(action)
    if done or truncated:
        obs, _ = env.reset()
"
```

## ✅ Funcionalidades Implementadas

### **Sistema de Simulación Completo**
- [x] Modelado realista de equipos mineros (20 camiones, 6 palas, crusher, dump)
- [x] Red vial con 25 nodos y velocidades diferenciadas por tipo de ruta
- [x] Control de tráfico y distancias mínimas entre camiones (30m)
- [x] Gestión de colas FIFO con capacidades limitadas por equipo
- [x] Pathfinding automático con algoritmo Dijkstra optimizado
- [x] Sistema de estados avanzado para camiones con 8 estados distintos

### **Visualización Profesional**
- [x] Interfaz pygame redimensionable con auto-escalado
- [x] Información en tiempo real: colas, velocidades, producción acumulada
- [x] Códigos de color intuitivos por estado de camión y tipo de ruta
- [x] Visualización opcional de rutas activas con líneas punteadas
- [x] Panel de estadísticas detallado con métricas de performance
- [x] Leyenda completa y controles interactivos

### **Sistema de Reinforcement Learning**
- [x] Environment Gymnasium compatible (`MiningEnv`) con observation space de 124 dimensiones
- [x] Action space discreto (9 acciones) con action masking inteligente
- [x] Función de recompensa balanceada: producción + utilización - penalización de colas
- [x] Script de entrenamiento completo con PPO, A2C, DQN
- [x] Callbacks de evaluación automática cada 5k timesteps
- [x] Checkpoints automáticos y early stopping
- [x] Integración completa con TensorBoard para monitoreo

### **Validación y Testing**
- [x] Environment validation con `stable_baselines3.common.env_checker`
- [x] Tests automatizados para verificar terminación de episodios
- [x] Verificación automática de conectividad de red vial
- [x] Métricas de sanity check integradas en el simulador

## 🛠️ Tareas Pendientes

### **Optimizaciones de Performance**
- [ ] Optimización del loop principal para entrenamiento más rápido
- [ ] Implementación de batching para múltiples environments paralelos
- [ ] Caching inteligente de rutas calculadas frecuentemente
- [ ] Optimización de memoria para entrenamientos largos

### **Extensiones del Environment**
- [ ] Observation space configurable (diferentes niveles de detalle)
- [ ] Reward function parametrizable para diferentes objetivos
- [ ] Soporte para múltiples tipos de material con prioridades variables
- [ ] Integración de incertidumbre: fallas de equipos, variabilidad de tiempos

### **Algoritmos Avanzados**
- [ ] Implementación de algoritmos multi-agente (MADDPG, QMIX)
- [ ] Comparación con métodos de optimización clásicos (genetic algorithms)
- [ ] Hyperparameter tuning automático con Optuna
- [ ] Transfer learning entre configuraciones de mina diferentes

### **Análisis y Métricas**
- [ ] Dashboard web interactivo para análisis post-entrenamiento
- [ ] Exportación de datos a formatos estándar (CSV, JSON)
- [ ] Análisis estadístico automático de performance
- [ ] Generación automática de reportes de optimización

### **Validación Industrial**
- [ ] Calibración con datos reales de operaciones mineras
- [ ] Benchmarking contra sistemas FMS comerciales
- [ ] Casos de estudio con diferentes configuraciones de mina
- [ ] Validación de escalabilidad para flotas más grandes

## 🔧 Personalización Avanzada

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

### **Personalizar Función de Recompensa:**
```python
# En mining_env.py, método _calculate_reward()
def _calculate_reward(self) -> float:
    # Personalizar pesos y penalizaciones
    production = delta_waste + 3.0 * delta_mineral  # Mayor peso a mineral
    efficiency_bonus = working * 0.5  # Bonus por utilización
    queue_penalty = queue_total * 0.2  # Mayor penalización por colas
    return production + efficiency_bonus - queue_penalty
```

## 📝 Notas Técnicas

### **Arquitectura del Simulador**
- **Tick-based system**: Actualizaciones discretas (1 tick ≈ 0.1 horas simuladas)
- **Event-driven**: Estados y transiciones bien definidos para cada equipo
- **Modular design**: Fácil extensión y modificación de componentes
- **Performance optimized**: Modo headless para entrenamiento RL intensivo

### **Consideraciones de RL**
- **Normalización automática**: Observations normalizadas usando running statistics
- **Action masking**: Solo acciones válidas disponibles en cada timestep
- **Episode management**: Terminación por producción objetivo (400t) o límite de pasos (800)
- **Reward engineering**: Balance entre throughput, eficiencia y prevención de deadlocks

---

**Simulador FMS desarrollado como plataforma de investigación para Fleet Management Systems mineros con capacidades completas de Reinforcement Learning.**

*Objetivo: Proporcionar una plataforma robusta para el desarrollo y evaluación de algoritmos de asignación inteligente en operaciones mineras, combinando simulación realista con técnicas de IA avanzadas.*