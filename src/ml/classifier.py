import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import os

class GestureClassifier:
    def __init__(self, model_path=None):
        self.model = None
        self.scaler = None
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
            print(f"[Classifier] Model and scaler loaded from {model_path}")
        else:
            print("[Classifier] No model loaded, will train from scratch.")

    def preprocess_landmarks(self, landmarks):
        """
        Extract and normalize hand landmarks with advanced feature engineering
        specifically designed for thumb up/down, three-finger yo-yo, and closed fist gestures
        """
        if not landmarks or (not landmarks["left_hand"] and not landmarks["right_hand"]):
            return np.array([])
        
        # Use the first available hand
        hand_landmarks = landmarks["left_hand"] if landmarks["left_hand"] else landmarks["right_hand"]
        
        if not hand_landmarks or len(hand_landmarks) < 21:  # MediaPipe hand has 21 landmarks
            return np.array([])
        
        # Calculate bounding box for normalization
        x_values = [lm["x"] for lm in hand_landmarks]
        y_values = [lm["y"] for lm in hand_landmarks]
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        
        # Avoid division by zero
        x_range = max(0.001, x_max - x_min)
        y_range = max(0.001, y_max - y_min)
        
        # Extract key landmarks for gesture recognition
        wrist = hand_landmarks[0]
        thumb_cmc = hand_landmarks[1]
        thumb_mcp = hand_landmarks[2]
        thumb_ip = hand_landmarks[3]
        thumb_tip = hand_landmarks[4]
        
        index_mcp = hand_landmarks[5]
        index_pip = hand_landmarks[6]
        index_dip = hand_landmarks[7]
        index_tip = hand_landmarks[8]
        
        middle_mcp = hand_landmarks[9]
        middle_pip = hand_landmarks[10]
        middle_dip = hand_landmarks[11]
        middle_tip = hand_landmarks[12]
        
        ring_mcp = hand_landmarks[13]
        ring_pip = hand_landmarks[14]
        ring_dip = hand_landmarks[15]
        ring_tip = hand_landmarks[16]
        
        pinky_mcp = hand_landmarks[17]
        pinky_pip = hand_landmarks[18]
        pinky_dip = hand_landmarks[19]
        pinky_tip = hand_landmarks[20]
        
        features = []
        
        # 1. Normalized coordinates for all landmarks
        for lm in hand_landmarks:
            norm_x = (lm["x"] - x_min) / x_range
            norm_y = (lm["y"] - y_min) / y_range
            features.extend([norm_x, norm_y])
        
        # 2. Thumb direction (crucial for thumbs up/down)
        thumb_direction = (thumb_tip["y"] - wrist["y"]) / y_range
        features.append(thumb_direction)
        
        # 3. Finger extensions (distance from wrist to fingertips)
        for tip in [thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip]:
            dx = tip["x"] - wrist["x"]
            dy = tip["y"] - wrist["y"]
            distance = np.sqrt(dx**2 + dy**2)
            features.append(distance)
        
        # 4. Finger curling (for fist detection)
        for mcp, pip, dip, tip in [
            (index_mcp, index_pip, index_dip, index_tip),
            (middle_mcp, middle_pip, middle_dip, middle_tip),
            (ring_mcp, ring_pip, ring_dip, ring_tip),
            (pinky_mcp, pinky_pip, pinky_dip, pinky_tip)
        ]:
            # Calculate angle between segments
            v1x = pip["x"] - mcp["x"]
            v1y = pip["y"] - mcp["y"]
            v2x = dip["x"] - pip["x"]
            v2y = dip["y"] - pip["y"]
            v3x = tip["x"] - dip["x"]
            v3y = tip["y"] - dip["y"]
            
            # Dot products to estimate finger curling
            dot1 = v1x * v2x + v1y * v2y
            dot2 = v2x * v3x + v2y * v3y
            features.extend([dot1, dot2])
        
        # 5. Hand openness (for fist vs. open hand)
        hand_area = x_range * y_range
        features.append(hand_area)
        
        # 6. Finger-to-finger distances (for yo-yo sign)
        finger_tips = [thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip]
        for i in range(len(finger_tips)):
            for j in range(i+1, len(finger_tips)):
                dx = finger_tips[i]["x"] - finger_tips[j]["x"]
                dy = finger_tips[i]["y"] - finger_tips[j]["y"]
                distance = np.sqrt(dx**2 + dy**2)
                features.append(distance)
        
        # 7. Thumb position relative to other fingers (for thumbs up/down)
        for finger_tip in [index_tip, middle_tip, ring_tip, pinky_tip]:
            dx = thumb_tip["x"] - finger_tip["x"]
            dy = thumb_tip["y"] - finger_tip["y"]
            features.extend([dx, dy])
        
        return np.array(features).reshape(1, -1)

    def train(self, X, y):
        """Train the gesture classifier"""
        if X.size == 0 or len(y) == 0:
            print("[Classifier] Error: Empty training data")
            return False
        
        print(f"[Classifier] Training with {len(X)} samples, {len(np.unique(y))} classes")
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train a Random Forest classifier (more robust than SVM for this task)
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            random_state=42
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
        if max_proba > 0.7:  # Threshold for confidence
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
