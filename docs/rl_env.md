# MiningEnv

`MiningEnv` is a Gymnasium-compatible environment wrapping the `FMSManager` simulation.

## Observation Space
The observation vector has 115 continuous values:
- Global status: tick, total production and number of available trucks
- Fixed equipment: queue length and busy flag for crusher, dump and each shovel
- Truck state: task id, load ratio, efficiency and distances for each truck
- Spatial aggregates: average distances and fleet utilisation statistics

Observations are normalised automatically using `VecNormalize` during training and evaluation.

## Action Space
A discrete action chooses among nine high level commands:
0. No-op
1-6. Send an available empty truck to the corresponding shovel
7. Send a loaded truck to the crusher
8. Send a loaded truck to the dump


## Reward
The reward is based on incremental production with efficiency bonuses and several penalties:
```
reward = (delta_waste + 2 * delta_mineral)
         + fleet_utilisation
         - 0.1 * queue_penalty
         - 0.5 * delta_hang_time
         - 2.0 * delta_mineral_lost
         - 1.0 * delta_waste_in_crusher
```
This favours mineral production, keeps the fleet working and penalises idle shovels or incorrect dumping of material.

## Episode Termination
Episodes end when either a production target or a step limit is reached. By default the environment terminates after accumulating **400t** of total throughput or **800** steps, whichever happens first. These values can be customised via the `max_steps` and `target_production` parameters when creating the environment.
