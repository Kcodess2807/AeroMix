import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os



class GestureClassifier:
    def __init__(self, model_path=None):
        self.model=None
        self.scaler=None

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)

        else:
            self.model=MLPClassifier(
                hidden_layer_sizes=(100, 50),
                activation='relu',
                solver='adam',
                max_iter=500,
                random_state=42,
                )
    
    def preprocess_landmarks(self, landmarks):
        """Convert landmarks to a flat feature vector"""
        features = []
        
        # Extract pose landmarks if available
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
        #traning the classifier model
        #scaling up thh features

        X_scaled=self.scaler.fit_transform(X)

        #traning the model
        self.model.fit(X_scaled, y)
        print("Model trained successfully")

    def predict(self, landmarks):
        "gesture class ko predict krega from landmarks"
        if self.model is None:
            raise ValueError("Model not trained or loaded.")

        features=self.preprocess_landmarks(landmarks)

        #scaling the features
        features_scaled=self.self.scaler.transform(features)

        #prediciton
        return self.model.predict(features_scaled)
    
    def save_model(self, model_path):
        if self.model is None:
            raise ValueError("Model not trained or loaded.")
        
        #creating directory
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        #saving the model and scaler
        joblib.dump((self.model, self.scaler), model_path)
        print(f"Model saved to {model_path}")
    
    def load_model(self, model_path):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        self.model, self.scaler=joblib.load(model_path)
        print(f"Model loaded from {model_path}")



