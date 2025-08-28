"""
Carbon emissions calculator for ML training.
Combines energy consumption data with grid carbon intensity to calculate accurate carbon footprint.
"""

import time
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from utils.logger import get_logger
from utils.energy_monitor import EnergyTracker, EnergyMonitor
from data_pipeline.carbon_intensity import get_carbon_intensity, load_config

logger = get_logger("CarbonCalculator")

@dataclass
class CarbonFootprint:
    """Carbon footprint calculation result."""
    total_co2_grams: float
    total_co2_kg: float
    energy_kwh: float
    avg_carbon_intensity: float
    duration_hours: float
    cost_estimate_usd: Optional[float] = None
    
    def __str__(self) -> str:
        return (f"Carbon Footprint: {self.total_co2_grams:.2f}g CO2 "
                f"({self.total_co2_kg:.6f}kg) from {self.energy_kwh:.6f}kWh "
                f"over {self.duration_hours:.2f}h")

class CarbonCalculator:
    """Calculate carbon footprint of ML training sessions."""
    
    def __init__(self):
        """Initialize carbon calculator."""
        self.config = load_config()
        self.region = self.config['carbon_api']['region']
        
        # Carbon intensity cache to avoid excessive API calls
        self.carbon_intensity_cache = {}
        self.cache_duration = 300  # 5 minutes
        
        # Electricity cost estimates (USD per kWh) by region
        self.electricity_costs = {
            'IN-SO': 0.08,    # India South
            'US-CA': 0.20,    # California
            'DE': 0.30,       # Germany
            'FR': 0.18,       # France
            'GB': 0.25,       # UK
            'CN': 0.08,       # China
            'JP': 0.26,       # Japan
            'default': 0.15   # Global average
        }
        
        logger.info(f"Carbon calculator initialized for region: {self.region}")
    
    def get_carbon_intensity_cached(self, timestamp: Optional[float] = None) -> Optional[float]:
        """
        Get carbon intensity with caching to reduce API calls.
        
        Args:
            timestamp: Unix timestamp for historical data (not implemented yet)
            
        Returns:
            Carbon intensity in gCO2eq/kWh or None if unavailable
        """
        current_time = time.time()
        
        # Check cache
        if (self.region in self.carbon_intensity_cache and 
            current_time - self.carbon_intensity_cache[self.region]['timestamp'] < self.cache_duration):
            
            cached_value = self.carbon_intensity_cache[self.region]['value']
            logger.debug(f"Using cached carbon intensity: {cached_value} gCO2eq/kWh")
            return cached_value
        
        # Fetch new value
        carbon_intensity = get_carbon_intensity()
        
        if carbon_intensity is not None:
            # Update cache
            self.carbon_intensity_cache[self.region] = {
                'value': carbon_intensity,
                'timestamp': current_time
            }
            logger.debug(f"Fetched carbon intensity: {carbon_intensity} gCO2eq/kWh")
        else:
            logger.warning("Could not fetch carbon intensity")
        
        return carbon_intensity
    
    def calculate_footprint(self, energy_summary: Dict, 
                          carbon_intensity: Optional[float] = None) -> CarbonFootprint:
        """
        Calculate carbon footprint from energy consumption summary.
        
        Args:
            energy_summary: Energy consumption data from EnergyMonitor
            carbon_intensity: Carbon intensity override (gCO2eq/kWh)
            
        Returns:
            CarbonFootprint object with detailed calculations
        """
        if not energy_summary:
            logger.error("Empty energy summary provided")
            return CarbonFootprint(0, 0, 0, 0, 0)
        
        # Extract energy consumption
        energy_kwh = energy_summary.get('energy', {}).get('total_kwh', 0)
        duration_hours = energy_summary.get('duration_hours', 0)
        
        if energy_kwh <= 0:
            logger.warning("No energy consumption recorded")
            return CarbonFootprint(0, 0, 0, 0, duration_hours)
        
        # Get carbon intensity
        if carbon_intensity is None:
            carbon_intensity = self.get_carbon_intensity_cached()
        
        if carbon_intensity is None:
            # Fallback to regional averages (gCO2eq/kWh)
            regional_averages = {
                'IN-SO': 708,     # India South (coal heavy)
                'US-CA': 234,     # California (cleaner grid)
                'DE': 401,        # Germany
                'FR': 79,         # France (nuclear heavy)
                'GB': 233,        # UK
                'CN': 681,        # China
                'JP': 475,        # Japan
                'default': 475    # Global average
            }
            carbon_intensity = regional_averages.get(self.region, regional_averages['default'])
            logger.warning(f"Using fallback carbon intensity: {carbon_intensity} gCO2eq/kWh")
        
        # Calculate carbon emissions
        total_co2_grams = energy_kwh * carbon_intensity
        total_co2_kg = total_co2_grams / 1000
        
        # Estimate cost
        cost_per_kwh = self.electricity_costs.get(self.region, self.electricity_costs['default'])
        cost_estimate_usd = energy_kwh * cost_per_kwh
        
        footprint = CarbonFootprint(
            total_co2_grams=total_co2_grams,
            total_co2_kg=total_co2_kg,
            energy_kwh=energy_kwh,
            avg_carbon_intensity=carbon_intensity,
            duration_hours=duration_hours,
            cost_estimate_usd=cost_estimate_usd
        )
        
        logger.info(f"Carbon footprint calculated: {footprint}")
        return footprint
    
    def calculate_equivalent_emissions(self, co2_kg: float) -> Dict[str, str]:
        """
        Calculate equivalent emissions for context.
        
        Args:
            co2_kg: CO2 emissions in kilograms
            
        Returns:
            Dictionary with emission equivalents
        """
        equivalents = {}
        
        # Car driving (assuming 0.404 kg CO2/mile for average car)
        car_miles = co2_kg / 0.404
        equivalents['car_driving_miles'] = f"{car_miles:.2f} miles of driving"
        equivalents['car_driving_km'] = f"{car_miles * 1.60934:.2f} km of driving"
        
        # Smartphone charging (assuming 0.0084 kg CO2 per full charge)
        phone_charges = co2_kg / 0.0084
        equivalents['smartphone_charges'] = f"{phone_charges:.0f} smartphone charges"
        
        # LED light bulb hours (assuming 0.009 kg CO2/hour for 10W LED)
        led_hours = co2_kg / 0.009
        equivalents['led_bulb_hours'] = f"{led_hours:.1f} hours of LED light bulb"
        
        # Tree absorption (assuming 21.8 kg CO2/year per tree)
        tree_years = co2_kg / 21.8
        equivalents['tree_absorption'] = f"{tree_years:.4f} years of tree CO2 absorption"
        
        # Flight emissions (short haul ~0.255 kg CO2/km per passenger)
        flight_km = co2_kg / 0.255
        equivalents['flight_km'] = f"{flight_km:.2f} km of flight per passenger"
        
        return equivalents
    
    def get_carbon_budget_status(self, co2_kg: float, 
                                daily_budget_kg: Optional[float] = None) -> Dict:
        """
        Check carbon budget status.
        
        Args:
            co2_kg: Current emissions in kg
            daily_budget_kg: Daily carbon budget in kg CO2
            
        Returns:
            Budget status information
        """
        if daily_budget_kg is None:
            # Default daily carbon budget (based on 2°C target ~2.3 tons CO2/year per person)
            daily_budget_kg = 2300 / 365  # ~6.3 kg CO2/day
        
        percentage_used = (co2_kg / daily_budget_kg) * 100
        remaining_kg = max(0, daily_budget_kg - co2_kg)
        
        status = {
            'daily_budget_kg': daily_budget_kg,
            'used_kg': co2_kg,
            'remaining_kg': remaining_kg,
            'percentage_used': percentage_used,
            'budget_exceeded': co2_kg > daily_budget_kg
        }
        
        return status

class CarbonAwareTrainingSession:
    """Context manager for carbon-aware ML training with automatic tracking."""
    
    def __init__(self, session_name: str = "ML Training", 
                 sampling_interval: float = 1.0,
                 carbon_budget_kg: Optional[float] = None):
        """
        Initialize carbon-aware training session.
        
        Args:
            session_name: Name of the training session
            sampling_interval: Energy monitoring interval in seconds
            carbon_budget_kg: Carbon budget limit in kg CO2
        """
        self.session_name = session_name
        self.energy_tracker = EnergyTracker(sampling_interval)
        self.carbon_calculator = CarbonCalculator()
        self.carbon_budget_kg = carbon_budget_kg
        self.start_time = None
        self.footprint = None
        
    def __enter__(self):
        """Start the carbon-aware training session."""
        logger.info(f"Starting carbon-aware training session: {self.session_name}")
        self.start_time = time.time()
        
        # Check initial carbon intensity
        initial_ci = self.carbon_calculator.get_carbon_intensity_cached()
        if initial_ci:
            logger.info(f"Initial carbon intensity: {initial_ci} gCO2eq/kWh")
        
        return self.energy_tracker.__enter__()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End the session and calculate carbon footprint."""
        # Stop energy tracking
        self.energy_tracker.__exit__(exc_type, exc_val, exc_tb)
        
        # Calculate carbon footprint
        energy_summary = self.energy_tracker.get_summary()
        self.footprint = self.carbon_calculator.calculate_footprint(energy_summary)
        
        # Log results
        logger.info(f"Training session '{self.session_name}' completed")
        logger.info(f"Carbon footprint: {self.footprint}")
        
        # Check budget
        if self.carbon_budget_kg and self.footprint.total_co2_kg > self.carbon_budget_kg:
            logger.warning(f"Carbon budget exceeded! Used {self.footprint.total_co2_kg:.6f}kg, "
                         f"budget was {self.carbon_budget_kg:.6f}kg")
        
        return False
    
    def get_carbon_footprint(self) -> Optional[CarbonFootprint]:
        """Get the calculated carbon footprint."""
        return self.footprint
    
    def get_equivalents(self) -> Dict[str, str]:
        """Get emission equivalents for context."""
        if not self.footprint:
            return {}
        return self.carbon_calculator.calculate_equivalent_emissions(self.footprint.total_co2_kg)

if __name__ == "__main__":
    # Test the carbon calculator
    print("Testing Carbon Calculator...")
    
    # Simulate a training session
    with CarbonAwareTrainingSession("Test Training", sampling_interval=0.5) as monitor:
        print("Simulating training for 5 seconds...")
        
        # Simulate some work
        for i in range(5):
            time.sleep(1)
            # Simulate computation
            _ = sum(x**2 for x in range(10000))
            
            stats = monitor.get_realtime_stats()
            print(f"Step {i+1}: {stats.get('total_power_watts', 0):.1f}W")
    
    # Get carbon footprint
    calculator = CarbonAwareTrainingSession("Test Training")
    footprint = calculator.get_carbon_footprint()
    if footprint:
        print(f"\nCarbon Footprint: {footprint}")
        
        equivalents = calculator.get_equivalents()
        print("\nEquivalent Emissions:")
        for key, value in equivalents.items():
            print(f"  {key}: {value}")
    else:
        print("No footprint calculated yet.")
