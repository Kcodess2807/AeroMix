import cv2
import time
import json
import argparse
from gesture_detection import GestureDetector
from sound_control import SoundController
from ml_models.mlp_classifier import GestureClassifier
from utils.osc_communication import OSCHandler
from visualizer import Visualizer
import numpy as np
class AeroMixApp:
    def __init__(self, camera_id=0, use_mediapipe=True, use_yolo=False,
                model_path=None, training_mode=False):
        # Initialize components
        self.detector = GestureDetector(use_mediapipe, use_yolo)
        self.osc_handler = OSCHandler()
        self.sound_controller = SoundController(self.osc_handler)
        self.classifier = GestureClassifier(model_path)
        self.visualizer = Visualizer()
        
        # Camera setup
        self.camera_id = camera_id
        self.cap = None
        
        # Application state
        self.running = False
        self.training_mode = training_mode
        self.training_data = []
        self.training_labels = []
        
        # Set up OSC handlers
        self.setup_osc_handlers()
        
    def setup_osc_handlers(self):
        """Set up OSC message handlers"""
        # Handler for receiving landmarks from Max/MSP
        self.osc_handler.add_handler("/landmarks", self.handle_landmarks)
        
        # Handler for training commands
        self.osc_handler.add_handler("/training/start", self.start_training)
        self.osc_handler.add_handler("/training/record", self.record_training_sample)
        self.osc_handler.add_handler("/training/stop", self.stop_training)
        
        # Start the OSC server
        self.osc_server_thread = self.osc_handler.start_server()
        
    def handle_landmarks(self, address, *args):
        """Handle incoming landmark data from Max/MSP"""
        if len(args) > 0:
            try:
                # Parse the JSON data
                landmarks = json.loads(args[0])
                
                # Process the landmarks
                if self.training_mode:
                    # Store for training
                    pass
                else:
                    # Classify the gesture
                    gesture = self.classifier.predict(landmarks)
                    
                    # Control sound based on the gesture
                    self.process_gesture(gesture)
            except Exception as e:
                print(f"Error processing landmarks: {e}")
    
    def process_gesture(self, gesture):
        """Process a detected gesture and control sound"""
        # Map gestures to sound control actions
        if gesture == "TEMPO_UP":
            self.sound_controller.adjust_tempo(5.0)
        elif gesture == "TEMPO_DOWN":
            self.sound_controller.adjust_tempo(-5.0)
        elif gesture == "PITCH_UP":
            self.sound_controller.adjust_pitch(0.1)
        elif gesture == "PITCH_DOWN":
            self.sound_controller.adjust_pitch(-0.1)
        elif gesture == "VOLUME_UP":
            self.sound_controller.adjust_volume(0.1)
        elif gesture == "VOLUME_DOWN":
            self.sound_controller.adjust_volume(-0.1)
        elif gesture == "EFFECT_REVERB":
            self.sound_controller.apply_effect("reverb", 0.8)
        elif gesture == "PLAY":
            self.sound_controller.control_playback("play", "data/audio/tracks/demo.mp3")
        elif gesture == "PAUSE":
            self.sound_controller.control_playback("pause")
    
    def start_camera(self):
        """Start the camera capture"""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise ValueError(f"Failed to open camera {self.camera_id}")
    
    def run(self):
        """Run the main application loop"""
        self.running = True
        self.start_camera()
        
        try:
            while self.running:
                # Capture frame
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # Process frame to detect gestures
                landmarks = self.detector.process_frame(frame)
                
                if landmarks:
                    # If in training mode, store the landmarks
                    if self.training_mode:
                        pass
                    else:
                        # Classify the gesture
                        gesture = self.classifier.predict(landmarks)
                        
                        # Process the gesture
                        self.process_gesture(gesture)
                    
                    # Visualize the landmarks
                    self.detector.visualize_landmarks(frame, landmarks)
                
                # Update the visualizer
                self.visualizer.update(frame)
                
                # Display the frame
                cv2.imshow('AEROMIX', frame)
                
                # Check for exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.running = False
        
        finally:
            # Clean up
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            self.osc_handler.stop_server()
    
    def start_training(self, address, *args):
        """Start training mode"""
        self.training_mode = True
        self.training_data = []
        self.training_labels = []
        print("Training mode started")
    
    def record_training_sample(self, address, *args):
        """Record a training sample"""
        if len(args) > 1:
            try:
                landmarks = json.loads(args[0])
                label = args[1]
                
                # Add to training data
                features = self.classifier.preprocess_landmarks(landmarks)
                self.training_data.append(features[0])
                self.training_labels.append(label)
                
                print(f"Recorded sample for gesture: {label}")
            except Exception as e:
                print(f"Error recording training sample: {e}")
    
    def stop_training(self, address, *args):
        """Stop training mode and train the model"""
        if len(self.training_data) > 0:
            # Convert to numpy arrays
            X = np.array(self.training_data)
            y = np.array(self.training_labels)
            
            # Train the classifier
            self.classifier.train(X, y)
            
            # Save the model
            self.classifier.save_model("model/trained/mlp_gesture_model.pkl")
            
            print(f"Model trained with {len(self.training_data)} samples")
        
        self.training_mode = False
        print("Training mode stopped")

def main():
    parser = argparse.ArgumentParser(description='AEROMIX - Touchless DJ System')
    parser.add_argument('--camera', type=int, default=0, help='Camera device ID')
    parser.add_argument('--model', type=str, default=None, help='Path to trained model')
    parser.add_argument('--training', action='store_true', help='Start in training mode')
    
    args = parser.parse_args()
    
    app = AeroMixApp(
        camera_id=args.camera,
        model_path=args.model,
        training_mode=args.training
    )
    
    app.run()

if __name__ == "__main__":
    main()
