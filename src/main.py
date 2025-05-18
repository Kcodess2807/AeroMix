import cv2
import time
import json
import argparse
import os
import numpy as np
from utils.osc_handler import OSCHandler
from ml.classifier import GestureClassifier
from ml.trainer import GestureTrainer
from sound_control import SoundController
from utils.gesture_Detection import GestureDetector

class AeroMixApp:
    def __init__(self, model_dir="model/trained", training_mode=False):
        print("AeroMixApp: Initializing...")
        self.osc_handler = OSCHandler(receive_port=5005, send_port=5006)
        self.sound_controller = SoundController(self.osc_handler)
        self.trainer = GestureTrainer(save_dir=model_dir)
        self.gestures = {}
        self.model_dir = model_dir
        self.load_gesture_models(model_dir)
        self.running = False
        self.training_mode = training_mode
        self.webcam = None
        self.gesture_detector = GestureDetector()
        self._detector_released = False
        self.setup_osc_handlers()
        if not self.training_mode:
            self.sound_controller.control_playback("play", "data/audio/audio3.mp3")

    def load_gesture_models(self, model_dir):
        print(f"Loading gesture models from {model_dir}")
        self.gestures = {}
        if not os.path.exists(model_dir):
            os.makedirs(model_dir, exist_ok=True)
            return
        for filename in os.listdir(model_dir):
            if filename.endswith("_model.pkl"):
                gesture_name = filename.replace("_model.pkl", "")
                model_path = os.path.join(model_dir, filename)
                try:
                    self.gestures[gesture_name] = GestureClassifier(model_path)
                    print(f"Loaded model for gesture: {gesture_name}")
                except Exception as e:
                    print(f"Failed to load model for {gesture_name}: {e}")
        print(f"Loaded gestures: {list(self.gestures.keys())}")

    @staticmethod
    def clean_args(args):
        cleaned = []
        for arg in args:
            if isinstance(arg, str):
                arg_no_paren = arg.replace("(", "").replace(")", "").replace("[", "").replace("]", "").strip()
                if not arg_no_paren:
                    continue
                try:
                    if arg_no_paren.isdigit() or (arg_no_paren.startswith('-') and arg_no_paren[1:].isdigit()):
                        cleaned.append(int(arg_no_paren))
                    else:
                        cleaned.append(float(arg_no_paren))
                except ValueError:
                    cleaned.append(arg_no_paren)
            else:
                cleaned.append(arg)
        return cleaned

    def setup_osc_handlers(self):
        print("Setting up OSC handlers...")
        self.osc_handler.add_handler("/pd/landmarks", self.handle_landmarks)
        self.osc_handler.add_handler("/pd/training/start", self.start_training)
        self.osc_handler.add_handler("/pd/training/record", self.record_training_sample)
        self.osc_handler.add_handler("/pd/training/stop", self.stop_training)
        self.osc_handler.add_handler("/landmarks", self.handle_landmarks)
        self.osc_handler.add_handler("/training/start", self.start_training)
        self.osc_handler.add_handler("/training/record", self.record_training_sample)
        self.osc_handler.add_handler("/training/stop", self.stop_training)
        self.osc_handler.dispatcher.set_default_handler(
            lambda address, *args: print(f"DEFAULT HANDLER: {address} {args}")
        )
        self.osc_server_thread = self.osc_handler.start_server()

    def handle_landmarks(self, address, *args):
        args = self.clean_args(args)
        if len(args) > 0:
            try:
                if isinstance(args[0], str):
                    try:
                        landmarks = json.loads(args[0])
                    except json.JSONDecodeError:
                        print(f"Received non-JSON data: {args[0][:100]}...")
                        return
                else:
                    landmarks = self.reconstruct_landmarks_from_list(args)
                if self.training_mode:
                    print("Training mode active: not processing landmarks for recognition.")
                else:
                    self.recognize_gesture(landmarks)
            except Exception as e:
                print(f"Error processing landmarks: {e}")

    def reconstruct_landmarks_from_list(self, args):
        landmarks = {"pose": [], "left_hand": [], "right_hand": []}
        if len(args) > 0 and isinstance(args[0], (list, tuple)):
            coords = args[0]
        else:
            coords = args
        try:
            pose_points = min(33*2, len(coords))
            for i in range(0, pose_points, 2):
                if i+1 < len(coords):
                    landmarks["pose"].append({"x": float(coords[i]), "y": float(coords[i+1]), "z": 0.0})
            remaining = len(coords) - pose_points
            if remaining > 0:
                hand_points = min(21*2, remaining)
                for i in range(pose_points, pose_points + hand_points, 2):
                    if i+1 < len(coords):
                        landmarks["left_hand"].append({"x": float(coords[i]), "y": float(coords[i+1]), "z": 0.0})
        except Exception as e:
            print(f"Error reconstructing landmarks: {e}")
        return landmarks

    def recognize_gesture(self, landmarks):
        detected_gestures = []
        for gesture_name, classifier in self.gestures.items():
            try:
                features = classifier.preprocess_landmarks(landmarks)
                if features.size > 0:
                    prediction = classifier.predict(features)
                    if prediction == gesture_name:
                        detected_gestures.append(gesture_name)
                        print(f"Detected gesture: {gesture_name}")
            except Exception as e:
                print(f"Error predicting with model {gesture_name}: {e}")
        for gesture in detected_gestures:
            self.process_gesture(gesture)

    def process_gesture(self, gesture):
        print(f"Processing gesture: {gesture}")
        if gesture == "volume_up":
            self.sound_controller.adjust_volume(0.1)
        elif gesture == "volume_down":
            self.sound_controller.adjust_volume(-0.1)
        elif gesture == "tempo_up":
            self.sound_controller.adjust_tempo(0.1)  # No division in adjust_tempo
        elif gesture == "tempo_down":
            self.sound_controller.adjust_tempo(-0.1)  # No division in adjust_tempo
        elif gesture == "bass_up":
            self.sound_controller.adjust_bass(0.1)
        elif gesture == "bass_down":
            self.sound_controller.adjust_bass(-0.1)
        elif gesture == "pitch_up":
            self.sound_controller.adjust_pitch(0.1)
        elif gesture == "pitch_down":
            self.sound_controller.adjust_pitch(-0.1)
        elif gesture == "play":
            self.sound_controller.control_playback("play", "data/audio/audio3.mp3")

    def start_webcam(self):
        for camera_index in range(5):
            print(f"Trying to open camera at index {camera_index}")
            self.webcam = cv2.VideoCapture(camera_index)
            if self.webcam.isOpened():
                print(f"Successfully opened camera at index {camera_index}")
                # Set high resolution for better visualization
                self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                return True
        print("Error: Could not open any camera")
        return False

    def stop_webcam(self):
        print("Stopping webcam...")
        if hasattr(self, 'gesture_detector') and not self._detector_released:
            try:
                self.gesture_detector.release()
                self._detector_released = True
            except Exception as e:
                print(f"Warning (gesture_detector.release): {e}")
        if self.webcam is not None and self.webcam.isOpened():
            self.webcam.release()
        cv2.destroyAllWindows()
        print("Webcam stopped")

    def enhanced_visualization(self, annotated_frame, bar_top=150, bar_bottom=900):
        # Get frame dimensions
        frame_height, frame_width = annotated_frame.shape[:2]
        
        # Calculate center position for better layout
        center_y = frame_height // 2
        
        # Helper for color interpolation
        def lerp_color(color1, color2, t):
            return tuple([int(a + (b - a) * t) for a, b in zip(color1, color2)])

        # Map pitch to color hue (blue to magenta)
        def pitch_to_color(pitch):
            t = (pitch - 0.5) / (2.0 - 0.5)
            hue = int(240 + 60 * t)
            color = cv2.cvtColor(np.uint8([[[hue,255,255]]]), cv2.COLOR_HSV2BGR)[0][0]
            return tuple(int(x) for x in color)

        # Calculate positions for circles - evenly spaced across the width
        circle_spacing = frame_width // 5
        circle_y = center_y
        
        # Volume circle (1/5 of the way across)
        vol_x = circle_spacing
        vol_val = self.sound_controller.volume
        vol_radius = int(np.interp(vol_val, [0.0, 1.0], [30, 100]))
        vol_color = lerp_color((0, 100, 0), (0, 255, 0), vol_val)
        cv2.circle(annotated_frame, (vol_x, circle_y), vol_radius, vol_color, -1)
        cv2.putText(annotated_frame, f"Volume: {int(vol_val*100)}%", 
                (vol_x - 80, circle_y + 150), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, vol_color, 3)

        # Bass circle (2/5 of the way across)
        bass_x = circle_spacing * 2
        bass_val = self.sound_controller.bass
        bass_radius = int(np.interp(bass_val, [0.0, 1.0], [30, 100]))
        bass_color = lerp_color((0, 0, 100), (0, 0, 255), bass_val)
        cv2.circle(annotated_frame, (bass_x, circle_y), bass_radius, bass_color, -1)
        cv2.putText(annotated_frame, f"Bass: {int(bass_val*100)}%", 
                (bass_x - 70, circle_y + 150), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, bass_color, 3)

        # Tempo circle with pulsing effect (3/5 of the way across)
        tempo_x = circle_spacing * 3
        tempo_val = self.sound_controller.tempo
        tempo_radius = int(np.interp(tempo_val, [0.5, 2.0], [30, 100]))
        tempo_color = lerp_color((100, 100, 0), (0, 165, 255), (tempo_val-0.5)/1.5)
        pulse = int(5 + 10 * np.sin(time.time() * tempo_val * 2 * np.pi))
        
        # Draw pulse effect
        cv2.circle(annotated_frame, (tempo_x, circle_y), tempo_radius + pulse, tempo_color, 3)
        cv2.circle(annotated_frame, (tempo_x, circle_y), tempo_radius, tempo_color, -1)
        
        base_bpm = 120
        current_bpm = int(tempo_val * base_bpm)
        cv2.putText(annotated_frame, f"Tempo: {current_bpm} BPM", 
                (tempo_x - 100, circle_y + 150), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, tempo_color, 3)

        # Pitch circle (4/5 of the way across)
        pitch_x = circle_spacing * 4
        pitch_val = self.sound_controller.pitch
        pitch_radius = int(np.interp(pitch_val, [0.5, 2.0], [30, 100]))
        pitch_color = pitch_to_color(pitch_val)
        cv2.circle(annotated_frame, (pitch_x, circle_y), pitch_radius, pitch_color, -1)
        cv2.putText(annotated_frame, f"Pitch: {pitch_val:.1f}x", 
                (pitch_x - 80, circle_y + 150), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, pitch_color, 3)

        return annotated_frame


    def run_recognition(self):
        print("Starting real-time gesture recognition...")
        print(f"Available gesture models: {list(self.gestures.keys())}")
        label_map = {
            "volume_up": "Volume Up",
            "volume_down": "Volume Down",
            "bass_up": "Bass Up",
            "bass_down": "Bass Down",
            "tempo_up": "Tempo Up",
            "tempo_down": "Tempo Down",
            "pitch_up": "Pitch Up",
            "pitch_down": "Pitch Down",
            "play": "Play"
        }
        if not self.start_webcam():
            print("Could not open webcam for recognition.")
            return
        pred_history = []
        HISTORY_SIZE = 10
        PRED_THRESHOLD = 7
        last_label = ""
        label_timer = 0
        last_gesture_time = 0
        GESTURE_COOLDOWN = 0.5

        # Create a resizable window (not fullscreen by default)
        cv2.namedWindow("Recognition Mode", cv2.WINDOW_NORMAL)
        
        # Set initial window size (can be resized by user)
        cv2.resizeWindow("Recognition Mode", 1280, 720)
        
        # Flag to track fullscreen state
        is_fullscreen = False

        while True:
            ret, frame = self.webcam.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            landmarks, annotated_frame = self.gesture_detector.detect_landmarks(frame)
            recognized_label = ""
            pred_this_frame = None
            current_time = time.time()

            if landmarks and (landmarks["left_hand"] or landmarks["right_hand"]):
                for gesture_name, classifier in self.gestures.items():
                    features = classifier.preprocess_landmarks(landmarks)
                    if features.size > 0:
                        pred = classifier.predict(features)
                        if pred == gesture_name:
                            pred_this_frame = pred
                            break
                if pred_this_frame:
                    pred_history.append(pred_this_frame)
                    if len(pred_history) > HISTORY_SIZE:
                        pred_history.pop(0)
                    if len(pred_history) >= PRED_THRESHOLD:
                        gesture_counts = {}
                        for gesture in pred_history:
                            gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1
                        most_common = max(gesture_counts, key=gesture_counts.get, default=None)
                        if (most_common and
                            gesture_counts[most_common] >= PRED_THRESHOLD and
                            current_time - last_gesture_time > GESTURE_COOLDOWN):
                            self.process_gesture(most_common)
                            recognized_label = label_map.get(most_common, most_common)
                            last_label = recognized_label
                            label_timer = 15
                            last_gesture_time = current_time
                            pred_history = []

            if label_timer > 0 and last_label:
                cv2.putText(
                    annotated_frame, f"{last_label}", (20, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3
                )
                label_timer -= 1

            # Apply the enhanced circle visualization
            annotated_frame = self.enhanced_visualization(annotated_frame)

            cv2.imshow("Recognition Mode", annotated_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('f'):
                # Toggle fullscreen
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    cv2.setWindowProperty("Recognition Mode", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty("Recognition Mode", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                    
        self.stop_webcam()

    def start_training(self, address, *args):
        print(f"start_training called with args: {args}")
        args = self.clean_args(args)
        
        if hasattr(self, 'gesture_detector'):
            self.gesture_detector.reinitialize()
            self._detector_released = False
        
        if len(args) > 0:
            gesture_name = args[0]
            print(f"Starting training for gesture: {gesture_name}")
            self.trainer.current_gesture = gesture_name
            self.trainer.start_training(gesture_name)
            self.training_mode = True
            
            if self.start_webcam():
                print(f"Started training for gesture: {gesture_name}")
                print("Webcam activated for training. Press 'q' to stop training.")
                print("Press 'g' to record a GESTURE sample, 'n' for NEUTRAL sample.")
                
                # Create a resizable window for training
                cv2.namedWindow('Training Mode', cv2.WINDOW_NORMAL)
                
                while self.training_mode and self.webcam.isOpened():
                    ret, frame = self.webcam.read()
                    if ret:
                        frame = cv2.flip(frame, 1)
                    
                    if not ret:
                        print("Failed to grab frame from webcam")
                        break
                    
                    if not self._detector_released:
                        try:
                            landmarks, annotated_frame = self.gesture_detector.detect_landmarks(frame)
                        except Exception as e:
                            print(f"Warning (detect_landmarks): {e}")
                            break
                    else:
                        annotated_frame = frame
                    
                    cv2.putText(annotated_frame, "TRAINING MODE", (20, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    cv2.putText(annotated_frame, f"Gesture: {self.trainer.current_gesture}", (20, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(annotated_frame, "Press 'g' for gesture, 'n' for neutral, 'q' to stop", (20, frame.shape[0] - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
                    if hasattr(self.trainer, 'training_data'):
                        sample_count = len(self.trainer.training_data)
                        cv2.putText(annotated_frame, f"Samples: {sample_count}", (20, 90),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    cv2.imshow('Training Mode', annotated_frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        self.stop_training(address)
                        break
                    elif key == ord('g'):
                        print("Pressed 'g': Recording gesture sample.")
                        self.record_training_sample(address, self.trainer.current_gesture)
                    elif key == ord('n'):
                        print("Pressed 'n': Recording neutral sample.")
                        self.record_training_sample(address, "neutral")
                    elif key == ord('f'):
                        # Toggle fullscreen
                        current = cv2.getWindowProperty('Training Mode', cv2.WND_PROP_FULLSCREEN)
                        if current == cv2.WINDOW_FULLSCREEN:
                            cv2.setWindowProperty('Training Mode', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                        else:
                            cv2.setWindowProperty('Training Mode', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                print("Could not start webcam for training")

    def record_training_sample(self, address, *args):
        print(f"record_training_sample called with args: {args}")
        args = self.clean_args(args)
        
        if not self.training_mode or not self.webcam or not self.webcam.isOpened() or self._detector_released:
            print("Training not active or webcam not open, skipping sample.")
            return
        
        try:
            ret, frame = self.webcam.read()
            if ret:
                frame = cv2.flip(frame, 1)
                landmarks, annotated_frame = self.gesture_detector.detect_landmarks(frame)
                
                if not landmarks or (not landmarks["left_hand"] and not landmarks["right_hand"]):
                    print("No hand detected in frame, sample not recorded.")
                    return
                
                label = args[0] if args else self.trainer.current_gesture
                self.trainer.add_sample(landmarks, label)
                print(f"Sample recorded for {label}, total samples={len(self.trainer.training_data)}")
                
                display_frame = annotated_frame.copy()
                color = (0, 255, 0) if label != "neutral" else (0, 255, 255)
                cv2.rectangle(display_frame, (0, 0), (frame.shape[1], frame.shape[0]), color, 10)
                cv2.putText(display_frame, f"SAMPLE RECORDED: {label}", (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                
                sample_count = len(self.trainer.training_data)
                cv2.putText(display_frame, f"Samples: {sample_count}", (20, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                cv2.imshow('Training Mode', display_frame)
        except Exception as e:
            print(f"Error recording training sample: {e}")

    def stop_training(self, address, *args):
        print("Stopping training...")
        if hasattr(self, 'gesture_detector') and not self._detector_released:
            try:
                self.gesture_detector.release()
                self._detector_released = True
            except Exception as e:
                print(f"Warning (gesture_detector.release): {e}")
        self.stop_webcam()
        if self.trainer.stop_training():
            self.load_gesture_models(self.trainer.save_dir)
        self.training_mode = False
        print("Training stopped")

    def run(self):
        self.running = True
        try:
            print("AEROMIX is running with Pyo audio engine. Press Ctrl+C to stop.")
            if self.training_mode:
                while self.running:
                    time.sleep(0.1)
            else:
                self.run_recognition()
        except KeyboardInterrupt:
            print("Shutting down AEROMIX...")
        finally:
            self.stop_webcam()
            self.osc_handler.stop_server()
            if hasattr(self.sound_controller, 'cleanup'):
                self.sound_controller.cleanup()

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
