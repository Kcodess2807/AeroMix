import numpy as np
import os
from .classifier import GestureClassifier

class GestureTrainer:
    def __init__(self, save_dir="model/trained"):
        self.classifier = GestureClassifier()
        self.save_dir = save_dir
        self.training_data = []
        self.training_labels = []
        self.is_training = False
        self.current_gesture = None

        # Ensure save directory exists
        os.makedirs(self.save_dir, exist_ok=True)

    def start_training(self, gesture_name):
        """Start training mode for a gesture"""
        print(f"GestureTrainer: Starting training for gesture '{gesture_name}'")
        self.training_data = []
        self.training_labels = []
        self.is_training = True
        self.current_gesture = gesture_name

    def add_sample(self, landmarks, is_gesture=True):
        """Add a training sample"""
        print(f"add_sample called. Landmarks: {landmarks}, is_gesture: {is_gesture}")
        if not self.is_training:
            print("Not in training mode, sample not added.")
            return

        # Process landmarks to extract features
        features = self.classifier.preprocess_landmarks(landmarks)
        print(f"Extracted features: {features}")

        # Skip if features are empty or malformed
        if features.size == 0 or (features.ndim > 1 and features.shape[1] == 0):
            print("Warning: Empty features detected, sample skipped")
            return

        # Add to training data (flatten if needed)
        self.training_data.append(features.flatten())
        label = self.current_gesture if is_gesture else "OTHER"
        self.training_labels.append(label)
        print(f"Sample added. Current training data length: {len(self.training_data)}")

    def train_model(self):
        """Train the model with collected samples"""
        if not self.is_training or len(self.training_data) == 0:
            print("No training data available")
            return False

        # Convert to numpy arrays
        X = np.array(self.training_data)
        y = np.array(self.training_labels)
        print(f"Training model with {len(X)} samples. Labels: {np.unique(y)}")

        # Train the classifier
        self.classifier.train(X, y)

        # Save the model
        model_path = os.path.join(self.save_dir, f"{self.current_gesture}_model.pkl")
        try:
            self.classifier.save_model(model_path)
            print(f"Model trained and saved to {model_path}")
        except Exception as e:
            print(f"Error saving model: {e}")
            return False

        self.is_training = False
        return True

    def stop_training(self):
        """Stop training and train the model"""
        print(f"Stopping training for {self.current_gesture}. Total samples: {len(self.training_data)}")
        if not self.is_training:
            print("Not in training mode, nothing to stop.")
            return False
        result = self.train_model()
        self.is_training = False
        return result
