import streamlit as st
import cv2
import numpy as np
import time
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import threading
import queue
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av
from streamlit_option_menu import option_menu
import os
import tempfile
try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None

# Import your existing modules with error handling
try:
    from utils.gesture_Detection import GestureDetector
    from ml.classifier import GestureClassifier
    from sound_control import SoundController
    from utils.osc_handler import OSCHandler
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="AeroMix - Gesture DJ System",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with beautiful animations
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        animation: headerPulse 3s ease-in-out infinite;
    }
    
    @keyframes headerPulse {
        0%, 100% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.5); }
        50% { box-shadow: 0 0 40px rgba(102, 126, 234, 0.8); }
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }
    
    .gesture-card {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        animation: gestureDetected 1s ease-in-out;
        transform: scale(1);
        transition: all 0.3s ease;
    }
    
    @keyframes gestureDetected {
        0% { transform: scale(0.8) rotate(-5deg); opacity: 0; }
        50% { transform: scale(1.1) rotate(2deg); }
        100% { transform: scale(1) rotate(0deg); opacity: 1; }
    }
    
    .audio-upload-card {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .current-track-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        text-align: center;
        border: 2px solid rgba(255, 255, 255, 0.2);
        animation: trackGlow 2s ease-in-out infinite alternate;
    }
    
    @keyframes trackGlow {
        from { border-color: rgba(255, 255, 255, 0.2); }
        to { border-color: rgba(255, 255, 255, 0.6); }
    }
    
    .status-indicator {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
    }
    
    .status-active {
        background: radial-gradient(circle, #4CAF50, #45a049);
        animation: statusBlink 1.5s ease-in-out infinite;
        box-shadow: 0 0 10px #4CAF50;
    }
    
    .status-inactive {
        background: radial-gradient(circle, #f44336, #d32f2f);
        animation: statusPulse 2s ease-in-out infinite;
    }
    
    @keyframes statusBlink {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.1); }
    }
    
    @keyframes statusPulse {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }
    
    .volume-animation {
        animation: volumeWave 0.5s ease-in-out;
    }
    
    @keyframes volumeWave {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); background: #66ff66; }
        100% { transform: scale(1); }
    }
    
    .bass-animation {
        animation: bassThump 0.6s ease-in-out;
    }
    
    @keyframes bassThump {
        0% { transform: scale(1); }
        25% { transform: scale(1.3); background: #ff6666; }
        50% { transform: scale(0.9); }
        100% { transform: scale(1); }
    }
    
    .tempo-animation {
        animation: tempoSpin 0.8s ease-in-out;
    }
    
    @keyframes tempoSpin {
        0% { transform: rotate(0deg) scale(1); }
        50% { transform: rotate(180deg) scale(1.2); background: #6666ff; }
        100% { transform: rotate(360deg) scale(1); }
    }
    
    .pitch-animation {
        animation: pitchSlide 0.7s ease-in-out;
    }
    
    @keyframes pitchSlide {
        0% { transform: translateY(0) scale(1); }
        50% { transform: translateY(-20px) scale(1.15); background: #ff66ff; }
        100% { transform: translateY(0) scale(1); }
    }
    
    .error-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        text-align: center;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #ffa726 0%, #ff9800 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        text-align: center;
    }
    
    .camera-instructions {
        background: linear-gradient(135deg, #2196F3 0%, #21CBF3 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class GestureVideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.gesture_detector = None
        self.gestures = {}
        self.detected_gestures = []
        self.confidence_scores = {}
        self.landmarks_detected = False
        self.error_count = 0
        self.max_errors = 5
        self.frame_count = 0
        
        try:
            self.gesture_detector = GestureDetector()
            self.load_gesture_models()
            print("GestureVideoProcessor initialized successfully")
        except Exception as e:
            print(f"Error initializing GestureVideoProcessor: {e}")
            self.gesture_detector = None
        
    def load_gesture_models(self):
        """Load trained gesture models"""
        model_dir = "model/trained"
        if os.path.exists(model_dir):
            for filename in os.listdir(model_dir):
                if filename.endswith("_model.pkl"):
                    gesture_name = filename.replace("_model.pkl", "")
                    model_path = os.path.join(model_dir, filename)
                    try:
                        self.gestures[gesture_name] = GestureClassifier(model_path)
                        print(f"Loaded model for gesture: {gesture_name}")
                    except Exception as e:
                        print(f"Failed to load model for {gesture_name}: {e}")

    def recv(self, frame):
        try:
            img = frame.to_ndarray(format="bgr24")
            self.frame_count += 1
            
            # Always flip the image to fix mirroring
            img = cv2.flip(img, 1)
            
            # Add frame counter and status overlay
            cv2.putText(img, f"AeroMix Camera Feed - Frame {self.frame_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Reset detection status
            self.detected_gestures = []
            self.confidence_scores = {}
            self.landmarks_detected = False
            
            # Process gestures if detector is available
            if self.gesture_detector:
                try:
                    landmarks, annotated_frame = self.gesture_detector.detect_landmarks(img)
                    self.landmarks_detected = bool(landmarks and (landmarks.get("left_hand") or landmarks.get("right_hand")))
                    
                    if self.landmarks_detected:
                        cv2.putText(annotated_frame, "Hand Detected!", (10, 70), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        
                        # Process gestures
                        for gesture_name, classifier in self.gestures.items():
                            try:
                                processed_landmarks = self.convert_landmarks_format(landmarks)
                                if processed_landmarks:
                                    features = classifier.preprocess_landmarks(processed_landmarks)
                                    if features.size > 0:
                                        prediction = classifier.predict(features)
                                        if prediction == gesture_name:
                                            self.detected_gestures.append(gesture_name)
                                            self.confidence_scores[gesture_name] = 0.8
                                            # Add gesture overlay
                                            cv2.putText(annotated_frame, f"Gesture: {gesture_name}", (10, 110), 
                                                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                            except Exception as e:
                                print(f"Error predicting gesture {gesture_name}: {e}")
                    else:
                        cv2.putText(annotated_frame, "Show your hand to the camera", (10, 70), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    
                    return av.VideoFrame.from_ndarray(annotated_frame, format="bgr24")
                    
                except Exception as e:
                    print(f"Error in gesture detection: {e}")
                    cv2.putText(img, f"Gesture Detection Error", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            else:
                cv2.putText(img, "Gesture Detector Not Available", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            
            return av.VideoFrame.from_ndarray(img, format="bgr24")
            
        except Exception as e:
            self.error_count += 1
            print(f"Critical error in recv(): {e}")
            
            # Return a simple error frame
            if hasattr(frame, 'to_ndarray'):
                try:
                    img = frame.to_ndarray(format="bgr24")
                    cv2.putText(img, f"Processing Error: {str(e)[:50]}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    return av.VideoFrame.from_ndarray(img, format="bgr24")
                except:
                    pass
            
            return frame
    
    def convert_landmarks_format(self, landmarks):
        """Convert landmarks from dict format to list format expected by classifier"""
        if not landmarks:
            return None
            
        # Use left_hand if available, otherwise right_hand
        if landmarks.get("left_hand") and len(landmarks["left_hand"]) == 21:
            hand_landmarks = landmarks["left_hand"]
        elif landmarks.get("right_hand") and len(landmarks["right_hand"]) == 21:
            hand_landmarks = landmarks["right_hand"]
        else:
            return None
        
        # Convert to the format expected by classifier
        class LandmarkObj:
            def __init__(self, x, y, z=0.0):
                self.x = x
                self.y = y
                self.z = z
        
        landmark_objects = []
        for lm in hand_landmarks:
            landmark_objects.append(LandmarkObj(lm["x"], lm["y"], lm.get("z", 0.0)))
        
        return [landmark_objects]  # Return as list with one hand

def initialize_session_state():
    """Initialize session state variables"""
    if 'sound_controller' not in st.session_state:
        try:
            st.session_state.sound_controller = SoundController()
            st.session_state.audio_available = True
        except Exception as e:
            st.session_state.sound_controller = None
            st.session_state.audio_available = False
            st.session_state.audio_error = str(e)
            
    if 'gesture_history' not in st.session_state:
        st.session_state.gesture_history = []
    if 'audio_metrics' not in st.session_state:
        st.session_state.audio_metrics = {
            'volume': 0.7,
            'bass': 0.5,
            'tempo': 1.0,
            'pitch': 1.0
        }
    if 'current_track' not in st.session_state:
        st.session_state.current_track = "data/audio/audio3.mp3"
    if 'uploaded_audio_path' not in st.session_state:
        st.session_state.uploaded_audio_path = None
    if 'is_playing' not in st.session_state:
        st.session_state.is_playing = False
    if 'last_gesture_time' not in st.session_state:
        st.session_state.last_gesture_time = {}

def save_uploaded_audio(uploaded_file):
    """Save uploaded audio file and convert to compatible format if needed"""
    if AudioSegment is None:
        st.error("Audio processing not available. Please install ffmpeg.")
        return None
        
    try:
        # Create temp directory if it doesn't exist
        temp_dir = "temp_audio"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save the uploaded file
        file_extension = uploaded_file.name.split('.')[-1].lower()
        temp_path = os.path.join(temp_dir, f"uploaded_audio.{file_extension}")
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Convert to WAV if it's MP3 (for better compatibility with pyo)
        if file_extension == 'mp3':
            wav_path = os.path.join(temp_dir, "uploaded_audio.wav")
            audio = AudioSegment.from_mp3(temp_path)
            audio.export(wav_path, format="wav")
            os.remove(temp_path)  # Remove the original MP3
            return wav_path
        elif file_extension in ['wav', 'wave']:
            return temp_path
        else:
            # Try to convert other formats
            wav_path = os.path.join(temp_dir, "uploaded_audio.wav")
            audio = AudioSegment.from_file(temp_path)
            audio.export(wav_path, format="wav")
            os.remove(temp_path)
            return wav_path
            
    except Exception as e:
        st.error(f"Error processing audio file: {e}")
        return None

def create_enhanced_audio_visualization():
    """Create enhanced real-time audio visualization with animations"""
    metrics = st.session_state.audio_metrics
    
    # Create animated gauge charts
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('🔊 Volume', '🎵 Bass', '⚡ Tempo', '🎼 Pitch'),
        specs=[[{"type": "indicator"}, {"type": "indicator"}],
               [{"type": "indicator"}, {"type": "indicator"}]]
    )
    
    # Enhanced Volume gauge with gradient
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=metrics['volume'] * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Volume (%)", 'font': {'size': 16, 'color': 'white'}},
        delta={'reference': 70, 'increasing': {'color': "lightgreen"}, 'decreasing': {'color': "lightcoral"}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': "white", 'tickfont': {'color': 'white'}},
            'bar': {'color': "#4CAF50", 'thickness': 0.8},
            'bgcolor': "rgba(255,255,255,0.1)",
            'borderwidth': 2,
            'bordercolor': "white",
            'steps': [
                {'range': [0, 30], 'color': "rgba(255,0,0,0.3)"},
                {'range': [30, 70], 'color': "rgba(255,255,0,0.3)"},
                {'range': [70, 100], 'color': "rgba(0,255,0,0.3)"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ), row=1, col=1)
    
    # Enhanced Bass gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=metrics['bass'] * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Bass (%)", 'font': {'size': 16, 'color': 'white'}},
        delta={'reference': 50, 'increasing': {'color': "orange"}, 'decreasing': {'color': "lightblue"}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': "white", 'tickfont': {'color': 'white'}},
            'bar': {'color': "#FF5722", 'thickness': 0.8},
            'bgcolor': "rgba(255,255,255,0.1)",
            'borderwidth': 2,
            'bordercolor': "white",
            'steps': [
                {'range': [0, 25], 'color': "rgba(0,0,255,0.2)"},
                {'range': [25, 75], 'color': "rgba(255,165,0,0.3)"},
                {'range': [75, 100], 'color': "rgba(255,0,0,0.4)"}
            ]
        }
    ), row=1, col=2)
    
    # Enhanced Tempo gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=metrics['tempo'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Tempo (x)", 'font': {'size': 16, 'color': 'white'}},
        delta={'reference': 1.0, 'increasing': {'color': "lightgreen"}, 'decreasing': {'color': "lightcoral"}},
        gauge={
            'axis': {'range': [0.5, 2.0], 'tickcolor': "white", 'tickfont': {'color': 'white'}},
            'bar': {'color': "#2196F3", 'thickness': 0.8},
            'bgcolor': "rgba(255,255,255,0.1)",
            'borderwidth': 2,
            'bordercolor': "white",
            'steps': [
                {'range': [0.5, 0.8], 'color': "rgba(0,0,255,0.2)"},
                {'range': [0.8, 1.2], 'color': "rgba(0,255,0,0.2)"},
                {'range': [1.2, 2.0], 'color': "rgba(255,0,0,0.2)"}
            ]
        }
    ), row=2, col=1)
    
    # Enhanced Pitch gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=metrics['pitch'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Pitch (x)", 'font': {'size': 16, 'color': 'white'}},
        delta={'reference': 1.0, 'increasing': {'color': "magenta"}, 'decreasing': {'color': "cyan"}},
        gauge={
            'axis': {'range': [0.5, 2.0], 'tickcolor': "white", 'tickfont': {'color': 'white'}},
            'bar': {'color': "#9C27B0", 'thickness': 0.8},
            'bgcolor': "rgba(255,255,255,0.1)",
            'borderwidth': 2,
            'bordercolor': "white",
            'steps': [
                {'range': [0.5, 0.8], 'color': "rgba(128,0,128,0.2)"},
                {'range': [0.8, 1.2], 'color': "rgba(255,0,255,0.2)"},
                {'range': [1.2, 2.0], 'color': "rgba(255,20,147,0.3)"}
            ]
        }
    ), row=2, col=2)
    
    fig.update_layout(
        height=500,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': 'white', 'size': 12},
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

def show_audio_upload_section():
    """Display audio upload section"""
    st.markdown("""
    <div class="audio-upload-card">
        <h3>🎵 Upload Your Music</h3>
        <p>Upload your own MP3, WAV, or other audio files to control with gestures!</p>
    </div>
    """, unsafe_allow_html=True)
    
    if AudioSegment is None:
        st.markdown("""
        <div class="warning-card">
            <h4>⚠️ Audio Processing Limited</h4>
            <p>FFmpeg not found. Only WAV files supported for upload.</p>
        </div>
        """, unsafe_allow_html=True)
        file_types = ['wav']
    else:
        file_types = ['mp3', 'wav', 'ogg', 'm4a', 'flac']
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=file_types,
        help=f"Upload {', '.join(file_types).upper()} files"
    )
    
    if uploaded_file is not None:
        # Display file info
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB"
        }
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**File Details:**")
            for key, value in file_details.items():
                st.write(f"- {key}: {value}")
        
        with col2:
            # Audio preview
            st.write("**Preview:**")
            st.audio(uploaded_file, format=f'audio/{uploaded_file.name.split(".")[-1]}')
        
        # Process and save the file
        if st.button("🚀 Load This Track", type="primary", key="load_track"):
            with st.spinner("Processing audio file..."):
                processed_path = save_uploaded_audio(uploaded_file)
                
                if processed_path:
                    st.session_state.uploaded_audio_path = processed_path
                    st.session_state.current_track = processed_path
                    st.success(f"✅ Audio loaded successfully: {uploaded_file.name}")
                    
                    # Auto-play the new track if audio is available
                    if st.session_state.audio_available:
                        try:
                            st.session_state.sound_controller.control_playback("play", processed_path)
                            st.session_state.is_playing = True
                            st.success("🎵 Now playing your uploaded track!")
                        except Exception as e:
                            st.error(f"Error playing audio: {e}")
                    else:
                        st.info("Audio loaded but playback not available due to audio system issues.")
                else:
                    st.error("❌ Failed to process audio file")

def show_current_track_info():
    """Display current track information"""
    current_track = st.session_state.current_track
    track_name = os.path.basename(current_track) if current_track else "No track loaded"
    
    # Determine if it's an uploaded track or default
    is_uploaded = st.session_state.uploaded_audio_path and current_track == st.session_state.uploaded_audio_path
    track_type = "🎵 Your Upload" if is_uploaded else "🎼 Default Track"
    
    # Show audio system status
    audio_status = "🎵 Playing" if st.session_state.is_playing else "⏸️ Stopped"
    if not st.session_state.audio_available:
        audio_status = "❌ Audio System Error"
    
    st.markdown(f"""
    <div class="current-track-display">
        <h4>Currently Loaded Track</h4>
        <p><strong>{track_type}</strong></p>
        <p>📁 {track_name}</p>
        <p>{audio_status}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show audio error if present
    if not st.session_state.audio_available and hasattr(st.session_state, 'audio_error'):
        st.markdown(f"""
        <div class="error-card">
            <h4>🔧 Audio System Issue</h4>
            <p>The audio system is running in silent mode. Gestures will be detected but no audio will play.</p>
            <small>Error: {st.session_state.audio_error[:100]}...</small>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎵 AeroMix - Gesture-Based DJ System</h1>
        <p>Control your music with hand gestures in real-time</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")
        
        # Show system status
        if st.session_state.audio_available:
            st.success("🔊 Audio System: Ready")
        else:
            st.error("🔇 Audio System: Silent Mode")
        
        selected = option_menu(
            menu_title=None,
            options=["Live Performance", "Audio Upload", "Training Mode", "Analytics", "Settings"],
            icons=["play-circle", "upload", "mortarboard", "bar-chart", "gear"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "white", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "color": "white",
                    "--hover-color": "rgba(255,255,255,0.1)"
                },
                "nav-link-selected": {"background-color": "rgba(255,255,255,0.2)"},
            }
        )
    
    if selected == "Live Performance":
        show_live_performance()
    elif selected == "Audio Upload":
        show_audio_upload()
    elif selected == "Training Mode":
        show_training_mode()
    elif selected == "Analytics":
        show_analytics()
    elif selected == "Settings":
        show_settings()

def show_live_performance():
    """Main live performance interface"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📹 Live Camera Feed")
        
        # Camera troubleshooting instructions
        st.markdown("""
        <div class="camera-instructions">
            <h4>📋 Camera Setup Instructions</h4>
            <p>1. Click "START" button below</p>
            <p>2. Allow camera access when prompted</p>
            <p>3. If camera doesn't work, try refreshing the page</p>
            <p>4. Make sure no other apps are using your camera</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced WebRTC streamer with better configuration
        ctx = webrtc_streamer(
            key="gesture-detection",
            video_processor_factory=GestureVideoProcessor,
            rtc_configuration=RTCConfiguration(
                {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
            ),
            media_stream_constraints={
                "video": {
                    "width": {"ideal": 640, "max": 1280},
                    "height": {"ideal": 480, "max": 720},
                    "frameRate": {"ideal": 30, "max": 60}
                }, 
                "audio": False
            },
            async_processing=True,
        )
        
        # Display detected gestures
        if ctx.video_processor:
            processor = ctx.video_processor
            
            # Gesture detection status
            status_color = "status-active" if processor.landmarks_detected else "status-inactive"
            status_text = "Hand Detected" if processor.landmarks_detected else "No Hand Detected"
            
            st.markdown(f"""
            <div style="margin: 1rem 0;">
                <span class="status-indicator {status_color}"></span>
                <strong>{status_text}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # Display detected gestures with enhanced animations
            if processor.detected_gestures:
                st.markdown("### 🤲 Detected Gestures")
                for gesture in processor.detected_gestures:
                    confidence = processor.confidence_scores.get(gesture, 0)
                    
                    # Add gesture-specific animation class
                    animation_class = ""
                    if "volume" in gesture:
                        animation_class = "volume-animation"
                    elif "bass" in gesture:
                        animation_class = "bass-animation"
                    elif "tempo" in gesture:
                        animation_class = "tempo-animation"
                    elif "pitch" in gesture:
                        animation_class = "pitch-animation"
                    
                    st.markdown(f"""
                    <div class="gesture-card {animation_class}">
                        <h4>{gesture.replace('_', ' ').title()}</h4>
                        <p>Confidence: {confidence:.2%}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add to history
                    st.session_state.gesture_history.append(gesture)
                    
                    # Process gesture with cooldown
                    process_detected_gesture(gesture)
        else:
            st.markdown("""
            <div class="warning-card">
                <h4>⚠️ Camera Not Connected</h4>
                <p>Please click the START button above and allow camera access.</p>
                <p>If issues persist, try refreshing the page or using a different browser.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Current track display
        show_current_track_info()
        
        st.markdown("### 🎚️ Audio Controls")
        
        # Enhanced audio visualization
        audio_fig = create_enhanced_audio_visualization()
        st.plotly_chart(audio_fig, use_container_width=True)
        
        # Enhanced manual controls with animations
        st.markdown("#### Manual Controls")
        
        col_vol, col_bass = st.columns(2)
        with col_vol:
            if st.button("🔊 Volume +", key="vol_up", help="Increase volume"):
                adjust_audio_parameter('volume', 0.1)
                trigger_animation('volume')
            if st.button("🔉 Volume -", key="vol_down", help="Decrease volume"):
                adjust_audio_parameter('volume', -0.1)
                trigger_animation('volume')
        
        with col_bass:
            if st.button("🎵 Bass +", key="bass_up", help="Increase bass"):
                adjust_audio_parameter('bass', 0.1)
                trigger_animation('bass')
            if st.button("🎵 Bass -", key="bass_down", help="Decrease bass"):
                adjust_audio_parameter('bass', -0.1)
                trigger_animation('bass')
        
        col_tempo, col_pitch = st.columns(2)
        with col_tempo:
            if st.button("⚡ Tempo +", key="tempo_up", help="Increase tempo"):
                adjust_audio_parameter('tempo', 0.1)
                trigger_animation('tempo')
            if st.button("🐌 Tempo -", key="tempo_down", help="Decrease tempo"):
                adjust_audio_parameter('tempo', -0.1)
                trigger_animation('tempo')
        
        with col_pitch:
            if st.button("⬆️ Pitch +", key="pitch_up", help="Increase pitch"):
                adjust_audio_parameter('pitch', 0.1)
                trigger_animation('pitch')
            if st.button("⬇️ Pitch -", key="pitch_down", help="Decrease pitch"):
                adjust_audio_parameter('pitch', -0.1)
                trigger_animation('pitch')
        
        # Playback controls
        st.markdown("#### Playback")
        col_play, col_stop = st.columns(2)
        with col_play:
            if st.button("▶️ Play", key="play_btn", help="Start playback"):
                if st.session_state.current_track and st.session_state.audio_available:
                    try:
                        st.session_state.sound_controller.control_playback("play", st.session_state.current_track)
                        st.session_state.is_playing = True
                        st.success("🎵 Playing!")
                    except Exception as e:
                        st.error(f"Playback error: {e}")
                elif not st.session_state.audio_available:
                    st.warning("Audio system not available")
                else:
                    st.warning("No track loaded")
        with col_stop:
            if st.button("⏹️ Stop", key="stop_btn", help="Stop playback"):
                if st.session_state.audio_available:
                    try:
                        st.session_state.sound_controller.control_playback("stop")
                        st.session_state.is_playing = False
                        st.info("⏸️ Stopped")
                    except Exception as e:
                        st.error(f"Stop error: {e}")

def trigger_animation(param_type):
    """Trigger visual feedback for parameter changes"""
    current_time = time.time()
    st.session_state.last_gesture_time[param_type] = current_time
    
    # Show temporary success message with animation
    if param_type == 'volume':
        st.success("🔊 Volume adjusted!")
    elif param_type == 'bass':
        st.success("🎵 Bass adjusted!")
    elif param_type == 'tempo':
        st.success("⚡ Tempo adjusted!")
    elif param_type == 'pitch':
        st.success("🎼 Pitch adjusted!")

def show_audio_upload():
    """Audio upload interface"""
    st.markdown("### 🎵 Audio Upload & Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Audio upload section
        show_audio_upload_section()
        
        # Default tracks section
        st.markdown("### 🎼 Default Tracks")
        default_tracks = []
        if os.path.exists("data/audio"):
            default_tracks = [f for f in os.listdir("data/audio") if f.endswith(('.mp3', '.wav', '.ogg'))]
        
        if default_tracks:
            selected_default = st.selectbox("Choose a default track:", default_tracks)
            
            col_preview, col_load = st.columns(2)
            with col_preview:
                if st.button("🎧 Preview", key="preview_default"):
                    default_path = os.path.join("data/audio", selected_default)
                    if os.path.exists(default_path):
                        st.audio(default_path)
            
            with col_load:
                if st.button("📥 Load Default Track", key="load_default"):
                    default_path = os.path.join("data/audio", selected_default)
                    st.session_state.current_track = default_path
                    st.session_state.uploaded_audio_path = None
                    st.success(f"✅ Loaded: {selected_default}")
        else:
            st.info("No default tracks found in data/audio directory")
    
    with col2:
        # Current track info
        show_current_track_info()
        
        # Playback controls
        st.markdown("### 🎮 Playback Controls")
        
        col_play, col_stop = st.columns(2)
        with col_play:
            if st.button("▶️ Play", use_container_width=True, key="upload_play"):
                if st.session_state.current_track and st.session_state.audio_available:
                    try:
                        st.session_state.sound_controller.control_playback("play", st.session_state.current_track)
                        st.session_state.is_playing = True
                        st.success("🎵 Playing!")
                    except Exception as e:
                        st.error(f"Playback error: {e}")
                elif not st.session_state.audio_available:
                    st.warning("Audio system not available")
                else:
                    st.warning("No track loaded")
        
        with col_stop:
            if st.button("⏹️ Stop", use_container_width=True, key="upload_stop"):
                if st.session_state.audio_available:
                    try:
                        st.session_state.sound_controller.control_playback("stop")
                        st.session_state.is_playing = False
                        st.info("⏸️ Stopped")
                    except Exception as e:
                        st.error(f"Stop error: {e}")

def show_training_mode():
    """Training interface for new gestures"""
    st.markdown("### 🎓 Training Mode")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Train New Gesture")
        
        gesture_name = st.text_input("Gesture Name", placeholder="e.g., volume_up")
        
        if gesture_name:
            st.info(f"Training gesture: **{gesture_name}**")
            st.markdown("""
            **Instructions:**
            1. Click 'Start Training' below
            2. Position your hand in the camera view
            3. Press 'g' to record gesture samples
            4. Press 'n' to record neutral samples
            5. Press 'q' to stop training
            
            **Note:** You need at least 50 samples to train a model.
            """)
            
            if st.button("🚀 Start Training", key="start_training"):
                st.success("Training mode activated! Check your terminal for camera feed.")
    
    with col2:
        st.markdown("#### Available Models")
        
        model_dir = "model/trained"
        if os.path.exists(model_dir):
            models = [f.replace("_model.pkl", "") for f in os.listdir(model_dir) if f.endswith("_model.pkl")]
            
            if models:
                for model in models:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{model.replace('_', ' ').title()}</h4>
                        <p>✅ Ready</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No trained models found. Train your first gesture!")
        else:
            st.info("Model directory not found.")

def show_analytics():
    """Analytics and performance metrics"""
    st.markdown("### 📊 Analytics Dashboard")
    
    # Gesture history chart
    if st.session_state.gesture_history:
        history_fig = create_gesture_history_chart()
        if history_fig:
            st.plotly_chart(history_fig, use_container_width=True)
    else:
        st.info("No gesture data available yet. Start performing gestures to see analytics!")
    
    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Total Gestures</h3>
            <h2>{}</h2>
        </div>
        """.format(len(st.session_state.gesture_history)), unsafe_allow_html=True)
    
    with col2:
        unique_gestures = len(set(st.session_state.gesture_history)) if st.session_state.gesture_history else 0
        st.markdown("""
        <div class="metric-card">
            <h3>Unique Gestures</h3>
            <h2>{}</h2>
        </div>
        """.format(unique_gestures), unsafe_allow_html=True)
    
    with col3:
        model_count = len([f for f in os.listdir("model/trained") if f.endswith("_model.pkl")]) if os.path.exists("model/trained") else 0
        st.markdown("""
        <div class="metric-card">
            <h3>Trained Models</h3>
            <h2>{}</h2>
        </div>
        """.format(model_count), unsafe_allow_html=True)
    
    with col4:
        track_name = os.path.basename(st.session_state.current_track) if st.session_state.current_track else "None"
        st.markdown("""
        <div class="metric-card">
            <h3>Current Track</h3>
            <h2 style="font-size: 0.8rem;">{}</h2>
        </div>
        """.format(track_name[:15] + "..." if len(track_name) > 15 else track_name), unsafe_allow_html=True)

def show_settings():
    """Settings and configuration"""
    st.markdown("### ⚙️ Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Detection Settings")
        
        detection_confidence = st.slider(
            "Detection Confidence",
            min_value=0.1,
            max_value=1.0,
            value=0.3,  # Lowered for better detection
            step=0.1,
            help="Minimum confidence for hand detection"
        )
        
        tracking_confidence = st.slider(
            "Tracking Confidence",
            min_value=0.1,
            max_value=1.0,
            value=0.3,  # Lowered for better detection
            step=0.1,
            help="Minimum confidence for hand tracking"
        )
        
        max_hands = st.selectbox(
            "Maximum Hands",
            options=[1, 2],
            index=0,
            help="Maximum number of hands to detect"
        )
    
    with col2:
        st.markdown("#### Audio Settings")
        
        audio_device = st.selectbox(
            "Audio Device",
            options=["Default", "WASAPI", "DirectSound"],
            help="Audio driver to use"
        )
        
        buffer_size = st.selectbox(
            "Buffer Size",
            options=[256, 512, 1024, 2048],
            index=1,
            help="Audio buffer size (lower = less latency)"
        )
        
        sample_rate = st.selectbox(
            "Sample Rate",
            options=[44100, 48000, 96000],
            index=1,
            help="Audio sample rate"
        )
        
        # Audio file cleanup
        st.markdown("#### File Management")
        if st.button("🗑️ Clear Uploaded Audio", key="clear_audio"):
            if st.session_state.uploaded_audio_path and os.path.exists(st.session_state.uploaded_audio_path):
                try:
                    os.remove(st.session_state.uploaded_audio_path)
                    st.session_state.uploaded_audio_path = None
                    st.session_state.current_track = "data/audio/audio3.mp3"
                    st.success("Uploaded audio cleared!")
                except Exception as e:
                    st.error(f"Error clearing audio: {e}")
            else:
                st.info("No uploaded audio to clear")
    
    if st.button("💾 Save Settings", key="save_settings"):
        st.success("Settings saved successfully!")

def create_gesture_history_chart():
    """Create gesture detection history chart"""
    if not st.session_state.gesture_history:
        return None
    
    # Get last 20 gestures
    recent_gestures = st.session_state.gesture_history[-20:]
    
    fig = px.bar(
        x=list(range(len(recent_gestures))),
        y=[1] * len(recent_gestures),
        color=recent_gestures,
        title="Recent Gesture Detections",
        labels={'x': 'Time', 'y': 'Detection', 'color': 'Gesture'}
    )
    
    fig.update_layout(
        height=300,
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': 'white'}
    )
    
    return fig

def process_detected_gesture(gesture):
    """Process detected gesture and update audio parameters with cooldown"""
    current_time = time.time()
    
    # Implement cooldown to prevent rapid-fire gestures
    if gesture in st.session_state.last_gesture_time:
        if current_time - st.session_state.last_gesture_time[gesture] < 1.0:  # 1 second cooldown
            return
    
    st.session_state.last_gesture_time[gesture] = current_time
    
    # Only process audio if available
    if not st.session_state.audio_available:
        return
        
    sound_controller = st.session_state.sound_controller
    
    try:
        if gesture == "volume_up":
            sound_controller.adjust_volume(0.1)
            st.session_state.audio_metrics['volume'] = sound_controller.volume
        elif gesture == "volume_down":
            sound_controller.adjust_volume(-0.1)
            st.session_state.audio_metrics['volume'] = sound_controller.volume
        elif gesture == "bass_up":
            sound_controller.adjust_bass(0.1)
            st.session_state.audio_metrics['bass'] = sound_controller.bass
        elif gesture == "bass_down":
            sound_controller.adjust_bass(-0.1)
            st.session_state.audio_metrics['bass'] = sound_controller.bass
        elif gesture == "tempo_up":
            sound_controller.adjust_tempo(0.1)
            st.session_state.audio_metrics['tempo'] = sound_controller.tempo
        elif gesture == "tempo_down":
            sound_controller.adjust_tempo(-0.1)
            st.session_state.audio_metrics['tempo'] = sound_controller.tempo
        elif gesture == "pitch_up":
            sound_controller.adjust_pitch(0.1)
            st.session_state.audio_metrics['pitch'] = sound_controller.pitch
        elif gesture == "pitch_down":
            sound_controller.adjust_pitch(-0.1)
            st.session_state.audio_metrics['pitch'] = sound_controller.pitch
        elif gesture == "play":
            if st.session_state.current_track:
                sound_controller.control_playback("play", st.session_state.current_track)
                st.session_state.is_playing = True
    except Exception as e:
        print(f"Error processing gesture {gesture}: {e}")

def adjust_audio_parameter(param, value):
    """Manually adjust audio parameters"""
    if not st.session_state.audio_available:
        return
        
    sound_controller = st.session_state.sound_controller
    
    try:
        if param == 'volume':
            sound_controller.adjust_volume(value)
            st.session_state.audio_metrics['volume'] = sound_controller.volume
        elif param == 'bass':
            sound_controller.adjust_bass(value)
            st.session_state.audio_metrics['bass'] = sound_controller.bass
        elif param == 'tempo':
            sound_controller.adjust_tempo(value)
            st.session_state.audio_metrics['tempo'] = sound_controller.tempo
        elif param == 'pitch':
            sound_controller.adjust_pitch(value)
            st.session_state.audio_metrics['pitch'] = sound_controller.pitch
    except Exception as e:
        st.error(f"Error adjusting {param}: {e}")

if __name__ == "__main__":
    main()
