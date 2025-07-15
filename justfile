set shell := ["pwsh.exe", "-c"]

run:
    python.exe .\train_agents.py --timesteps 1000000

continue:
    python.exe .\train_agents.py --timesteps 1000000 --resume-from .\training_logs\checkpoints
    
evaluate:
    python.exe .\eval.py --model-path .\training_logs\ppo_final.zip --render-mode visual --steps 10000