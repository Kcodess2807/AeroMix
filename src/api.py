from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import cv2
import numpy as np
import os
from sound_control import SoundController
from ml.classifier import GestureClassifier
from utils.osc_handler import OSCHandler

osc_handler = OSCHandler(receive_port=5025, send_port=5026)
app = Flask(__name__)
CORS(app)
sound_controller = SoundController()

@app.route('/api/gesture', methods=['POST'])
def process_gesture():
    data = request.json
    gesture = data.get('gesture')
    if gesture == "volume_up":
        sound_controller.adjust_volume(0.1)
    elif gesture == "volume_down":
        sound_controller.adjust_volume(-0.1)
    elif gesture == "tempo_up":
        sound_controller.adjust_tempo(0.1)
    elif gesture == "tempo_down":
        sound_controller.adjust_tempo(-0.1)
    elif gesture == "bass_up":
        sound_controller.adjust_bass(0.1)
    elif gesture == "bass_down":
        sound_controller.adjust_bass(-0.1)
    elif gesture == "pitch_up":
        sound_controller.adjust_pitch(0.1)
    elif gesture == "pitch_down":
        sound_controller.adjust_pitch(-0.1)
    return jsonify({"status": "success", "gesture": gesture})

@app.route('/api/state', methods=['GET'])
def get_state():
    return jsonify({
        "volume": sound_controller.volume,
        "bass": sound_controller.bass,
        "tempo": sound_controller.tempo,
        "pitch": sound_controller.pitch
    })

@app.route('/api/gesture-frame', methods=['POST'])
def gesture_frame():
    data = request.json
    frame_data = data.get('frame')
    if frame_data:
        # Remove header: "data:image/jpeg;base64,"
        imgstr = frame_data.split(',')[1]
        img_bytes = base64.b64decode(imgstr)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # --- Your gesture prediction logic here ---
        # result = your_gesture_predict_function(img)
        # return jsonify({"gesture": result})
        print("Received frame for gesture prediction.")
        return jsonify({"status": "frame received"})
    return jsonify({"error": "No frame"}), 400

if __name__ == "__main__":
    app.run(debug=False, port=5000)
