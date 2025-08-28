from utils.logger import get_logger

logger = get_logger("Optimizer")

def optimize_training_config(ci, cfg):
    # Simple logic: If carbon intensity is high, use more efficient settings
    if ci is None:
        return cfg['model']

    new_cfg = cfg['model'].copy()
    if ci > cfg['train']['max_carbon_intensity']:
        logger.info("High carbon intensity: enabling aggressive optimization")
        new_cfg['use_mixed_precision'] = True
        new_cfg['batch_size'] = max(32, new_cfg['batch_size'] // 2)
    elif ci < cfg['train']['min_carbon_intensity']:
        logger.info("Low carbon intensity: using default settings")
    else:
        logger.info("Moderate carbon intensity: moderate optimization")
        new_cfg['batch_size'] = int(new_cfg['batch_size'] * 0.75)
    return new_cfg