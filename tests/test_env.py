import unittest
import sys
from stable_baselines3.common.env_checker import check_env

sys.path.append(".")
from rl.mining_env import MiningEnv


class EnvTest(unittest.TestCase):
    def test_env_valid(self):
        env = MiningEnv()
        check_env(env, warn=True)
        obs, info = env.reset()
        self.assertEqual(obs.shape[0], env.observation_space.shape[0])
        env.close()

    def test_env_terminates(self):
        env = MiningEnv(max_steps=5, target_production=10)
        env.reset()
        done = False
        for _ in range(10):
            _, _, terminated, truncated, _ = env.step(env.action_space.sample())
            if terminated or truncated:
                done = True
                break
        env.close()
        self.assertTrue(done)

    def test_info_metrics(self):
        env = MiningEnv(max_steps=1)
        _, info = env.reset()
        self.assertIn("action_mask", info)
        _, _, _, _, info = env.step(0)
        self.assertIn("hang_time", info)
        self.assertIn("ore_lost", info)
        self.assertIn("waste_to_crusher", info)
        env.close()


if __name__ == "__main__":
    unittest.main()
