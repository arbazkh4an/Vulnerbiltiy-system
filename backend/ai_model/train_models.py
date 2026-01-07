"""
Script to train and compare different ML models for severity prediction
Run this to generate model files before deployment
"""

from severity_predictor import SeverityPredictor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_all_models():
    """Train all available model types"""
    model_types = ['random_forest', 'logistic_regression', 'naive_bayes']
    
    for model_type in model_types:
        logger.info(f"\n{'='*50}")
        logger.info(f"Training {model_type} model...")
        logger.info(f"{'='*50}\n")
        
        predictor = SeverityPredictor(model_type=model_type)
        
        # Test prediction
        test_vuln = {
            'name': 'SQL Injection',
            'description': 'Database access bypass through unsanitized input',
            'type': 'Injection',
            'cvss_score': 9.8
        }
        
        result = predictor.predict_severity(test_vuln)
        logger.info(f"Test prediction: {result}")
    
    logger.info("\n" + "="*50)
    logger.info("All models trained successfully!")
    logger.info("="*50)

if __name__ == '__main__':
    train_all_models()
