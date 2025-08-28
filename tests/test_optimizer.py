import unittest
from optimization.optimizer import optimize_training_config
from data_pipeline.carbon_intensity import load_config

class TestOptimizer(unittest.TestCase):
    def test_optimizer_config(self):
        cfg = load_config()
        ci = 500  # Simulate high carbon intensity
        new_cfg = optimize_training_config(ci, cfg)
        self.assertIn('batch_size', new_cfg)
        self.assertIn('use_mixed_precision', new_cfg)

if __name__ == "__main__":
    unittest.main()