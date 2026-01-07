"""
AI-Powered Severity Prediction Model
Uses machine learning to predict vulnerability severity
Implements: Logistic Regression, Random Forest, and Naive Bayes
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os
import logging

logger = logging.getLogger(__name__)

class SeverityPredictor:
    def __init__(self, model_type='random_forest'):
        """
        Initialize the severity predictor
        Args:
            model_type: 'random_forest', 'logistic_regression', or 'naive_bayes'
        """
        self.model_type = model_type
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.model = None
        self.is_trained = False
        
        # Try to load pre-trained model
        self.load_model()
        
        # If no model exists, train a new one
        if not self.is_trained:
            self.train_model()
    
    def train_model(self):
        """Train the ML model with sample vulnerability data"""
        logger.info(f"Training new {self.model_type} model...")
        
        # Training data: vulnerability descriptions and their severities
        # In production, this would be trained on a larger dataset
        training_data = [
            # Critical
            ("SQL injection allows database access bypass authentication", "critical"),
            ("Remote code execution vulnerability in authentication system", "critical"),
            ("Broken access control allows unauthorized admin access", "critical"),
            ("Authentication bypass through parameter manipulation", "critical"),
            ("Complete data exposure without authentication", "critical"),
            
            # High
            ("Cross-site scripting in user input fields", "high"),
            ("Insecure direct object reference exposes user data", "high"),
            ("Session fixation vulnerability in login process", "high"),
            ("XML external entity injection vulnerability", "high"),
            ("Server-side request forgery allows internal network access", "high"),
            
            # Medium
            ("Missing security headers allow clickjacking", "medium"),
            ("Weak password policy allows simple passwords", "medium"),
            ("Information disclosure in error messages", "medium"),
            ("Insufficient logging and monitoring", "medium"),
            ("Outdated software components with known vulnerabilities", "medium"),
            
            # Low
            ("Missing autocomplete attribute on forms", "low"),
            ("Directory listing enabled", "low"),
            ("Verbose error messages reveal software versions", "low"),
            ("Cache-control headers not properly configured", "low"),
            ("Missing secure flag on non-sensitive cookies", "low")
        ]
        
        descriptions = [item[0] for item in training_data]
        labels = [item[1] for item in training_data]
        
        # Convert text to numerical features
        X = self.vectorizer.fit_transform(descriptions)
        
        # Map severity to numerical values
        severity_map = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        y = np.array([severity_map[label] for label in labels])
        
        # Train the selected model
        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        elif self.model_type == 'logistic_regression':
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42
            )
        elif self.model_type == 'naive_bayes':
            self.model = MultinomialNB(alpha=1.0)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        self.model.fit(X, y)
        self.is_trained = True
        
        # Save the trained model
        self.save_model()
        
        logger.info(f"Model training completed. Type: {self.model_type}")
    
    def predict_severity(self, vulnerability):
        """
        Predict severity for a given vulnerability
        Args:
            vulnerability: dict with vulnerability details
        Returns:
            dict with predicted_severity and confidence
        """
        if not self.is_trained:
            logger.warning("Model not trained, using rule-based prediction")
            return self._rule_based_prediction(vulnerability)
        
        # Create feature text from vulnerability details
        feature_text = f"{vulnerability.get('name', '')} {vulnerability.get('description', '')} {vulnerability.get('type', '')}"
        
        # Transform to features
        X = self.vectorizer.transform([feature_text])
        
        # Get prediction and probability
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        # Map numerical prediction back to severity
        severity_reverse_map = {0: 'low', 1: 'medium', 2: 'high', 3: 'critical'}
        predicted_severity = severity_reverse_map[prediction]
        
        # Confidence is the probability of the predicted class
        confidence = probabilities[prediction] * 100
        
        return {
            'predicted_severity': predicted_severity,
            'confidence': round(confidence, 2)
        }
    
    def _rule_based_prediction(self, vulnerability):
        """Fallback rule-based prediction if ML model not available"""
        cvss_score = vulnerability.get('cvss_score', 0)
        
        if cvss_score >= 9.0:
            predicted_severity = 'critical'
            confidence = 95.0
        elif cvss_score >= 7.0:
            predicted_severity = 'high'
            confidence = 90.0
        elif cvss_score >= 4.0:
            predicted_severity = 'medium'
            confidence = 85.0
        else:
            predicted_severity = 'low'
            confidence = 80.0
        
        return {
            'predicted_severity': predicted_severity,
            'confidence': confidence
        }
    
    def save_model(self):
        """Save the trained model and vectorizer"""
        try:
            model_dir = 'ai_model/saved_models'
            os.makedirs(model_dir, exist_ok=True)
            
            model_path = os.path.join(model_dir, f'{self.model_type}_model.pkl')
            vectorizer_path = os.path.join(model_dir, 'vectorizer.pkl')
            
            joblib.dump(self.model, model_path)
            joblib.dump(self.vectorizer, vectorizer_path)
            
            logger.info(f"Model saved to {model_path}")
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
    
    def load_model(self):
        """Load a pre-trained model"""
        try:
            model_path = f'ai_model/saved_models/{self.model_type}_model.pkl'
            vectorizer_path = 'ai_model/saved_models/vectorizer.pkl'
            
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                self.model = joblib.load(model_path)
                self.vectorizer = joblib.load(vectorizer_path)
                self.is_trained = True
                logger.info(f"Model loaded from {model_path}")
            else:
                logger.info("No pre-trained model found")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
