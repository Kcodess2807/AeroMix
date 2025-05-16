import numpy as np
import os
from .classifier import GestureClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

class GestureTrainer:
    def __init__(self, save_dir="model/trained"):
        self.classifier = GestureClassifier()
        self.save_dir = save_dir
        self.training_data = []
        self.training_labels = []
        self.is_training = False
        self.current_gesture = None
        os.makedirs(self.save_dir, exist_ok=True)

    def start_training(self, gesture_name):
        """Start training mode for a gesture"""
        print(f"GestureTrainer: Starting training for gesture '{gesture_name}'")
        self.training_data = []
        self.training_labels = []
        self.is_training = True
        self.current_gesture = gesture_name

    def add_sample(self, landmarks, label):
        """Add a training sample with explicit label (gesture or neutral)"""
        print(f"add_sample called. Landmarks: {landmarks}, label: {label}")
        if not self.is_training:
            print("Not in training mode, sample not added.")
            return

        features = self.classifier.preprocess_landmarks(landmarks)
        print(f"Extracted features: {features}")

        if features.size == 0 or (features.ndim > 1 and features.shape[1] == 0):
            print("Warning: Empty features detected, sample skipped")
            return

        self.training_data.append(features.flatten())
        self.training_labels.append(label)
        print(f"Sample added. Label: {label}, Current training data length: {len(self.training_data)}")

    def train_model(self):
        """Train the model with collected samples"""
        if not self.is_training or len(self.training_data) < 50:
            print(f"Insufficient training data: {len(self.training_data)} samples. Need at least 50.")
            return False

        X = np.array(self.training_data)
        y = np.array(self.training_labels)
        unique_labels, counts = np.unique(y, return_counts=True)
        print(f"Training model with {len(X)} samples. Labels: {unique_labels}, Counts: {counts}")

        if len(unique_labels) < 2:
            print("Need at least two classes (gesture and neutral) for training.")
            return False

        # Split data for validation
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train classifier
        self.classifier.train(X_train, y_train)
        
        # Evaluate on test set
        y_pred = []
        for features in X_test:
            pred = self.classifier.predict(features.reshape(1, -1))
            y_pred.append(pred)
        
        print("Classification Report:")
        # Filter out NO_GESTURE for reporting
        filtered = [(yt, yp) for yt, yp in zip(y_test, y_pred) if yp != "NO_GESTURE"]
        if filtered:
            y_test_filtered, y_pred_filtered = zip(*filtered)
            print(classification_report(y_test_filtered, y_pred_filtered))
        else:
            print("No valid predictions to report (all predictions were NO_GESTURE).")

        # Save the model
        model_path = os.path.join(self.save_dir, f"{self.current_gesture}_model.pkl")
        try:
            self.classifier.save_model(model_path)
            print(f"Model trained and saved to {model_path}")
        except Exception as e:
            print(f"Error saving model: {e}")
            return False

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
