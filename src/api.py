from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import cv2
import numpy as np
import os
import time
from utils.osc_handler import OSCHandler
from ml.classifier import GestureClassifier
from utils.gesture_Detection import GestureDetector
import logging
import traceback

# Suppress MediaPipe warnings
logging.getLogger('mediapipe').setLevel(logging.ERROR)

osc_handler = OSCHandler(receive_port=5025, send_port=5026)
app = Flask(__name__)
CORS(app)

# Initialize GestureDetector once at startup
try:
    gesture_detector = GestureDetector()
    print("[INFO] GestureDetector initialized at startup")
except Exception as e:
    print(f"[ERROR] Failed to initialize GestureDetector: {e}")
    print("[ERROR] Stack trace:")
    traceback.print_exc()
    gesture_detector = None

# Track the last detected gesture and timestamp for cooldown
last_gesture = None
last_gesture_time = 0
COOLDOWN_SECONDS = 1.0

class SoundController:
    def __init__(self):
        self.volume = 0.7
        self.bass = 0.5
        self.tempo = 1.0
        self.pitch = 1.0
        self.osc_handler = osc_handler

    def adjust_volume(self, delta):
        self.volume = max(0.0, min(1.0, self.volume + delta))
        print(f"[DEBUG] Volume adjusted to: {self.volume}")

    def adjust_bass(self, delta):
        self.bass = max(0.0, min(1.0, self.bass + delta))
        print(f"[DEBUG] Bass adjusted to: {self.bass}")

    def adjust_tempo(self, delta):
        self.tempo = max(0.5, min(2.0, self.tempo + delta))
        print(f"[DEBUG] Tempo adjusted to: {self.tempo}")

    def adjust_pitch(self, delta):
        self.pitch = max(0.5, min(2.0, self.pitch + delta))
        print(f"[DEBUG] Pitch adjusted to: {self.pitch}")

    def process_gesture(self, gesture):
        print(f"[DEBUG] Processing gesture: {gesture}")
        if gesture == "volume_up":
            self.adjust_volume(0.1)
        elif gesture == "volume_down":
            self.adjust_volume(-0.1)
        elif gesture == "tempo_up":
            self.adjust_tempo(0.1)
        elif gesture == "tempo_down":
            self.adjust_tempo(-0.1)
        elif gesture == "bass_up":
            self.adjust_bass(0.1)
        elif gesture == "bass_down":
            self.adjust_bass(-0.1)
        elif gesture == "pitch_up":
            self.adjust_pitch(0.1)
        elif gesture == "pitch_down":
            self.adjust_pitch(-0.1)

sound_controller = SoundController()

# Load gesture models
model_dir = "model/trained"
gesture_classifiers = {}
if os.path.exists(model_dir):
    for filename in os.listdir(model_dir):
        if filename.endswith("_model.pkl"):
            gesture_name = filename.replace("_model.pkl", "")
            model_path = os.path.join(model_dir, filename)
            gesture_classifiers[gesture_name] = GestureClassifier(model_path)
            print(f"[DEBUG] Loaded model for gesture: {gesture_name}")
else:
    print(f"[ERROR] Model directory {model_dir} does not exist")

@app.route('/api/gesture', methods=['POST'])
def process_gesture():
    data = request.json
    gesture = data.get('gesture')
    print(f"[DEBUG] Received gesture command: {gesture}")
    sound_controller.process_gesture(gesture)
    return jsonify({
        "status": "success",
        "gesture": gesture,
        "state": {
            "volume": sound_controller.volume,
            "bass": sound_controller.bass,
            "tempo": sound_controller.tempo,
            "pitch": sound_controller.pitch
        }
    })

@app.route('/api/state', methods=['GET'])
def get_state():
    print("[DEBUG] State requested")
    return jsonify({
        "volume": sound_controller.volume,
        "bass": sound_controller.bass,
        "tempo": sound_controller.tempo,
        "pitch": sound_controller.pitch
    })

@app.route('/api/gesture-frame', methods=['POST'])
def gesture_frame():
    global last_gesture, last_gesture_time

    print("[DEBUG] /api/gesture-frame called")
    data = request.json
    frame_data = data.get('frame')
    if not frame_data:
        print("[ERROR] No frame data found in request")
        return jsonify({"error": "No frame data"}), 400

    try:
        # Decode the frame
        imgstr = frame_data.split(',')[1]
        img_bytes = base64.b64decode(imgstr)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            print("[ERROR] Failed to decode image")
            return jsonify({"error": "Failed to decode image"}), 500
        print("[DEBUG] Frame decoded successfully, shape:", img.shape)

        # Check if GestureDetector is initialized
        if gesture_detector is None:
            print("[ERROR] GestureDetector not initialized")
            return jsonify({"status": "success", "gestures": []})

        # Detect landmarks using the global GestureDetector
        print("[DEBUG] Calling detect_landmarks...")
        landmarks_dict, _ = gesture_detector.detect_landmarks(img)
        print(f"[DEBUG] Landmarks dictionary: {landmarks_dict}")

        # Convert landmarks_dict to the format expected by GestureClassifier (list of lists)
        landmarks = []
        for hand in ['left_hand', 'right_hand']:
            if landmarks_dict[hand]:
                hand_landmarks = [
                    type('Landmark', (), {'x': lm['x'], 'y': lm['y'], 'z': lm['z']})
                    for lm in landmarks_dict[hand]
                ]
                landmarks.append(hand_landmarks)
                break  # Use the first detected hand

        if not landmarks:
            print("[DEBUG] No hands detected in frame")
            return jsonify({"status": "success", "gestures": []})
        print(f"[DEBUG] Converted landmarks: {len(landmarks)} hands detected, each with {len(landmarks[0]) if landmarks else 0} landmarks")

        # Classify gestures
        detected_gestures = []
        if not gesture_classifiers:
            print("[ERROR] No gesture classifiers loaded")
            return jsonify({"error": "No gesture classifiers loaded"}), 500

        current_time = time.time()
        for gesture_name, classifier in gesture_classifiers.items():
            features = classifier.preprocess_landmarks(landmarks)
            if features.size == 0:
                print(f"[DEBUG] No features extracted for gesture: {gesture_name}")
                continue
            print(f"[DEBUG] Features extracted for gesture {gesture_name}:", features.shape)
            prediction = classifier.predict(features)
            confidence = classifier.predict_proba(features)
            print(f"[Classifier] Prediction: {prediction} with confidence {confidence:.2f}")
            if prediction == gesture_name and confidence > 0.85:
                if (last_gesture == gesture_name and 
                    (current_time - last_gesture_time) < COOLDOWN_SECONDS):
                    print(f"[DEBUG] Gesture {gesture_name} ignored due to cooldown")
                    continue
                detected_gestures.append(gesture_name)
                print(f"[DEBUG] Detected gesture: {gesture_name}")
                last_gesture = gesture_name
                last_gesture_time = current_time
                sound_controller.process_gesture(gesture_name)
            elif confidence < 0.65:
                print(f"[Classifier] Low confidence: {confidence:.2f}, returning NO_GESTURE")

        print(f"[DEBUG] Returning response: {{'status': 'success', 'gestures': {detected_gestures}}}")
        return jsonify({"status": "success", "gestures": detected_gestures})
    except Exception as e:
        print(f"[ERROR] Gesture processing error: {e}")
        print("[ERROR] Stack trace:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, port=5000)