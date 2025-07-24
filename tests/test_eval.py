import os
import shutil
import unittest

from single_agent.train_agents import train
from single_agent.eval import evaluate


class EvalTest(unittest.TestCase):
    def test_eval_runs(self):
        logdir = "test_logs"
        # Train a tiny model
        train(timesteps=2, logdir=logdir, render_mode="headless")
        model_path = os.path.join(logdir, "ppo_final.zip")
        self.assertTrue(os.path.exists(model_path))
        # Evaluate for one step
        evaluate(model_path, render_mode="headless", steps=1)
        shutil.rmtree(logdir)


if __name__ == "__main__":
    unittest.main()
