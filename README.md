# Open Pit Mining Fleet Management System (FMS) Simulator

A comprehensive Fleet Management System (FMS) simulator for open pit mining operations developed in Python with pygame. The system models complete hauling and loading material behavior, focusing on destination assignment optimization through reinforcement learning algorithms.

## 🚀 Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the simulator in visual mode:
   ```bash
   python main.py --visual
   ```
3. For training or headless execution:
   ```bash
   python main.py
   ```

---

## 🎯 Main Objective

The simulator allows analysis and optimization of mining operations through realistic simulation of:
- **Fleet Management System (FMS)**: Fleet management system that controls destination assignment
- **Loading and hauling cycles**: Complete modeling of mining truck behavior
- **Queue and traffic management**: Simulation of hang time, queue time and bottlenecks
- **RL optimization**: Training reinforcement learning agents to maximize throughput

### Single Control: Destination Assignment
The only controllable element of the simulator is **truck destination assignment**:
- Which shovel to send empty trucks to?
- Crusher or dump for material discharge?
- Everything else (movement, loading, unloading, queues) is automatically simulated

## 🏗️ FMS System Architecture

### Main Components

#### **Mobile Equipment**
- **Trucks**: Fleet of 30 trucks (16 of 200t and 14 of 180t) with individual efficiency
  - States: `waiting_assignment`, `moving_to_shovel`, `loading`, `moving_to_dump`, `dumping`, `returning`
  - Attributes: efficiency (0.75-0.90), variable speed per segment
  - Traffic control: minimum distance between trucks (30m)
  - Automatic pathfinding with Dijkstra algorithm

#### **Fixed Equipment**
- **Shovels**: 6 loading shovels with different characteristics
  - **Ore**: c3 (40t, 85%), c4 (45t, 90%), c5 (47t, 92%)
  - **Waste**: c1 (35t, 70%), c2 (37t, 80%), c6 (47t, 88%)
  - Loading time: 5 ticks
  - Queue capacity: maximum 3 trucks

- **Crusher**: Exclusive ore processing
  - Throughput: 200 t/h
  - Processing time: 4 ticks
  - Queue capacity: maximum 2 trucks

- **Dump**: Waste and excess ore disposal
  - Unloading time: 4 ticks
  - Queue capacity: maximum 2 trucks

#### **Intelligent Road Network**
- **25 Nodes** strategically connected
- **Bidirectional segments** with differentiated speeds:
  - **Empty speed**: 18-40 km/h depending on route type
  - **Loaded speed**: ~60% of empty speed
  - **Main routes**: 30-40 km/h (parking ↔ crusher/dump)
  - **Secondary routes**: 25-35 km/h (internal connections)
  - **Shovel access**: 18-25 km/h (slow maneuvers)

### FMS Control System

#### **FMSManager: System Core**
The `FMSManager` class centralizes all control logic and offers:
- **Assignment control**: Single system decision point
- **System states**: Complete monitoring of equipment and queues
- **RL interface**: Functions optimized for training
  - `get_system_state()`: Complete system state
  - `get_available_actions()`: Available valid actions
  - `execute_action()`: Execute assignment decision
  - `calculate_reward()`: Reward function for RL

#### **Simulation: Heuristic Assignment Logic**
The `Simulation` class implements advanced heuristics for automatic assignment:
- **Ore/waste balancing**: Prioritizes ore when crusher is available
- **Queue management**: Avoids equipment oversaturation
- **Distance efficiency**: Considers optimal routes
- **Traffic control**: Prevents segment congestion

## 🚀 Installation and Execution

### Prerequisites
```bash
pip install -r requirements.txt
```

**Main dependencies:**
- `pygame>=2.1.0` - Visualization
- `numpy>=1.21.0` - Numerical calculations

**RL dependencies:**
- `gymnasium>=0.21.0` - Environment wrapper
- `stable-baselines3>=1.6.0` - RL algorithms
- `torch>=1.12.0` - Deep learning
- `tensorboard>=2.9.0` - Training monitoring

### Simulator Execution

**Full Visual Mode (Analysis and debug):**
```bash
python main.py --visual
```

**Headless Mode (Optimized for RL training):**
```bash
python main.py
```

**TensorBoard:**
```bash
tensorboard --logdir training_logs/tb
```

### Interactive Controls
- **S**: Toggle segment speed information
- **R**: Toggle active truck routes
- **ESC**: Exit simulator
- **Resize window**: Automatic auto-scaling

## 📁 Project Structure

```
mining_simulation/
├── core/                          # Main simulator engine
│   ├── fms_manager.py            # FMS core with complete RL interface
│   ├── simulation.py             # Simulator with assignment heuristics
│   ├── truck.py                  # Advanced truck behavior
│   ├── shovel.py                 # Shovels with materials and efficiencies
│   ├── crusher.py                # Crusher with throughput
│   ├── dump.py                   # Dump with statistics
│   ├── mine_map.py               # Road network with variable speeds
│   ├── dijkstra.py               # Optimal pathfinding
│   ├── node.py & segment.py      # Network infrastructure
│   └── visualizer.py             # Advanced adaptable visualization
├── rl/                           # Reinforcement Learning system
│   ├── mining_env.py             # Gym environment wrapper
│   └── __init__.py
├── docs/                         # Technical documentation
│   └── rl_env.md                 # Environment specification
├── tests/                        # System tests
│   └── test_env.py               # RL environment validation
├── train_agents.py               # RL training script
├── run_visual.py                 # Execution with visualization
├── run_headless.py               # Headless execution
├── config.py                     # System configuration
├── logger.py                     # Logging system
├── requirements.txt              # Project dependencies
└── main.py                       # Main entry point
```

## 🤖 Reinforcement Learning System

### Environment: `MiningEnv`

**Observation Space** (84 continuous values + action mask of 270)
- Hierarchical structure local/global/communication/temporal
- Global state: tick, total production, available trucks
- Queues and state of crusher, dump and shovels
- Detailed state of each truck (task, load, efficiency, distances)
- Spatial aggregates: average distances, fleet utilization and wrong route penalties

**Action Space**:
- One independent command per truck `[9] * num_trucks`
- Command 0: No-op
- Commands 1-6: Send empty truck to each shovel
- Command 7: Send loaded truck to crusher
- Command 8: Send loaded truck to dump

**Reward Function**:
```python
reward = (delta_waste + 2 * delta_mineral) + fleet_utilisation - 0.1 * queue_penalty
```

### Agent Training

**Train with PPO (recommended):**
```bash
python train_agents.py --timesteps 100000 --mode headless
```

**Train with visualization (debug):**
```bash
python train_agents.py --timesteps 10000 --mode visual
```

**Resume from checkpoint:**
```bash
python train_agents.py --timesteps 50000 --resume-from training_logs/checkpoints
```

**Available algorithm:**
- **PPO**: Proximal Policy Optimization (recommended)

**Training features:**
- Automatic checkpoints every 10,000 timesteps
- TensorBoard logs for custom metrics
- Automatic best model saving
- Resume training from checkpoint with `--resume-from`

### TensorBoard Monitoring

```bash
tensorboard --logdir training_logs/tb
```

Available metrics:
- `rollout/throughput`: Total accumulated production
- `rollout/utilization`: Fleet utilization
- `rollout/ep_rew_mean`: Average reward per episode
- `rollout/ep_len_mean`: Average episode duration
- `rollout/mineral_crusher`: Ore unloaded at crusher
- `rollout/mineral_dump`: Ore unloaded at dump
- `rollout/waste_in_crusher`: Waste unloaded at crusher
- `rollout/waste_dump`: Waste unloaded at dump
- `rollout/wrong_assignments`: Incorrectly assigned trucks

## 📊 System Configuration

### Simulator Parameters (`config.py`):
```python
SCREEN_WIDTH = 1920         # Screen resolution
SCREEN_HEIGHT = 1080
FPS = 60                    # Frames per second
FOLLOW_DISTANCE = 30        # Minimum distance between trucks (meters)
```

### Fleet Characteristics:
- **30 Trucks (16 of 200t and 14 of 180t)**: Capacities 180-200t with variable efficiency (0.75-1.04)
- **6 Shovels**: 3 ore + 3 waste, different capacities and efficiencies
- **Road Network**: 25 nodes, 40+ segments with realistic speeds

### Speeds by Route Type:
| Route Type | Empty Speed | Loaded Speed |
|------------|-------------|--------------|
| Main Routes | 30-40 km/h | 18-25 km/h |
| Secondary Routes | 25-35 km/h | 15-20 km/h |
| Shovel Access | 18-25 km/h | 10-15 km/h |

## 📈 Performance Metrics

### Implemented KPIs:
- **Throughput**: Tons processed by type (ore priority 2x)
- **Queue Time**: Average time in queues per equipment
- **Fleet Utilization**: % of trucks working vs available
- **Spatial Efficiency**: Average distances to key destinations

### Real-time Dashboard:
- Equipment queue status (visual)
- Moving trucks with current speeds
- Accumulated production (ore vs waste)
- Active routes with color codes by speed
- Automatic traffic congestion detection

## 🎮 Use Cases

### **1. Operational Analysis**
```bash
python main.py --visual
```
- Real-time visualization of system behavior
- Bottleneck and congestion pattern identification
- Fleet configuration evaluation
- Different route impact analysis

### **2. RL Training**
```bash
python train_agents.py --timesteps 100000
```
- Development of intelligent assignment policies
- RL vs traditional heuristics comparison
- Automatic throughput optimization
- Continuous monitoring via TensorBoard

### **3. Model Evaluation**
```bash
# Load trained model and evaluate
python eval.py --from training_logs/best/best_model.zip --mode visual --steps 1000
```

## ✅ Implemented Features

### **Complete Simulation System**
- [x] Realistic modeling of mining equipment (30 trucks, 6 shovels, crusher, dump)
- [x] Road network with 25 nodes and differentiated speeds by route type
- [x] Traffic control and minimum distances between trucks (30m)
- [x] FIFO queue management with limited capacities per equipment
- [x] Automatic pathfinding with optimized Dijkstra algorithm
- [x] Advanced state system for trucks with 8 distinct states

### **Professional Visualization**
- [x] Resizable pygame interface with auto-scaling
- [x] Real-time information: queues, speeds, accumulated production
- [x] Intuitive color codes by truck state and route type
- [x] Optional visualization of active routes with dotted lines
- [x] Detailed statistics panel with performance metrics
- [x] Complete legend and interactive controls

### **Reinforcement Learning System**
- [x] Gymnasium compatible environment (`MiningEnv`) with structured observation space of 84 continuous values and action mask of 270 dimensions
- [x] Multi-discrete action space with one command per truck
- [x] Balanced reward function: production + utilization - queue penalty
- [x] PPO training script
- [x] Automatic checkpoints
- [x] Complete TensorBoard integration for monitoring
- [x] Ability to resume training from checkpoints

### **Validation and Testing**
- [x] Environment validation with `stable_baselines3.common.env_checker`
- [x] Automated tests to verify episode termination
- [x] Automatic road network connectivity verification
- [x] Sanity check metrics integrated in simulator

## 🛠️ Pending Tasks

### **Performance Optimizations**
- [ ] Main loop optimization for faster training
- [ ] Batching implementation for multiple parallel environments
- [ ] Intelligent caching of frequently calculated routes
- [ ] Memory optimization for long training sessions

### **Environment Extensions**
- [ ] Configurable observation space (different detail levels)
- [ ] Parameterizable reward function for different objectives
- [ ] Support for multiple material types with variable priorities
- [ ] Uncertainty integration: equipment failures, time variability

### **Advanced Algorithms**
- [ ] Multi-agent algorithm implementation (MADDPG, QMIX)
- [ ] Comparison with classical optimization methods (genetic algorithms)
- [ ] Automatic hyperparameter tuning with Optuna
- [ ] Transfer learning between different mine configurations

### **Analysis and Metrics**
- [ ] Interactive web dashboard for post-training analysis
- [ ] Data export to standard formats (CSV, JSON)
- [ ] Automatic statistical performance analysis
- [ ] Automatic optimization report generation

### **Industrial Validation**
- [ ] Calibration with real mining operation data
- [ ] Benchmarking against commercial FMS systems
- [ ] Case studies with different mine configurations
- [ ] Scalability validation for larger fleets

## 🔧 Advanced Customization

### **Modify Fleet Configuration:**
```python
# In fms_manager.py
self.trucks = [
    Truck(i, capacity=300, position=start_node, efficiency=0.90) 
    for i in range(8)  # Change number and characteristics
]
```

### **Add New Shovels:**
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

### **Customize Reward Function:**
```python
# In mining_env.py, _calculate_reward() method
def _calculate_reward(self) -> float:
    # Customize weights and penalties
    production = delta_waste + 3.0 * delta_mineral  # Higher weight for ore
    efficiency_bonus = working * 0.5  # Bonus for utilization
    queue_penalty = queue_total * 0.2  # Higher penalty for queues
    return production + efficiency_bonus - queue_penalty
```

## 📝 Technical Notes

### **Simulator Architecture**
- **Tick-based system**: Discrete updates (1 tick ≈ 0.1 simulated hours)
- **Event-driven**: Well-defined states and transitions for each equipment
- **Modular design**: Easy extension and modification of components
- **Performance optimized**: Headless mode for intensive RL training

### **RL Considerations**
- **Automatic normalization**: Normalized observations using `VecNormalize`
- **Episode management**: Termination by production target (400t) or step limit (800)
- **Reward engineering**: Balance between throughput, efficiency and deadlock prevention

---

**FMS Simulator developed as a research platform for mining Fleet Management Systems with complete Reinforcement Learning capabilities.**

*Objective: Provide a robust platform for the development and evaluation of intelligent assignment algorithms in mining operations, combining realistic simulation with advanced AI techniques.*
