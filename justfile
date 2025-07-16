set shell := ["pwsh.exe", "-c"]

run:
    python.exe .\train_agents.py --timesteps 1000000

runv:
    python.exe .\train_agents.py --timesteps 1000000 --mode visual

continue:
    python.exe .\train_agents.py --timesteps 1000000 --resume-from .\training_logs\checkpoints
    
eval:
    python.exe .\eval.py --from .\training_logs\checkpoints\ppo_120000_steps.zip --mode visual --steps 10000