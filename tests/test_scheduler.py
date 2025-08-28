import unittest
from scheduler.scheduler import schedule_training

class TestScheduler(unittest.TestCase):
    def test_schedule_returns_bool(self):
        res = schedule_training()
        self.assertIsInstance(res, bool)

if __name__ == "__main__":
    unittest.main()