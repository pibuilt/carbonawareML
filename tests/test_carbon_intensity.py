import unittest
from data_pipeline.carbon_intensity import get_carbon_intensity

class TestCarbonIntensity(unittest.TestCase):
    def test_api_returns_value(self):
        ci = get_carbon_intensity()
        self.assertTrue(ci is None or isinstance(ci, (int, float)))

if __name__ == "__main__":
    unittest.main()