import cv2
import time
import json
import argparse
import os
from utils.osc_handler import OSCHandler
from ml.classifier import GestureClassifier
from ml.trainer import GestureTrainer
from sound_control import SoundController
from utils.gesture_Detection import GestureDetector

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
        self.webcam = None  # Initialize webcam variable
        
        self.gesture_detector=GestureDetector()

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
    
    @staticmethod
    def clean_args(args):
        cleaned = []
        for arg in args:
            # If it's a string, remove parentheses and whitespace
            if isinstance(arg, str):
                # Remove parentheses and brackets completely
                arg_no_paren = arg.replace("(", "").replace(")", "").replace("[", "").replace("]", "").strip()
                # Skip if now empty
                if not arg_no_paren:
                    continue
                # Try to convert to float or int
                try:
                    # Try int first for flags, then float
                    if arg_no_paren.isdigit() or (arg_no_paren.startswith('-') and arg_no_paren[1:].isdigit()):
                        cleaned.append(int(arg_no_paren))
                    else:
                        cleaned.append(float(arg_no_paren))
                except ValueError:
                    # If it's not a number, keep the string (for gesture names)
                    if arg_no_paren:
                        cleaned.append(arg_no_paren)
            else:
                cleaned.append(arg)
        return cleaned

    
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
        
        # Add a catch-all handler for debugging
        self.osc_handler.dispatcher.set_default_handler(
            lambda address, *args: print(f"DEFAULT HANDLER: {address} {args}")
        )
        
        # Start the OSC server
        self.osc_server_thread = self.osc_handler.start_server()
    
    def handle_landmarks(self, address, *args):
        """Handle incoming landmark data from Pure Data"""
        print(f"Received message at address: {address}")
        print(f"Arguments: {args}")
        args = self.clean_args(args)
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
    
    def start_webcam(self):
        """Start the webcam capture"""
        # Try different camera indices if the default doesn't work
        for camera_index in range(5):  # Try indices 0-4
            print(f"Trying to open camera at index {camera_index}")
            self.webcam = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            if self.webcam.isOpened():
                print(f"Successfully opened camera at index {camera_index}")
                # Set resolution
                self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                return True
        
        print("Error: Could not open any camera")
        return False
    
    def stop_webcam(self):
        """Stop the webcam capture"""
        if hasattr(self, 'gesture_detector'):
            self.gesture_detector.release()
            
        if self.webcam is not None and self.webcam.isOpened():
            self.webcam.release()
            cv2.destroyAllWindows()
            print("Webcam stopped")

    
    def start_training(self, address, *args):
        """Start training mode for a gesture"""
        args = self.clean_args(args)
        if hasattr(self, 'gesture_detector'):
            self.gesture_detector.reinitialize()
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
                    ret, frame = self.webcam.read()
                    if not ret:
                        print("Failed to grab frame from webcam")
                        break
                    
                    # Detect hand landmarks
                    landmarks, annotated_frame = self.gesture_detector.detect_landmarks(frame)
                    
                    # Display the annotated frame
                    cv2.putText(annotated_frame, "TRAINING MODE", (20, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    cv2.putText(annotated_frame, f"Gesture: {self.trainer.current_gesture}", (20, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(annotated_frame, "Press 'q' to stop training", (20, frame.shape[0] - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
                    # Show sample count
                    if hasattr(self.trainer, 'training_data'):
                        sample_count = len(self.trainer.training_data)
                        cv2.putText(annotated_frame, f"Samples: {sample_count}", (20, 90),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    cv2.imshow('Training Mode - Press q to stop', annotated_frame)
                    
                    # Break the loop if 'q' is pressed
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self.stop_training(address)
                        break
            else:
                print("Could not start webcam for training")
    
    def record_training_sample(self, address, *args):
        """Record a training sample"""
        args = self.clean_args(args)
        if len(args) > 1:
            try:
                # Get the latest landmarks from the gesture detector
                if self.webcam is not None and self.webcam.isOpened():
                    ret, frame = self.webcam.read()
                    if ret:
                        landmarks, annotated_frame = self.gesture_detector.detect_landmarks(frame)
                        
                        # Last argument is the is_gesture flag
                        is_gesture = bool(int(args[-1]))  # 1 for green light, 0 for yellow light
                        
                        # Add to training data
                        self.trainer.add_sample(landmarks, is_gesture)
                        
                        # Create a copy of the frame for drawing
                        display_frame = annotated_frame.copy()
                        
                        # Draw a colored border based on is_gesture
                        color = (0, 255, 0) if is_gesture else (0, 255, 255)  # Green or Yellow
                        cv2.rectangle(display_frame, (0, 0), (frame.shape[1], frame.shape[0]), color, 10)
                        
                        # Add a "Recording" indicator
                        cv2.putText(display_frame, "SAMPLE RECORDED!", (20, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                        
                        # Show sample count
                        sample_count = len(self.trainer.training_data)
                        cv2.putText(display_frame, f"Samples: {sample_count}", (20, 90),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                        
                        # Show the frame with visual feedback
                        cv2.imshow('Training Mode - Press q to stop', display_frame)
                        
                        # Flash effect - show for a moment then return to normal
                        cv2.waitKey(200)  # Show the recording indicator for 200ms
                
            except Exception as e:
                print(f"Error recording training sample: {e}")


    def show_webcam_frame(self):
        """Show the current webcam frame with instructions"""
        if self.webcam is not None and self.webcam.isOpened():
            ret, frame = self.webcam.read()
            if ret:
                # Add instructions and status
                cv2.putText(frame, "TRAINING MODE", (20, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(frame, f"Gesture: {self.trainer.current_gesture}", (20, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, "Press 'q' to stop training", (20, frame.shape[0] - 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                # Show sample count
                if hasattr(self.trainer, 'training_data'):
                    sample_count = len(self.trainer.training_data)
                    cv2.putText(frame, f"Samples: {sample_count}", (20, 90), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow('Training Mode - Press q to stop', frame)
                cv2.waitKey(1)


    def stop_training(self, address, *args):
        if hasattr(self, 'gesture_detector'):
            self.gesture_detector.hands.close()
        self.stop_webcam()
        
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
            self.stop_webcam()
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
