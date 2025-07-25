import unittest
import sys
from stable_baselines3.common.env_checker import check_env

sys.path.append(".")
from single_agent.rl.mining_env import MiningEnv


class EnvTest(unittest.TestCase):
    def test_env_valid(self):
        env = MiningEnv()
        check_env(env, warn=True)
        obs, info = env.reset()
        self.assertIsInstance(obs, dict)
        for key, space in env.observation_space.spaces.items():
            self.assertIn(key, obs)
            self.assertEqual(obs[key].shape, space.shape)
        env.close()

    def test_env_terminates(self):
        env = MiningEnv(max_steps=5)
        env.reset()
        done = False
        for _ in range(10):
            _, _, terminated, truncated, _ = env.step(env.action_space.sample())
            if terminated or truncated:
                done = True
                break
        env.close()
        self.assertTrue(done)


if __name__ == "__main__":
    unittest.main()
