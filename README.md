# AEROMIX

AEROMIX is a touchless DJ and sound control system that leverages computer vision and machine learning for real-time body gesture recognition. It allows users to control music features such as bass, volume, scratching, looping, and effects using intuitive body movements and gestures, creating a futuristic and interactive music experience.

## Features

- **Real-time gesture detection:** Uses advanced computer vision (OpenCV, YOLO, and MediaPipe) to recognize and interpret body movements instantly for seamless control.
- **Intuitive music controls:**
  - **Tempo:** Adjust the speed (BPM) of your tracks in real time, enabling smooth beatmatching and creative transitions.
  - **Pitch:** Change the pitch of audio independently or in sync with tempo, allowing for key changes, harmonic mixing, or vinyl-style effects.
  - **Effects:** Apply effects such as filters, echoes, and reverbs using hand gestures, adding dynamic expression to your mixes.
  - **Playback sequence:** Control track playback, trigger loops, jump to cue points, or rearrange song sections with intuitive gestures for live remixing.
- **Dynamic visualizer:** Visual feedback responds to both music and user gestures, enhancing the interactive experience.
- **Multi-hand detection:** Recognizes and processes multiple hands for advanced, multi-control interactions, enabling complex techniques and simultaneous feature adjustments.
- **Full body interaction:** Extends beyond hand gestures to incorporate full body movement for more expressive control.

## System Architecture

AEROMIX integrates Max/MSP and Python environments to create a powerful real-time gesture-based sound control system:

1. **Video Processing Pipeline:**
   - Live video streams are captured in Max/MSP
   - Google's MediaPipe framework extracts key body, hand, and facial landmarks
   - Landmark data is formatted as JSON and transmitted between environments

2. **Cross-Platform Communication:**
   - Open Sound Control (OSC) protocol creates a bridge between Max/MSP and Python
   - Enables fast, structured communication for real-time processing
   - Leverages Max/MSP's multimedia strengths with Python's machine learning capabilities

3. **Dual-Phase Operation:**
   - **Training Phase:** Landmark data is collected and used to train ML models for gesture classification
   - **Performance Phase:** Trained models classify incoming landmarks in real-time to control sound

4. **Gesture-to-Sound Mapping:**
   - Users can define custom mappings between detected gestures and sound parameters
   - Modular design allows flexible control over audio manipulation based on movement

The system's architecture ensures efficient data flow while maintaining the flexibility needed for interactive sound applications in both experimental and performance contexts.

## Project Structure

```
model/
    Contains YOLO model weights, configuration, and class names for gesture detection.
src/
    main_app.py - Core application script
    gesture_detection.py - Hand and body gesture detection module
    sound_control.py - Audio manipulation functions
    visualizer.py - Dynamic music visualization components
    ml_models/ - Machine learning models for gesture classification
    utils/ - Utility functions for data processing and OSC communication
max_msp/
    Contains Max/MSP patches for video capture and sound processing
requirements.txt
    Lists Python dependencies required to run the project.
README.md
    Project overview and instructions.
LICENSE
    Project license information.
```

## Getting Started

1. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Max/MSP:**
   - Install Max/MSP from [cycling74.com](https://cycling74.com/)
   - Open the main patch in the max_msp directory

3. **Download and place the required model files:**
   - Place YOLO model files in the `model` directory
   - Ensure MediaPipe models are accessible

4. **Run the system:**
   - Start the Max/MSP patch
   - Launch the Python backend:
     ```bash
     python src/main_app.py
     ```

5. **Training mode (optional):**
   - To train custom gesture recognition:
     ```bash
     python src/main_app.py --mode training
     ```

## Requirements

- Python 3.8+
- Max/MSP 8.0+
- Webcam or compatible video input device
- MediaPipe
- OpenCV
- YOLO (model files)
- PyTorch
- numpy, scipy, pandas

## Contributing

Contributions are welcome! Please open issues or submit pull requests to help improve AEROMIX.

## License

This project is licensed under the **MIT License**.

## Contact

For questions, feedback, or collaboration, feel free to reach out:
- **Name:** Arush Karnatak
- **Email:** [arushkarnatak1881@gmail.com](mailto:arushkarnatak1881@gmail.com)
