import cv2
import numpy as np
import pygame
import time

class Visualizer:
    """
    A class for visualizing music and gestures in the AEROMIX application.
    Creates dynamic visual elements that respond to audio parameters and detected gestures.
    """
    
    def __init__(self, width=640, height=480):
        
        self.width = width
        self.height = height
        self.last_update = time.time()
        self.fps = 30
        
        # Visualization parameters
        self.bars = 16  # Number of frequency bars
        self.bar_width = width // self.bars
        self.bar_heights = np.zeros(self.bars)
        self.colors = []
        
        # Generate colors for visualization
        for i in range(self.bars):
            # Create a gradient of colors from blue to red
            r = int(255 * (i / self.bars))
            g = int(100 * np.sin(i / self.bars * np.pi))
            b = int(255 * (1 - i / self.bars))
            self.colors.append((b, g, r))  # OpenCV uses BGR
        
        # Audio parameters for visualization
        self.tempo = 120
        self.volume = 0.5
        self.bass = 0.5
        self.effects = {
            'reverb': 0.0,
            'echo': 0.0,
            'filter': 0.0
        }
        
        # Gesture visualization
        self.last_gesture = None
        self.gesture_time = 0
        self.gesture_display_time = 2.0  # seconds to display gesture name
        
    def update_audio_params(self, tempo=None, volume=None, bass=None, effects=None):
        
        if tempo is not None:
            self.tempo = tempo
        if volume is not None:
            self.volume = volume
        if bass is not None:
            self.bass = bass
        if effects is not None:
            self.effects.update(effects)
            
    def show_gesture(self, gesture_name):
        """
        Display a detected gesture name.
        
        Args:
            gesture_name (str): Name of the detected gesture
        """
        self.last_gesture = gesture_name
        self.gesture_time = time.time()
    
    def _update_visualization(self):
        """Update the visualization elements based on audio parameters."""
        current_time = time.time()
        elapsed = current_time - self.last_update
        
        # Only update at the specified frame rate
        if elapsed < 1.0 / self.fps:
            return
            
        self.last_update = current_time
        
        # Calculate bar heights based on audio parameters
        # This is a simple simulation - in a real app, you might use FFT data
        beat_phase = (current_time * self.tempo / 60) % 1.0
        beat_impact = np.exp(-beat_phase * 5) * 0.5  # Decay effect after beat
        
        for i in range(self.bars):
            # Base height from volume
            height = self.height * 0.2 * self.volume
            
            # Add bass impact to lower frequencies
            if i < self.bars // 3:
                height += self.height * 0.3 * self.bass * (1 - i / (self.bars // 3))
            
            # Add beat impact
            height += self.height * 0.3 * beat_impact
            
            # Add some randomness
            height += np.random.uniform(0, self.height * 0.1)
            
            # Smooth transition
            self.bar_heights[i] = self.bar_heights[i] * 0.7 + height * 0.3
    
    def update(self, frame):
        
        # Update visualization elements
        self._update_visualization()
        
        # Draw frequency bars
        for i in range(self.bars):
            height = int(min(self.bar_heights[i], self.height * 0.8))
            x1 = i * self.bar_width
            y1 = self.height - height
            x2 = (i + 1) * self.bar_width - 2  # Gap between bars
            y2 = self.height
            cv2.rectangle(frame, (x1, y1), (x2, y2), self.colors[i], -1)
        
        # Draw audio parameters
        cv2.putText(frame, f"Tempo: {self.tempo:.1f} BPM", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Volume: {int(self.volume * 100)}%", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Bass: {int(self.bass * 100)}%", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Display detected gesture if recent
        if self.last_gesture and time.time() - self.gesture_time < self.gesture_display_time:
            cv2.putText(frame, f"Gesture: {self.last_gesture}", 
                       (self.width // 2 - 100, self.height - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        
        return frame
