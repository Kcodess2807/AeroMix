import cv2
import mediapipe as mp
import numpy as np
import time

class GestureDetector:
    def __init__(self):
        print("GestureDetector: Initializing MediaPipe Hands...")
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.last_landmarks = None
        self.last_detection_time = 0

    def reinitialize(self):
        print("GestureDetector: Reinitializing MediaPipe Hands...")
        if hasattr(self, 'hands') and self.hands is not None:
            try:
                self.hands.close()
            except Exception as e:
                print(f"Warning (hands.close): {e}")
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1, #as of now, considering single hand
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    def detect_landmarks(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        annotated_frame = frame.copy()
        landmarks_dict = {"pose": [], "left_hand": [], "right_hand": []}
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                handedness = "left_hand"
                if results.multi_handedness and len(results.multi_handedness) > idx:
                    handedness = "left_hand" if results.multi_handedness[idx].classification[0].label == "Left" else "right_hand"
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
        return landmarks_dict, annotated_frame

    def get_landmark_features(self, landmarks_dict):
        features = []
        for hand in ['left_hand', 'right_hand']:
            if hand in landmarks_dict and landmarks_dict[hand]:
                for lm in landmarks_dict[hand]:
                    features.extend([lm['x'], lm['y'], lm['z']])
        return np.array(features)

    def release(self):
        print("GestureDetector: Releasing MediaPipe Hands...")
        if hasattr(self, 'hands') and self.hands is not None:
            try:
                self.hands.close()
            except Exception as e:
                print(f"Warning (hands.close): {e}")
