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
        # Pose: 33 landmarks
        for i in range(33):
            if 'pose' in landmarks and len(landmarks['pose']) > i:
                lm = landmarks['pose'][i]
                features.extend([lm['x'], lm['y']])
            else:
                features.extend([0.0, 0.0])
        # Left hand: 21 landmarks
        for i in range(21):
            if 'left_hand' in landmarks and len(landmarks['left_hand']) > i:
                lm = landmarks['left_hand'][i]
                features.extend([lm['x'], lm['y']])
            else:
                features.extend([0.0, 0.0])
        # Right hand: 21 landmarks
        for i in range(21):
            if 'right_hand' in landmarks and len(landmarks['right_hand']) > i:
                lm = landmarks['right_hand'][i]
                features.extend([lm['x'], lm['y']])
            else:
                features.extend([0.0, 0.0])
        return np.array(features).reshape(1, -1)



    def train(self, X, y):
        print(f"[Classifier] Training on {X.shape} samples, labels: {np.unique(y)}")
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

    def predict(self, landmarks):
        if self.model is None or self.scaler is None:
            print("[Classifier] Model or scaler not loaded.")
            return "NO_GESTURE"
        
        features = self.preprocess_landmarks(landmarks)
        if features.size == 0:
            return "NO_GESTURE"
            
        features_scaled = self.scaler.transform(features)
        
        # Get probabilities instead of just class prediction
        probas = self.model.predict_proba(features_scaled)[0]
        max_proba = probas.max()
        
        # Only predict if confidence is high enough
        if max_proba > 0.7:  # Adjust threshold as needed
            pred = self.model.classes_[probas.argmax()]
            print(f"[Classifier] Prediction: {pred} with confidence {max_proba:.2f}")
            return pred
        else:
            print(f"[Classifier] Low confidence: {max_proba:.2f}, returning NO_GESTURE")
            return "NO_GESTURE"


    def save_model(self, model_path):
        if self.model is None or self.scaler is None:
            raise ValueError("No trained model or scaler to save")
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump((self.model, self.scaler), model_path)
        print(f"[Classifier] Model and scaler saved to {model_path}")

    def load_model(self, model_path):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        self.model, self.scaler = joblib.load(model_path)
        print(f"[Classifier] Model and scaler loaded from {model_path}")

    def is_trained(self):
        return self.model is not None and self.scaler is not None
