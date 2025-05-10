import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

class GestureClassifier:
    def __init__(self, model_path=None):
        self.model = None
        self.scaler = None
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            
            self.model = MLPClassifier(
                hidden_layer_sizes=(100, 50),
                activation='relu',
                solver='adam',
                max_iter=1000,
                random_state=42
            )
            self.scaler = StandardScaler()
    
    def preprocess_landmarks(self, landmarks):
        
        features = []
        
        # Extract pose landmarks if available (using only x,y as mentioned in the paper)
        if 'pose' in landmarks:
            for lm in landmarks['pose']:
                features.extend([lm['x'], lm['y']])
        
        # Extract hand landmarks if available
        for hand in ['left_hand', 'right_hand']:
            if hand in landmarks:
                for lm in landmarks[hand]:
                    features.extend([lm['x'], lm['y']])
        
        return np.array(features).reshape(1, -1)
    
    def train(self, X, y):
        """Train the classifier with landmark data"""
        # Scale the features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train the model
        self.model.fit(X_scaled, y)
        
    def predict(self, landmarks):
        
        if self.model is None:
            raise ValueError("Model not trained or loaded")
            
        
        features = self.preprocess_landmarks(landmarks)
        
        
        if features.size == 0 or features.shape[1] == 0:
            return "NO_GESTURE"
        
        # Scale the features
        if self.scaler is None:
            self.scaler = StandardScaler()
            self.scaler.fit(features)
            
        features_scaled = self.scaler.transform(features)
        
        # Make prediction
        return self.model.predict(features_scaled)[0]
    
    def save_model(self, model_path):
        """Save the trained model to disk"""
        if self.model is None:
            raise ValueError("No trained model to save")
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save the model and scaler
        joblib.dump((self.model, self.scaler), model_path)
        
    def load_model(self, model_path):
        """Load a trained model from disk"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
            
        # Load the model and scaler
        self.model, self.scaler = joblib.load(model_path)
