import unittest
from stable_baselines3.common.env_checker import check_env
from rl.mining_env import MiningEnv

class EnvTest(unittest.TestCase):
    def test_env_valid(self):
        env = MiningEnv()
        check_env(env, warn=True)
        obs, info = env.reset()
        self.assertEqual(obs.shape[0], env.observation_space.shape[0])
        env.close()

if __name__ == "__main__":
    unittest.main()
