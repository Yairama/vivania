import os
import shutil
import unittest

from train_agents import train


class ResumeTest(unittest.TestCase):
    def test_resume_from_model(self):
        logdir = "test_logs"
        train(timesteps=2, logdir=logdir, render_mode="headless")
        model_path = os.path.join(logdir, "ppo_final.zip")
        self.assertTrue(os.path.exists(model_path))
        train(timesteps=1, logdir=logdir, render_mode="headless", resume_from=model_path)
        shutil.rmtree(logdir)


if __name__ == "__main__":
    unittest.main()
