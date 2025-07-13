set shell := ["pwsh.exe", "-c"]

run:
    python.exe .\train_agents.py --mode visual --timesteps 1000000

continue:
    python.exe .\train_agents.py --timesteps 1000000 --resume-from .\training_logs\checkpoints\ppo_20000_steps.zip
    