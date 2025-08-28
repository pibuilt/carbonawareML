import yaml
from scheduler.scheduler import schedule_training
from data_pipeline.carbon_intensity import get_carbon_intensity, load_config
from optimization.optimizer import optimize_training_config
from utils.logger import get_logger
from utils.carbon_calculator import CarbonAwareTrainingSession

from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report

logger = get_logger("ML_Engine")

def main():
    logger.info("Starting carbon-aware ML training...")
    cfg = load_config()
    can_train = schedule_training()
    if not can_train:
        logger.info("Training postponed due to high carbon intensity or outside allowed time.")
        return

    ci = get_carbon_intensity()
    model_cfg = optimize_training_config(ci, cfg)
    logger.info(f"Training config: {model_cfg}")

    # Use carbon-aware training session with energy tracking
    with CarbonAwareTrainingSession("ML Engine Training", sampling_interval=1.0) as monitor:
        # Example: Use sklearn MLP on digits dataset
        X, y = load_digits(return_X_y=True)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        clf = MLPClassifier(
            hidden_layer_sizes=(64, 32),
            max_iter=model_cfg['epochs'],
            batch_size=model_cfg['batch_size'],
            verbose=True
        )
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        logger.info("\n" + classification_report(y_test, y_pred))
    
    # Get carbon footprint from the training session
    session = CarbonAwareTrainingSession("ML Engine Training")
    footprint = session.get_carbon_footprint()
    if footprint:
        logger.info(f"Carbon footprint: {footprint}")
        
        # Log equivalents for context
        equivalents = session.get_equivalents()
        logger.info("Environmental impact equivalents:")
        for key, value in equivalents.items():
            logger.info(f"  {key}: {value}")
    else:
        logger.warning("Could not calculate carbon footprint")

if __name__ == "__main__":
    main()