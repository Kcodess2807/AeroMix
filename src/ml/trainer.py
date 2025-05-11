import numpy as np
import os
import json
import time
from .classifier import GestureClassifier
import cv2

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
    
    def start_training(self, address, *args):
        """Start training mode for a gesture"""
        # args = self.clean_args(args)
        if len(args) > 0:
            gesture_name = args[0]
            self.trainer.start_training(gesture_name)
            self.training_mode = True
            
            # Start the webcam for training
            if self.start_webcam():
                print(f"Started training for gesture: {gesture_name}")
                print("Webcam activated for training. Press 'q' to stop training.")
                
                # Open a window to show the webcam feed
                while self.training_mode and self.webcam.isOpened():
                    # Show the webcam frame with instructions
                    self.show_webcam_frame()
                    
                    # Break the loop if 'q' is pressed
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self.stop_training(address)
                        break
            else:
                print("Could not start webcam for training")

        
    def add_sample(self, landmarks, is_gesture=True):
        """Add a training sample
        
        Args:
            landmarks: Body landmarks from MediaPipe
            is_gesture: True for green light moments (main gesture),
                       False for yellow light moments (other movements)
        """

        print(f"add_sample called. Landmarks: {landmarks}, is_gesture: {is_gesture}")
        self.training_data.append((landmarks, is_gesture))
        print(f"Training data length is now: {len(self.training_data)}")
        if not self.is_training:
            return
            
        # Process landmarks to extract features
        features = self.classifier.preprocess_landmarks(landmarks)
        
        # Skip if features are empty
        if features.size == 0 or features.shape[1] == 0:
            print("Warning: Empty features detected, sample skipped")
            return
            
        # Add to training data
        self.training_data.append(features[0])
        
        # Label as current gesture or "other"
        label = self.current_gesture if is_gesture else "OTHER"
        self.training_labels.append(label)
        
        print(f"Adding sample: {landmarks}, is_gesture={is_gesture}")
        print(f"Current training data length: {len(self.training_data)}")

    
    def train_model(self):
        """Train the model with collected samples"""
        if not self.is_training or len(self.training_data) == 0:
            print("No training data available")
            return False
            
        # Convert to numpy arrays
        X = np.array(self.training_data)
        y = np.array(self.training_labels)
        
        # Train the classifier
        print(f"Training model with {len(X)} samples...")
        self.classifier.train(X, y)
        
        # Save the model
        model_path = os.path.join(self.save_dir, f"{self.current_gesture}_model.pkl")
        self.classifier.save_model(model_path)
        print(f"Model trained and saved to {model_path}")
        
        self.is_training = False
        return True
    
    def stop_training(self):
        """Stop training and train the model"""
        if not self.is_training:
            return False
            
        result = self.train_model()
        self.is_training = False
        return result
