import cv2
import time
import json
import argparse
import os
import numpy as np
import threading

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

        # --- PLAY AUDIO ON STARTUP (only in recognition mode) ---
        if not self.training_mode:
            self.sound_controller.control_playback("play", "data/audio/sample1.mp3")

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
                    print(f"Loaded model for gesture: {gesture_name} from {model_path}")
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
        print(f"Received message at address: {address}")
        print(f"Arguments: {args}")
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
        print(f"Reconstructing landmarks from list: {args}")
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
        print("Recognizing gesture...")
        detected_gestures = []
        for gesture_name, classifier in self.gestures.items():
            try:
                features = classifier.preprocess_landmarks(landmarks)
                print(f"[DEBUG] Features for {gesture_name}: {features}")
                if features.size > 0:
                    prediction = classifier.predict(features)
                    print(f"[DEBUG] Predicted: {prediction}, Target: {gesture_name}")
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
            self.sound_controller.control_playback("play", "data/audio/sample1.mp3")

    def start_webcam(self):
        for camera_index in range(5):
            print(f"Trying to open camera at index {camera_index}")
            self.webcam = cv2.VideoCapture(camera_index)
            if self.webcam.isOpened():
                print(f"Successfully opened camera at index {camera_index}")
                self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
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

                # --- AUTOMATIC SAMPLE RECORDING EVERY 300ms ---
                def auto_record():
                    while self.training_mode and self.webcam.isOpened():
                        self.record_training_sample(address, 1)
                        time.sleep(0.3)  # Adjust interval as needed

                threading.Thread(target=auto_record, daemon=True).start()

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
                    cv2.putText(annotated_frame, "Press 'q' to stop training", (20, frame.shape[0] - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    if hasattr(self.trainer, 'training_data'):
                        sample_count = len(self.trainer.training_data)
                        cv2.putText(annotated_frame, f"Samples: {sample_count}", (20, 90),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.imshow('Training Mode - Press q to stop', annotated_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self.stop_training(address)
                        break
            else:
                print("Could not start webcam for training")

    def record_training_sample(self, address, *args):
        print(f"record_training_sample called with args: {args}")
        args = self.clean_args(args)
        if not self.training_mode or not self.webcam or not self.webcam.isOpened() or self._detector_released:
            print("Training not active or webcam not open, skipping sample.")
            return
        if len(args) > 0:  # Now works for both manual and auto-record
            try:
                ret, frame = self.webcam.read()
                if ret:
                    frame = cv2.flip(frame, 1)
                    try:
                        landmarks, annotated_frame = self.gesture_detector.detect_landmarks(frame)
                    except Exception as e:
                        print(f"Warning (detect_landmarks in record_training_sample): {e}")
                        return
                    if not landmarks or (not landmarks["left_hand"] and not landmarks["right_hand"]):
                        print("No hand detected in frame, sample not recorded.")
                        return
                    is_gesture = bool(int(args[-1]))
                    self.trainer.add_sample(landmarks, is_gesture)
                    print(f"Sample recorded for {self.trainer.current_gesture}, is_gesture={is_gesture}, total samples={len(self.trainer.training_data)}")
                    display_frame = annotated_frame.copy()
                    color = (0, 255, 0) if is_gesture else (0, 255, 255)
                    cv2.rectangle(display_frame, (0, 0), (frame.shape[1], frame.shape[0]), color, 10)
                    cv2.putText(display_frame, "SAMPLE RECORDED!", (20, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                    sample_count = len(self.trainer.training_data)
                    cv2.putText(display_frame, f"Samples: {sample_count}", (20, 90),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    cv2.imshow('Training Mode - Press q to stop', display_frame)
                    cv2.waitKey(200)
            except Exception as e:
                print(f"Error recording training sample: {e}")

    def show_webcam_frame(self):
        if self.webcam is not None and self.webcam.isOpened():
            ret, frame = self.webcam.read()
            if ret:
                frame = cv2.flip(frame, 1)
                cv2.putText(frame, "TRAINING MODE", (20, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(frame, f"Gesture: {self.trainer.current_gesture}", (20, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, "Press 'q' to stop training", (20, frame.shape[0] - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                if hasattr(self.trainer, 'training_data'):
                    sample_count = len(self.trainer.training_data)
                    cv2.putText(frame, f"Samples: {sample_count}", (20, 90),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.imshow('Training Mode - Press q to stop', frame)
                cv2.waitKey(1)

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

        # Enhanced gesture recognition with observation window
        pred_history = []
        HISTORY_SIZE = 5
        PRED_THRESHOLD = 3  # Minimum consecutive frames for a gesture
        last_label = ""
        label_timer = 0
        last_gesture_time = 0
        GESTURE_COOLDOWN = 0.5  # Seconds to wait before detecting same gesture again

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
                # Try to detect a gesture
                for gesture_name, classifier in self.gestures.items():
                    features = classifier.preprocess_landmarks(landmarks)
                    if features.size > 0:
                        pred = classifier.predict(features)
                        if pred == gesture_name:
                            pred_this_frame = pred
                            break  # Only process the first matching gesture
                
                # Add to history
                if pred_this_frame is not None:
                    pred_history.append(pred_this_frame)
                    if len(pred_history) > HISTORY_SIZE:
                        pred_history.pop(0)
                    
                    # Check if we have enough consistent predictions
                    if len(pred_history) >= PRED_THRESHOLD:
                        # Count occurrences of each gesture in the history
                        gesture_counts = {}
                        for gesture in pred_history:
                            if gesture in gesture_counts:
                                gesture_counts[gesture] += 1
                            else:
                                gesture_counts[gesture] = 1
                        
                        # Find the most common gesture
                        most_common = max(gesture_counts, key=gesture_counts.get, default=None)
                        
                        # Only trigger if the gesture appears consistently and cooldown has passed
                        if (most_common is not None and 
                            gesture_counts[most_common] >= PRED_THRESHOLD and
                            current_time - last_gesture_time > GESTURE_COOLDOWN):
                            
                            self.process_gesture(most_common)
                            recognized_label = label_map.get(most_common, most_common)
                            last_label = recognized_label
                            label_timer = 15  # Show label for 15 frames
                            last_gesture_time = current_time
                            
                            # Clear history after triggering to avoid rapid repeats
                            pred_history = []

            # Draw the last recognized label for a short time
            if label_timer > 0 and last_label:
                cv2.putText(
                    annotated_frame, f"{last_label}", (20, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3
                )
                label_timer -= 1

            # Draw a volume bar
            bar_top = 150
            bar_bottom = 400
            bar_left = 50
            bar_right = 85
            vol_bar = int(np.interp(self.sound_controller.volume, [0.0, 1.0], [bar_bottom, bar_top]))
            cv2.rectangle(annotated_frame, (bar_left, bar_top), (bar_right, bar_bottom), (0, 0, 0), 3)
            cv2.rectangle(annotated_frame, (bar_left, vol_bar), (bar_right, bar_bottom), (0, 255, 0), cv2.FILLED)
            cv2.putText(
                annotated_frame,
                f'Volume: {int(self.sound_controller.volume*100)}%',
                (40, 430),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
            )

            # Draw a bass bar next to volume bar
            bass_bar_left = 100
            bass_bar_right = 135
            bass_bar = int(np.interp(self.sound_controller.bass, [0.0, 1.0], [bar_bottom, bar_top]))
            cv2.rectangle(annotated_frame, (bass_bar_left, bar_top), (bass_bar_right, bar_bottom), (0, 0, 0), 3)
            cv2.rectangle(annotated_frame, (bass_bar_left, bass_bar), (bass_bar_right, bar_bottom), (255, 0, 0), cv2.FILLED)
            cv2.putText(
                annotated_frame,
                f'Bass: {int(self.sound_controller.bass*100)}%',
                (90, 430),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2
            )

            # Draw confidence meter (optional)
            if pred_history:
                most_common = max(set(pred_history), key=pred_history.count)
                confidence = pred_history.count(most_common) / len(pred_history)
                conf_width = int(100 * confidence)
                cv2.rectangle(annotated_frame, (500, 50), (500 + conf_width, 70), (0, 255, 255), cv2.FILLED)
                cv2.rectangle(annotated_frame, (500, 50), (600, 70), (0, 0, 0), 2)
                cv2.putText(
                    annotated_frame,
                    f'Confidence',
                    (500, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
                )

            cv2.imshow("Recognition Mode", annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.stop_webcam()


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
        print(f"Stopping training for {self.trainer.current_gesture}. Total samples: {len(self.trainer.training_data)}")

    def run(self):
        self.running = True
        try:
            print("AEROMIX is running with Pure Data. Press Ctrl+C to stop.")
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
