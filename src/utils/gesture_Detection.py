import cv2
import mediapipe as mp
import numpy as np
import time

class GestureDetector:
    def __init__(self):
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Configure MediaPipe Hands with good defaults for gesture recognition
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Store the last detected landmarks
        self.last_landmarks = None
        self.last_detection_time = 0
    

    def reinitialize(self):
        """Reinitialize the MediaPipe Hands object"""
        if hasattr(self, 'hands'):
            self.hands.close()
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )


    def detect_landmarks(self, frame):
        """
        Detect hand landmarks in a frame using MediaPipe
        
        Args:
            frame: OpenCV image in BGR format
            
        Returns:
            landmarks_dict: Dictionary with hand landmarks
            annotated_frame: Frame with landmarks drawn on it
        """
        # Convert BGR to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame with MediaPipe
        results = self.hands.process(frame_rgb)
        
        # Create a copy of the frame for drawing
        annotated_frame = frame.copy()
        
        # Initialize landmarks dictionary
        landmarks_dict = {"pose": [], "left_hand": [], "right_hand": []}
        
        # If hands are detected
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Determine if it's left or right hand
                handedness = "left_hand"
                if results.multi_handedness and len(results.multi_handedness) > idx:
                    handedness = "left_hand" if results.multi_handedness[idx].classification[0].label == "Left" else "right_hand"
                
                # Extract landmarks
                for i, landmark in enumerate(hand_landmarks.landmark):
                    landmarks_dict[handedness].append({
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z
                    })
                
                # Draw landmarks on the frame
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
            
            # Update the last detected landmarks
            self.last_landmarks = landmarks_dict
            self.last_detection_time = time.time()
        elif time.time() - self.last_detection_time < 0.5:
            # Use the last detected landmarks for a short period to avoid flickering
            landmarks_dict = self.last_landmarks
        
        return landmarks_dict, annotated_frame
    
    def get_landmark_features(self, landmarks_dict):
        """
        Extract features from landmarks for model training
        
        Args:
            landmarks_dict: Dictionary with hand landmarks
            
        Returns:
            features: Numpy array of features
        """
        features = []
        
        # Extract hand landmarks
        for hand in ['left_hand', 'right_hand']:
            if hand in landmarks_dict and landmarks_dict[hand]:
                for lm in landmarks_dict[hand]:
                    features.extend([lm['x'], lm['y'], lm['z']])
        
        return np.array(features)
    
    def release(self):
        """Release resources"""
        self.hands.close()
