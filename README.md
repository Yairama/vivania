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

## 🚀 Related Projects

This repository is part of a comprehensive suite of mining-focused and AI/ML projects. Below are the key repositories developed by [@Yairama](https://github.com/Yairama):

### 🏭 Mining & Industrial Systems

#### [SAM-Rock-Fragmentation](https://github.com/Yairama/SAM-Rock-Fragmentation) ⭐ 33 stars
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://github.com/Yairama/SAM-Rock-Fragmentation)
[![Mining](https://img.shields.io/badge/Mining-⛏️-brown)](https://github.com/Yairama/SAM-Rock-Fragmentation)
[![Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue)](https://github.com/Yairama/SAM-Rock-Fragmentation)

**Advanced Rock Fragmentation Analysis using MetaAI's Segment Anything Model**
- Implementation of cutting-edge computer vision for mining blast analysis
- Automated P80 fragmentation calculation from blast imagery
- Integration of state-of-the-art AI models for industrial applications

#### [3D-Fleet-Management-System](https://github.com/Yairama/3D-Fleet-management-system)
[![Java](https://img.shields.io/badge/Java-ED8B00?style=flat&logo=openjdk&logoColor=white)](https://github.com/Yairama/3D-Fleet-management-system)
[![OpenGL](https://img.shields.io/badge/OpenGL-5586A4?style=flat&logo=opengl&logoColor=white)](https://github.com/Yairama/3D-Fleet-management-system)
[![LWJGL](https://img.shields.io/badge/LWJGL-3.3.1-orange)](https://github.com/Yairama/3D-Fleet-management-system)

**3D Mining Operations Visualizer**
- Real-time 3D visualization of mining fleet operations
- Built with Java and LWJGL using OpenGL backend
- Advanced rendering pipeline for mining equipment simulation

#### [vivania_env](https://github.com/Yairama/vivania_env) | [vivania_learn](https://github.com/Yairama/vivania_learn)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://github.com/Yairama/vivania_env)
[![RL](https://img.shields.io/badge/Reinforcement%20Learning-FF6B6B)](https://github.com/Yairama/vivania_env)
[![AI](https://img.shields.io/badge/AI-Enhanced%20Learning-green)](https://github.com/Yairama/vivania_learn)

**AI-Enhanced Mining Fleet Management Environments**
- Specialized RL environments for mining optimization
- Deep learning agent training for fleet coordination
- Advanced AI algorithms for mining operations

### 🤖 Machine Learning & AI

#### [machine_learning_for_mining_industry](https://github.com/Yairama/machine_learning_for_mining_industry)
[![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat&logo=jupyter&logoColor=white)](https://github.com/Yairama/machine_learning_for_mining_industry)
[![ML](https://img.shields.io/badge/Machine%20Learning-4285F4)](https://github.com/Yairama/machine_learning_for_mining_industry)

**Comprehensive ML Applications for Mining Industry**
- Collection of machine learning models and algorithms
- Industry-specific applications and case studies
- Jupyter notebooks with practical implementations

#### [Geospatial-Interpolation](https://github.com/Yairama/Geospatial-Interpolation)
[![Deep Learning](https://img.shields.io/badge/Deep%20Learning-FF4500)](https://github.com/Yairama/Geospatial-Interpolation)
[![Geology](https://img.shields.io/badge/Geology-8B4513)](https://github.com/Yairama/Geospatial-Interpolation)

**Advanced Geospatial Data Interpolation for Ore Bodies**
- Neural network-based interpolation techniques
- Simulated ore body data processing
- Advanced geological modeling algorithms

#### [alpaca-miner](https://github.com/Yairama/alpaca-miner)
[![LLM](https://img.shields.io/badge/LLM-Fine%20Tuning-purple)](https://github.com/Yairama/alpaca-miner)
[![Alpaca](https://img.shields.io/badge/Alpaca-Model-yellow)](https://github.com/Yairama/alpaca-miner)

**Specialized Language Model for Mining Industry**
- Fine-tuning of Alpaca LLM with mining-specific datasets
- Domain-specific natural language processing
- AI assistant for mining operations

### 🎮 Graphics Engines & Game Development

#### [Yamete-Kudasai-Engine](https://github.com/Yairama/Yamete-Kudasai-Engine)
[![Rust](https://img.shields.io/badge/Rust-000000?style=flat&logo=rust&logoColor=white)](https://github.com/Yairama/Yamete-Kudasai-Engine)
[![Bevy](https://img.shields.io/badge/Bevy-232326?style=flat&logo=bevy&logoColor=white)](https://github.com/Yairama/Yamete-Kudasai-Engine)
[![MIT](https://img.shields.io/badge/License-MIT-green)](https://github.com/Yairama/Yamete-Kudasai-Engine)

**Modern Graphics Engine Built with Rust & Bevy**
- High-performance graphics rendering pipeline
- ECS-based architecture for optimal performance
- Cross-platform graphics engine development

#### [voxel_engine](https://github.com/Yairama/voxel_engine)
[![Rust](https://img.shields.io/badge/Rust-000000?style=flat&logo=rust&logoColor=white)](https://github.com/Yairama/voxel_engine)
[![Voxel](https://img.shields.io/badge/Voxel%20Engine-3D-blue)](https://github.com/Yairama/voxel_engine)

**Voxel-Based 3D Engine**
- Block-mesh-rs library integration
- Efficient voxel rendering algorithms
- Minecraft-style world generation

#### [breakout_2d](https://github.com/Yairama/breakout_2d) | [pick_the_apple](https://github.com/Yairama/pick_the_apple)
[![Rust](https://img.shields.io/badge/Rust-000000?style=flat&logo=rust&logoColor=white)](https://github.com/Yairama/breakout_2d)
[![GDScript](https://img.shields.io/badge/GDScript-478CBF?style=flat&logo=godot-engine&logoColor=white)](https://github.com/Yairama/pick_the_apple)

**Game Development Learning Projects**
- Classic game implementations
- Exploring different game engines (Bevy, Godot)
- Educational game development resources

### 💼 Industrial Applications

#### [sso_platform](https://github.com/Yairama/sso_platform)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)](https://github.com/Yairama/sso_platform)
[![Safety](https://img.shields.io/badge/Safety-Platform-red)](https://github.com/Yairama/sso_platform)

**Occupational Health and Safety Platform**
- Complete safety management system
- Critical controls mapping
- Mining industry safety compliance

#### [EPPHelper](https://github.com/Yairama/EPPHelper)
[![Kotlin](https://img.shields.io/badge/Kotlin-0095D5?style=flat&logo=kotlin&logoColor=white)](https://github.com/Yairama/EPPHelper)
[![Android](https://img.shields.io/badge/Android-3DDC84?style=flat&logo=android&logoColor=white)](https://github.com/Yairama/EPPHelper)

**Personal Protective Equipment Registration App**
- Mobile application for PPE management
- Safety compliance tracking
- Mining industry specialized tools

### 🔬 Research & Algorithms

#### [casos_de_exito_mineria](https://github.com/Yairama/casos_de_exito_mineria)
[![Research](https://img.shields.io/badge/Research-Documentation-orange)](https://github.com/Yairama/casos_de_exito_mineria)

**Machine Learning Success Cases in Mining (2020-2025)**
- Comprehensive documentation of ML applications
- Industry case studies and analysis
- Research compilation and insights

#### [NicholasMethod](https://github.com/Yairama/NicholasMethod)
[![Java](https://img.shields.io/badge/Java-ED8B00?style=flat&logo=openjdk&logoColor=white)](https://github.com/Yairama/NicholasMethod)
[![MIT](https://img.shields.io/badge/License-MIT-green)](https://github.com/Yairama/NicholasMethod)

**Mining Exploitation Method Selection Tool**
- Implementation of Nicolas method algorithm
- Java Swing GUI application
- Mining engineering decision support

#### [pyminerpit](https://github.com/Yairama/pyminerpit) | [mining-deposit-simulation](https://github.com/Yairama/mining-deposit-simulation)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://github.com/Yairama/pyminerpit)
[![Algorithms](https://img.shields.io/badge/Algorithms-Mining-brown)](https://github.com/Yairama/pyminerpit)

**Mining Algorithms and Simulation Tools**
- Collection of mining-specific algorithms
- Deposit simulation and modeling
- Educational mining engineering resources

### 🌐 Web & Portfolio

#### [yairama.github.io](https://github.com/Yairama/yairama.github.io) | [portfolio](https://github.com/Yairama/portfolio)
[![CSS](https://img.shields.io/badge/CSS-1572B6?style=flat&logo=css3&logoColor=white)](https://github.com/Yairama/portfolio)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-222222?style=flat&logo=github&logoColor=white)](https://github.com/Yairama/yairama.github.io)

**Personal Portfolio and Web Presence**
- GitHub Pages hosted portfolio
- Professional project showcase
- Contact and professional information

---

**FMS Simulator developed as a research platform for mining Fleet Management Systems with complete Reinforcement Learning capabilities.**

*Objective: Provide a robust platform for the development and evaluation of intelligent assignment algorithms in mining operations, combining realistic simulation with advanced AI techniques.*
