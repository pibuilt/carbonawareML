import requests
from utils.logger import get_logger
import yaml

logger = get_logger("CarbonIntensity")

def load_config():
    with open("configs/config.yaml", "r") as f:
        return yaml.safe_load(f)

def get_carbon_intensity():
    cfg = load_config()
    provider = cfg['carbon_api']['provider']
    api_key = cfg['carbon_api']['api_key']
    region = cfg['carbon_api']['region']

    if provider == "electricitymap":
        url = f"https://api.electricitymap.org/v3/carbon-intensity/latest?zone={region}"
        headers = {"auth-token": api_key}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            carbon_intensity = r.json().get("carbonIntensity", None)
            logger.info(f"Current carbon intensity in {region}: {carbon_intensity} gCO2eq/kWh")
            return carbon_intensity
        else:
            logger.error(f"Failed to fetch carbon intensity: {r.text}")
            return None
    elif provider == "mock":
        # Mock implementation for testing without real API
        import random
        import datetime
        
        # Generate realistic carbon intensity values based on time of day
        now = datetime.datetime.now()
        hour = now.hour
        
        # Lower carbon intensity during off-peak hours (night/early morning)
        if 0 <= hour <= 6:
            base_intensity = 150 + random.randint(-30, 30)  # Low
        elif 7 <= hour <= 9 or 18 <= hour <= 22:
            base_intensity = 350 + random.randint(-50, 50)  # High (peak hours)
        else:
            base_intensity = 250 + random.randint(-40, 40)  # Medium
            
        logger.info(f"Mock carbon intensity in {region}: {base_intensity} gCO2eq/kWh (simulated)")
        return base_intensity
    else:
        logger.error("Unknown provider")
        return None

if __name__ == "__main__":
    get_carbon_intensity()