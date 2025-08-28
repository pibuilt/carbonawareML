import unittest
from unittest.mock import patch, MagicMock
from utils.carbon_calculator import CarbonCalculator, CarbonFootprint, CarbonAwareTrainingSession

class TestCarbonCalculator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = CarbonCalculator()
    
    def test_carbon_calculator_initialization(self):
        """Test carbon calculator initialization."""
        self.assertIsNotNone(self.calculator)
        self.assertIn('region', self.calculator.__dict__)
    
    def test_calculate_footprint(self):
        """Test carbon footprint calculation."""
        energy_summary = {
            'energy': {'total_kwh': 0.1},
            'duration_hours': 1.0
        }
        
        footprint = self.calculator.calculate_footprint(energy_summary, carbon_intensity=400)
        
        self.assertIsInstance(footprint, CarbonFootprint)
        self.assertEqual(footprint.energy_kwh, 0.1)
        self.assertEqual(footprint.avg_carbon_intensity, 400)
        self.assertEqual(footprint.total_co2_grams, 40.0)  # 0.1 kWh * 400 gCO2eq/kWh
    
    def test_calculate_equivalent_emissions(self):
        """Test emission equivalents calculation."""
        equivalents = self.calculator.calculate_equivalent_emissions(1.0)  # 1 kg CO2
        
        self.assertIn('car_driving_miles', equivalents)
        self.assertIn('smartphone_charges', equivalents)
        self.assertIn('tree_absorption', equivalents)
        
        # Check that values are reasonable
        self.assertIn('miles', equivalents['car_driving_miles'])
        self.assertIn('charges', equivalents['smartphone_charges'])
    
    def test_carbon_budget_status(self):
        """Test carbon budget status calculation."""
        status = self.calculator.get_carbon_budget_status(1.0, daily_budget_kg=5.0)
        
        self.assertEqual(status['daily_budget_kg'], 5.0)
        self.assertEqual(status['used_kg'], 1.0)
        self.assertEqual(status['remaining_kg'], 4.0)
        self.assertEqual(status['percentage_used'], 20.0)
        self.assertFalse(status['budget_exceeded'])

if __name__ == "__main__":
    unittest.main()
