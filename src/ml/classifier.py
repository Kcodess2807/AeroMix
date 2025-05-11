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
        # Extract pose landmarks if available (using only x, y)
        if 'pose' in landmarks:
            for lm in landmarks['pose']:
                features.extend([lm['x'], lm['y']])
        # Extract hand landmarks if available
        for hand in ['left_hand', 'right_hand']:
            if hand in landmarks:
                for lm in landmarks[hand]:
                    features.extend([lm['x'], lm['y']])
        features = np.array(features).reshape(1, -1)
        print(f"[Classifier] Preprocessed features: {features.shape} {features}")
        return features

    def train(self, X, y):
        print(f"[Classifier] Training on {X.shape} samples, labels: {np.unique(y)}")
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

    def predict(self, landmarks):
        if self.model is None or self.scaler is None:
            print("[Classifier] Model or scaler not loaded.")
            return "NO_GESTURE"
        features = self.preprocess_landmarks(landmarks)
        if features.size == 0 or features.shape[1] == 0:
            print("[Classifier] Empty features, returning NO_GESTURE.")
            return "NO_GESTURE"
        try:
            features_scaled = self.scaler.transform(features)
        except Exception as e:
            print(f"[Classifier] Scaler transform failed: {e}")
            return "NO_GESTURE"
        pred = self.model.predict(features_scaled)[0]
        print(f"[Classifier] Model prediction: {pred}")
        return pred

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
