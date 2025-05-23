import cv2
import mediapipe as mp
import numpy as np
import time
import traceback

class GestureDetector:
    def __init__(self):
        print("GestureDetector: Initializing MediaPipe Hands...")
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        try:
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,  # Increased from 1
                min_detection_confidence=0.5,  # Reduced from 0.7
                min_tracking_confidence=0.5    # Reduced from 0.7
            )

            print("GestureDetector: MediaPipe Hands initialized successfully")
        except Exception as e:
            print(f"[ERROR] Failed to initialize MediaPipe Hands: {e}")
            print("[ERROR] Stack trace:")
            traceback.print_exc()
            self.hands = None
        self.last_landmarks = None
        self.last_detection_time = 0

    def reinitialize(self):
        print("GestureDetector: Reinitializing MediaPipe Hands...")
        if hasattr(self, 'hands') and self.hands is not None:
            try:
                self.hands.close()
            except Exception as e:
                print(f"Warning (hands.close): {e}")
        try:
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            )
            print("GestureDetector: MediaPipe Hands reinitialized successfully")
        except Exception as e:
            print(f"[ERROR] Failed to reinitialize MediaPipe Hands: {e}")
            print("[ERROR] Stack trace:")
            traceback.print_exc()
            self.hands = None

    def detect_landmarks(self, frame):
        print("[DEBUG] Starting detect_landmarks...")
        print("[DEBUG] Frame shape:", frame.shape)
        print("[DEBUG] Frame dtype:", frame.dtype)

        if self.hands is None:
            print("[ERROR] MediaPipe Hands not initialized")
            return {"pose": [], "left_hand": [], "right_hand": []}, frame.copy()

        # Preprocess frame to improve detection
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            print("[DEBUG] Frame converted to RGB, shape:", frame_rgb.shape)
        except Exception as e:
            print(f"[ERROR] Failed to convert frame to RGB: {e}")
            print("[ERROR] Stack trace:")
            traceback.print_exc()
            return {"pose": [], "left_hand": [], "right_hand": []}, frame.copy()

        try:
            frame_rgb = cv2.convertScaleAbs(frame_rgb, alpha=1.2, beta=10)  # Increase contrast
            print("[DEBUG] Frame contrast adjusted")
        except Exception as e:
            print(f"[ERROR] Failed to adjust frame contrast: {e}")
            print("[ERROR] Stack trace:")
            traceback.print_exc()
            return {"pose": [], "left_hand": [], "right_hand": []}, frame.copy()

        try:
            results = self.hands.process(frame_rgb)
            print("[DEBUG] MediaPipe processing completed")
        except Exception as e:
            print(f"[ERROR] MediaPipe processing failed: {e}")
            print("[ERROR] Stack trace:")
            traceback.print_exc()
            return {"pose": [], "left_hand": [], "right_hand": []}, frame.copy()

        annotated_frame = frame.copy()
        landmarks_dict = {"pose": [], "left_hand": [], "right_hand": []}
        
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                handedness = "left_hand"
                if results.multi_handedness and len(results.multi_handedness) > idx:
                    handedness = "left_hand" if results.multi_handedness[idx].classification[0].label == "Left" else "right_hand"
                print(f"[DEBUG] Detected {handedness} with {len(hand_landmarks.landmark)} landmarks")
                for i, landmark in enumerate(hand_landmarks.landmark):
                    landmarks_dict[handedness].append({
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z
                    })
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
            self.last_landmarks = landmarks_dict
            self.last_detection_time = time.time()
        elif time.time() - self.last_detection_time < 0.5:
            landmarks_dict = self.last_landmarks
            print("[DEBUG] Using cached landmarks from last detection")
        else:
            print("[DEBUG] No hands detected in frame")

        print("[DEBUG] detect_landmarks completed, returning landmarks_dict")
        return landmarks_dict, annotated_frame

    def get_landmark_features(self, landmarks_dict):
        print("[DEBUG] Extracting features from landmarks_dict")
        features = []
        for hand in ['left_hand', 'right_hand']:
            if hand in landmarks_dict and landmarks_dict[hand]:
                print(f"[DEBUG] Processing {hand} with {len(landmarks_dict[hand])} landmarks")
                for lm in landmarks_dict[hand]:
                    features.extend([lm['x'], lm['y']])  # Exclude z-coordinate
        features_array = np.array(features)
        print("[DEBUG] Extracted features shape:", features_array.shape)
        return features_array

    def release(self):
        print("GestureDetector: Releasing MediaPipe Hands...")
        if hasattr(self, 'hands') and self.hands is not None:
            try:
                self.hands.close()
            except Exception as e:
                print(f"Warning (hands.close): {e}")