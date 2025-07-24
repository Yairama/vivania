import os
import shutil
import unittest

from multi_agent.ma_train import train
from multi_agent.ma_eval import evaluate

class MultiAgentPipelineTest(unittest.TestCase):
    def test_train_headless(self):
        logdir = "ma_test_logs_headless"
        train(num_iters=1, logdir=logdir, render_mode="headless")
        ckpt = os.path.join(logdir, "checkpoint_000001")
        self.assertTrue(os.path.exists(ckpt))
        shutil.rmtree(logdir)

    def test_train_visual_and_eval(self):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        logdir = "ma_test_logs_visual"
        train(num_iters=1, logdir=logdir, render_mode="visual")
        ckpt_dir = os.path.join(logdir, "checkpoint_000001")
        ckpt_file = os.path.join(ckpt_dir, "checkpoint-000001")
        self.assertTrue(os.path.exists(ckpt_file))
        evaluate(ckpt_file, render_mode="headless", steps=1)
        evaluate(ckpt_file, render_mode="visual", steps=1)
        shutil.rmtree(logdir)


if __name__ == "__main__":
    unittest.main()
