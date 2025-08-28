import unittest
from unittest.mock import patch, MagicMock
import time
from utils.energy_monitor import EnergyMonitor, EnergyTracker

class TestEnergyMonitor(unittest.TestCase):
    def test_energy_monitor_initialization(self):
        """Test energy monitor can be initialized."""
        monitor = EnergyMonitor(sampling_interval=0.1)
        self.assertIsNotNone(monitor)
        self.assertEqual(monitor.sampling_interval, 0.1)
        self.assertFalse(monitor.monitoring)
    
    def test_energy_tracker_context_manager(self):
        """Test energy tracker context manager."""
        with EnergyTracker(sampling_interval=0.1) as tracker:
            self.assertIsNotNone(tracker)
            time.sleep(0.5)  # Brief monitoring period
        
        summary = tracker.get_summary()
        self.assertIn('duration_seconds', summary)
        self.assertIn('energy', summary)
        self.assertIn('power', summary)
    
    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_count')
    def test_cpu_power_estimation(self, mock_cpu_count, mock_cpu_percent):
        """Test CPU power estimation."""
        mock_cpu_count.return_value = 4
        mock_cpu_percent.return_value = 50.0
        
        monitor = EnergyMonitor()
        power, util = monitor._get_cpu_power()
        
        self.assertIsInstance(power, float)
        self.assertIsInstance(util, float)
        self.assertGreaterEqual(power, 0)
        self.assertEqual(util, 50.0)

if __name__ == "__main__":
    unittest.main()
