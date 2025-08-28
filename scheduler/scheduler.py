from data_pipeline.carbon_intensity import get_carbon_intensity, load_config
from utils.logger import get_logger

import datetime

logger = get_logger("Scheduler")

def schedule_training():
    cfg = load_config()
    earliest = cfg['train']['earliest_start_hour']
    latest = cfg['train']['latest_start_hour']
    min_intensity = cfg['train']['min_carbon_intensity']
    max_intensity = cfg['train']['max_carbon_intensity']

    now = datetime.datetime.now()
    current_hour = now.hour

    logger.info("Checking if current time is within the allowed window...")
    if not (earliest <= current_hour <= latest):
        logger.info(f"Current time {current_hour} not in allowed window ({earliest}-{latest}), will wait.")
        return False

    ci = get_carbon_intensity()
    if ci is None:
        logger.warning("Could not get carbon intensity, proceeding anyway.")
        return True
    elif ci < min_intensity:
        logger.info(f"Low carbon intensity ({ci}), optimal for training.")
        return True
    elif ci > max_intensity:
        logger.info(f"High carbon intensity ({ci}), not optimal. Consider waiting.")
        return False
    else:
        logger.info(f"Carbon intensity ({ci}) in acceptable range.")
        return True

if __name__ == "__main__":
    can_train = schedule_training()
    print(f"Can train now? {can_train}")