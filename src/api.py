from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from sound_control import SoundController
from ml.classifier import GestureClassifier

#app initialized
app=Flask(__name__)
CORS(app)

#initializing the sound controller of mine
sound_controller=SoundController()

@app.route('/api/gesture', methods=['POST'])
def process_gesture():
    data= request.json
    gesture=data.get('gesture')

    #volume control
    if gesture=="volume_up":
        sound_controller.adjust_volume(0.1)
    elif gesture=="volume_down":
        sound_controller.adjust_volume(-0.1)
    
    #tempo control
    elif gesture=="tempo_up":
        sound_controller.adjust_tempo(0.1)
    elif gesture=="tempo_down":
        sound_controller.adjust_tempo(-0.1)
    
    #bass control
    elif gesture=="bass_up":
        sound_controller.adjust_bass(0.1)
    elif gesture=="bass_down":
        sound_controller.adjust_bass(-0.1)
    
    #pitch control
    elif gesture=="pitch_up":
        sound_controller.adjust_pitch(0.1)
    elif gesture=="pitch_down":
        sound_controller.adjust_pitch(-0.1)

    return jsonify({"status": "success", "gesture": gesture})

@app.route('/api/state', methods=['GET'])
def get_state():
    return jsonify({
        "volume": sound_controller.volume, 
        "bass": sound_controller.adjust_bass, 
        "tempo": sound_controller.adjust_tempo, 
        "pitch": sound_controller.adjust_pitch
    })

if __name__=="__main__":
    app.run(debug=True, port=5000)