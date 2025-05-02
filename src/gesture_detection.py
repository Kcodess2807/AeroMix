#This module will process video input and detect gestures:

import cv2
import mediapipe as mp
import numpy as np
import utils.osc_communication as osc

class GestureDetector:
    def __init__(self, use_mediapipe=True, use_yolo=False):
        self.use_mediapipe = use_mediapipe
        self.use_yolo = use_yolo
        
        if self.use_mediapipe:
            self.mp_holistic=mp.solution.hoslistic
            self.holistic=self.mp_holistic.Holistic(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        
    def process_frame(self, frame):
        if self.use_mediapipe:
            #converting BGR to RGB
            rgb_frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results=self.holistic.process(rgb_frame)

            #extracting landmarks
            landmarks=self.__extract_mediapipe_landmarks(results)
            return landmarks
        
        return None


    def _extract_mediapipe_landmarks(self, results):
        #extract and format the landmarks by mediapipe
        landmarks={}

        #process pose landmarks
        if results.pose_landmarks:
            pose_landmarks=[]
            for landmark in results.pose_landmarks.landmark:
                pose_landmarks.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                })
            landmarks['psoe']=pose_landmarks

        
        #proceesing landmarks for the left hand
        if results.left_hand_landmarks:
            left_hand_landmarks=[]
            for landmark in results.left_hand_landmarks.landmark:
                left_hand_landmarks.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                })
        

        #processing landmas for the right hand
        if results.right_hand_landmarks:
            right_hand_landmarks=[]
            for landmark in results.right_hand_landmarks.landmark:
                right_hand_landmarks.append({
                    'x': landmark.x,
                    'y': landmark.y, 
                    'z': landmark.z,
                    'visibility': landmark.visibility
                })
        
        return landmarks
    
    def visualize_landmarks(self, frame, landmarks):
        #drawin the landmarks on the frame
        pass
    


