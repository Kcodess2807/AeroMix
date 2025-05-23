import streamlit as st
import cv2
import time
from main import AeroMixApp

# Initialize the AeroMixApp
app = AeroMixApp(training_mode=False)

# Streamlit app title and description
st.title("AeroMix - Gesture-Based DJ System")
st.write("Control music playback using hand gestures detected via webcam.")

# Sidebar for controls and status
st.sidebar.header("Audio Controls")
volume = st.sidebar.slider("Volume", 0.0, 1.0, app.sound_controller.volume, 0.1, key="volume")
if volume != app.sound_controller.volume:
    app.sound_controller.adjust_volume(volume - app.sound_controller.volume)

tempo = st.sidebar.slider("Tempo", 0.5, 2.0, app.sound_controller.tempo, 0.1, key="tempo")
if tempo != app.sound_controller.tempo:
    app.sound_controller.adjust_tempo(tempo - app.sound_controller.tempo)

pitch = st.sidebar.slider("Pitch", 0.5, 2.0, app.sound_controller.pitch, 0.1, key="pitch")
if pitch != app.sound_controller.pitch:
    app.sound_controller.adjust_pitch(pitch - app.sound_controller.pitch)

bass = st.sidebar.slider("Bass", 0.0, 1.0, app.sound_controller.bass, 0.1, key="bass")
if bass != app.sound_controller.bass:
    app.sound_controller.adjust_bass(bass - app.sound_controller.bass)

# Placeholder for webcam feed
frame_placeholder = st.empty()

# Button to start/stop playback
if st.sidebar.button("Play/Stop"):
    if app.sound_controller.is_playing:
        app.sound_controller.control_playback("stop")
    else:
        app.sound_controller.control_playback("play", "data/audio/audio3.mp3")

# Display gesture recognition status
gesture_status = st.empty()

# Start webcam and gesture recognition
if app.start_webcam():
    while True:
        ret, frame = app.webcam.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        landmarks, annotated_frame = app.gesture_detector.detect_landmarks(frame)
        annotated_frame = app.enhanced_visualization(annotated_frame)
        
        # Convert frame for Streamlit display
        frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
        
        # Update gesture status (placeholder for detected gesture)
        if landmarks and (landmarks["left_hand"] or landmarks["right_hand"]):
            gesture_status.write("Gesture Detected - Processing...")
        else:
            gesture_status.write("No Gesture Detected")
        
        time.sleep(0.1)  # Control frame update rate

    app.stop_webcam()
else:
    st.error("Could not open webcam for gesture recognition.")
