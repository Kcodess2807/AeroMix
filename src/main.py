import cv2
import time
import json
import argparse
import os
from utils.osc_handler import OSCHandler
from ml.classifier import GestureClassifier
from ml.trainer import GestureTrainer
from sound_control import SoundController

class AeroMixApp:
    def __init__(self, model_dir="model/trained", training_mode=False):
        # Initialize components
        self.osc_handler = OSCHandler(receive_port=5005, send_port=5006)  # Updated ports for PD
        self.sound_controller = SoundController(self.osc_handler)
        self.trainer = GestureTrainer(save_dir=model_dir)
        
        # Load all available gesture models
        self.gestures = {}
        self.load_gesture_models(model_dir)
        
        # Application state
        self.running = False
        self.training_mode = training_mode
        
        # Set up OSC handlers
        self.setup_osc_handlers()
        
    def load_gesture_models(self, model_dir):
        """Load all trained gesture models"""
        if not os.path.exists(model_dir):
            os.makedirs(model_dir, exist_ok=True)
            return
            
        # Look for model files
        for filename in os.listdir(model_dir):
            if filename.endswith("_model.pkl"):
                gesture_name = filename.replace("_model.pkl", "")
                model_path = os.path.join(model_dir, filename)
                
                # Load the model
                self.gestures[gesture_name] = GestureClassifier(model_path)
                print(f"Loaded model for gesture: {gesture_name}")
        
    def setup_osc_handlers(self):
        """Set up OSC message handlers for Pure Data"""
        # Handler for receiving landmarks from Pure Data
        self.osc_handler.add_handler("/pd/landmarks", self.handle_landmarks)
        
        # Handlers for training commands
        self.osc_handler.add_handler("/pd/training/start", self.start_training)
        self.osc_handler.add_handler("/pd/training/record", self.record_training_sample)
        self.osc_handler.add_handler("/pd/training/stop", self.stop_training)
        
        # For backward compatibility, keep the original handlers too
        self.osc_handler.add_handler("/landmarks", self.handle_landmarks)
        self.osc_handler.add_handler("/training/start", self.start_training)
        self.osc_handler.add_handler("/training/record", self.record_training_sample)
        self.osc_handler.add_handler("/training/stop", self.stop_training)
        
        # Start the OSC server
        self.osc_server_thread = self.osc_handler.start_server()
        
    def handle_landmarks(self, address, *args):
        """"Handle incoming landmark data from Pure Data"""
        print(f"Received message at address: {address}")
        print(f"Arguments: {args}")
        if len(args) > 0:
            try:
                # Check if the data is already JSON or a list of coordinates
                if isinstance(args[0], str):
                    try:
                        # Try to parse as JSON (Max/MSP style)
                        landmarks = json.loads(args[0])
                    except json.JSONDecodeError:
                        # If not JSON, might be a string representation of a list
                        print(f"Received non-JSON data: {args[0][:100]}...")
                        return
                else:
                    # Pure Data might send a flat list of coordinates
                    # We need to reconstruct the landmark structure
                    landmarks = self.reconstruct_landmarks_from_list(args)
                
                # Process the landmarks
                if self.training_mode:
                    # In training mode, just collect samples
                    pass
                else:
                    # In performance mode, recognize gestures
                    self.recognize_gesture(landmarks)
            except Exception as e:
                print(f"Error processing landmarks: {e}")
    
    def reconstruct_landmarks_from_list(self, args):
        """Reconstruct landmark structure from a flat list of coordinates"""
        # This is a simplified example - adjust based on your actual data format
        landmarks = {"pose": [], "left_hand": [], "right_hand": []}
        
        # If we have a flat list of coordinates
        if len(args) > 0 and isinstance(args[0], (list, tuple)):
            coords = args[0]
        else:
            coords = args
            
        # Process coordinates in pairs (x,y)
        try:
            # Assuming first 33*2 values are pose landmarks (if using MediaPipe pose)
            pose_points = min(33*2, len(coords))
            for i in range(0, pose_points, 2):
                if i+1 < len(coords):
                    landmarks["pose"].append({"x": float(coords[i]), "y": float(coords[i+1]), "z": 0.0})
            
            # Remaining points could be hand landmarks
            # This is very simplified - you'll need to adjust based on your actual data
            remaining = len(coords) - pose_points
            if remaining > 0:
                hand_points = min(21*2, remaining)  # 21 landmarks per hand in MediaPipe
                for i in range(pose_points, pose_points + hand_points, 2):
                    if i+1 < len(coords):
                        landmarks["left_hand"].append({"x": float(coords[i]), "y": float(coords[i+1]), "z": 0.0})
        except Exception as e:
            print(f"Error reconstructing landmarks: {e}")
            
        return landmarks
    
    def recognize_gesture(self, landmarks):
        """Recognize gestures from landmarks and control sound"""
        # Check each loaded gesture model
        detected_gestures = []
        
        for gesture_name, classifier in self.gestures.items():
            try:
                prediction = classifier.predict(landmarks)
                if prediction == gesture_name:
                    detected_gestures.append(gesture_name)
                    print(f"Detected gesture: {gesture_name}")
            except Exception as e:
                print(f"Error predicting with model {gesture_name}: {e}")
        
        # Process detected gestures
        for gesture in detected_gestures:
            self.process_gesture(gesture)
    
    def process_gesture(self, gesture):
        """Process a detected gesture and control sound"""
        # Map gestures to sound control actions based on gesture name
        if gesture == "volume_up":
            self.sound_controller.adjust_volume(0.1)
        elif gesture == "volume_down":
            self.sound_controller.adjust_volume(-0.1)
        elif gesture == "tempo_up":
            self.sound_controller.adjust_tempo(5.0)
        elif gesture == "tempo_down":
            self.sound_controller.adjust_tempo(-5.0)
        elif gesture == "pitch_up":
            self.sound_controller.adjust_pitch(0.1)
        elif gesture == "pitch_down":
            self.sound_controller.adjust_pitch(-0.1)
        elif gesture == "bass_up":
            self.sound_controller.adjust_bass(0.1)
        elif gesture == "bass_down":
            self.sound_controller.adjust_bass(-0.1)
        elif gesture == "play":
            self.sound_controller.control_playback("play", "data/audio/demo.mp3")
    
    def start_training(self, address, *args):
        """Start training mode for a gesture"""
        if len(args) > 0:
            gesture_name = args[0]
            self.trainer.start_training(gesture_name)
            self.training_mode = True
            print(f"Started training for gesture: {gesture_name}")
    
    def record_training_sample(self, address, *args):
        """Record a training sample"""
        if len(args) > 1:
            try:
                # Check if first arg is JSON string or list
                if isinstance(args[0], str):
                    try:
                        landmarks = json.loads(args[0])
                    except json.JSONDecodeError:
                        print(f"Error: Invalid JSON in training sample")
                        return
                else:
                    landmarks = self.reconstruct_landmarks_from_list(args[:-1])
                
                # Last argument is the is_gesture flag
                is_gesture = bool(int(args[-1]))  # 1 for green light, 0 for yellow light
                
                # Add to training data
                self.trainer.add_sample(landmarks, is_gesture)
            except Exception as e:
                print(f"Error recording training sample: {e}")
    
    def stop_training(self, address, *args):
        """Stop training and save the model"""
        if self.trainer.stop_training():
            # Reload the models
            self.load_gesture_models(self.trainer.save_dir)
            
        self.training_mode = False
        print("Training stopped")
    
    def run(self):
        """Run the main application loop"""
        self.running = True
        
        try:
            print("AEROMIX is running with Pure Data. Press Ctrl+C to stop.")
            while self.running:
                time.sleep(0.1)  # Just to prevent high CPU usage
                
        except KeyboardInterrupt:
            print("Shutting down AEROMIX...")
        finally:
            # Clean up
            self.osc_handler.stop_server()

def main():
    parser = argparse.ArgumentParser(description='AEROMIX - Gesture-Based DJ System')
    parser.add_argument('--training', action='store_true', help='Start in training mode')
    parser.add_argument('--model-dir', type=str, default='model/trained', help='Directory for trained models')
    
    args = parser.parse_args()
    
    app = AeroMixApp(
        model_dir=args.model_dir,
        training_mode=args.training
    )
    
    app.run()

if __name__ == "__main__":
    main()
