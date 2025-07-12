# MiningEnv

`MiningEnv` is a Gymnasium-compatible environment wrapping the `FMSManager` simulation.

## Observation Space
The observation vector has 54 continuous values:
- Global status: tick, total production and number of available trucks
- Fixed equipment: queue length and busy flag for crusher, dump and each shovel
- Truck state: task id, load ratio, efficiency and distances for each truck
- Spatial aggregates: average distances and fleet utilisation statistics

Values are normalised to `[0,1]` using running statistics collected during training.

## Action Space
A discrete action chooses among nine high level commands:
0. No-op
1-6. Send an available empty truck to the corresponding shovel
7. Send a loaded truck to the crusher
8. Send a loaded truck to the dump
Invalid actions are masked via the `action_mask` entry in `info`.

## Reward
The reward is based on incremental production with efficiency bonuses and queue penalties:
```
reward = (delta_waste + 2 * delta_mineral) + fleet_utilisation - 0.1 * queue_penalty
```
This favours mineral production and keeps the fleet working while discouraging long queues.
