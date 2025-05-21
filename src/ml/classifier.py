import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
import os
import math

class GestureClassifier:
    def __init__(self, model_path=None):
        self.model = None
        self.scaler = None
        self.gesture_name = None  # Add gesture_name for logging
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
            print(f"[Classifier] Model and scaler loaded from -> {model_path}")
            self.gesture_name = os.path.basename(model_path).replace('_model.pkl', '')
        else:
            print("[Classifier] No model loaded, will train from scratch.")

    def preprocess_landmarks(self, landmarks):
        """
        Extracting and normalizing hand gestures for gesture recognition
        focusing on normalized x, y coordinates and key distances for distinct gestures
        """
        print(f"[DEBUG] Preprocessing landmarks for gesture: {self.gesture_name}")
        print(f"[DEBUG] Landmarks received: {len(landmarks)} hands detected")

        if not landmarks:
            print("[DEBUG] No landmarks provided")
            return np.array([])
        
        # Use the first hand (MediaPipe returns a list of hands)
        hand_landmarks = landmarks[0]  # Take the first detected hand
        
        if not hand_landmarks or len(hand_landmarks) != 21:  # MediaPipe hand has 21 landmarks
            print(f"[DEBUG] Invalid hand landmarks: {len(hand_landmarks)} landmarks, expected 21")
            return np.array([])
        
        # Convert landmark objects to a dictionary format for easier access
        hand_landmarks_dict = [
            {"x": lm.x, "y": lm.y, "z": lm.z if hasattr(lm, 'z') else 0.0}
            for lm in hand_landmarks
        ]

        # Using wrist as the reference point
        wrist = hand_landmarks_dict[0]
        wrist_x, wrist_y = wrist["x"], wrist["y"]

        # Calculate bounding box for normalization
        x_values = [lm["x"] for lm in hand_landmarks_dict]
        y_values = [lm["y"] for lm in hand_landmarks_dict]
        x_range = max(0.001, max(x_values) - min(x_values))
        y_range = max(0.001, max(y_values) - min(y_values))
        
        features = []

        # Normalized x, y coordinates relative to wrist
        for lm in hand_landmarks_dict:
            norm_x = (lm["x"] - wrist_x) / x_range
            norm_y = (lm["y"] - wrist_y) / y_range
            features.extend([norm_x, norm_y])
        
        # Key distances: thumb tip to index tip, index tip to middle tip
        thumb_tip = hand_landmarks_dict[4]
        index_tip = hand_landmarks_dict[8]
        middle_tip = hand_landmarks_dict[12]
        distances = [
            np.sqrt((thumb_tip["x"] - index_tip["x"])**2 + (thumb_tip["y"] - index_tip["y"])**2) / x_range,
            np.sqrt((index_tip["x"] - middle_tip["x"])**2 + (index_tip["y"] - middle_tip["y"])**2) / x_range
        ]
        features.extend(distances)
        
        # Finger-to-wrist distances for curl detection
        for tip_idx in [4, 8, 12, 16, 20]:  # Thumb, index, middle, ring, pinky tips
            tip = hand_landmarks_dict[tip_idx]
            distance = np.sqrt((tip["x"] - wrist_x)**2 + (tip["y"] - wrist_y)**2) / x_range
            features.append(distance)
        
        features_array = np.array(features).reshape(1, -1)
        print(f"[DEBUG] Extracted features: {features_array}, shape: {features_array.shape}")
        return features_array

    def train(self, X, y):
        """Train the gesture classifier"""
        if X.size == 0 or len(y) == 0:
            print("[Classifier] Error: Empty training data")
            return False
        
        print(f"[Classifier] Training with {len(X)} samples, {len(np.unique(y))} classes")
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train MLP classifier
        self.model = MLPClassifier(
            hidden_layer_sizes=(100, 50),
            activation='relu',
            solver='adam',
            max_iter=1000,  # Increased for better convergence
            random_state=42,
            alpha=0.01  # L2 regularization
        )
        self.model.fit(X_scaled, y)
        
        print(f"[Classifier] Training complete. Model accuracy: {self.model.score(X_scaled, y):.4f}")
        return True

    def predict(self, features):
        """Predict gesture from landmarks"""
        if self.model is None or self.scaler is None:
            print("[Classifier] Model or scaler not loaded.")
            return "NO_GESTURE"
        
        if features.size == 0:
            return "NO_GESTURE"
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Get prediction probabilities
        probas = self.model.predict_proba(features_scaled)[0]
        max_proba = probas.max()
        
        # Only predict if confidence is high enough
        if max_proba > 0.7:  # Adjusted threshold
            pred = self.model.classes_[probas.argmax()]
            print(f"[Classifier] Prediction: {pred} with confidence {max_proba:.2f}")
            return pred
        else:
            print(f"[Classifier] Low confidence: {max_proba:.2f}, returning NO_GESTURE")
            return "NO_GESTURE"

    def save_model(self, model_path):
        """Save the trained model and scaler"""
        if self.model is None or self.scaler is None:
            print("[Classifier] Error: No trained model to save")
            return False
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"[Classifier] Model saved to {model_path}")
        return True

    def load_model(self, model_path):
        """Load a trained model and scaler"""
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            return True
        except Exception as e:
            print(f"[Classifier] Error loading model: {e}")
            return False