from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import cv2
import numpy as np
import os
from utils.osc_handler import OSCHandler
from ml.classifier import GestureClassifier

osc_handler = OSCHandler(receive_port=5025, send_port=5026)
app = Flask(__name__)
CORS(app)

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
    print("[DEBUG] /api/gesture-frame called")
    data = request.json
    frame_data = data.get('frame')
    if frame_data:
        try:
            imgstr = frame_data.split(',')[1]
            img_bytes = base64.b64decode(imgstr)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            from utils.gesture_Detection import GestureDetector
            gesture_detector = GestureDetector()
            landmarks, _ = gesture_detector.detect_landmarks(img)
            detected_gestures = []
            for gesture_name, classifier in gesture_classifiers.items():
                features = classifier.preprocess_landmarks(landmarks)
                if features.size > 0:
                    prediction = classifier.predict(features)
                    if prediction == gesture_name:
                        detected_gestures.append(gesture_name)
                        print(f"[DEBUG] Detected gesture: {gesture_name}")
                        sound_controller.process_gesture(gesture_name)
            return jsonify({"status": "success", "gestures": detected_gestures})
        except Exception as e:
            print(f"[ERROR] Gesture processing error: {e}")
            return jsonify({"error": str(e)}), 500
    print("[ERROR] No frame data found in request")
    return jsonify({"error": "No frame data"}), 400

if __name__ == "__main__":
    app.run(debug=False, port=5000)