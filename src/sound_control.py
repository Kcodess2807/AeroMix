import pygame
import numpy as np
from utils.osc_handler import OSCHandler

class SoundController:
    def __init__(self, osc_handler=None):
        # Initialize pygame mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # OSC handler for communication with Max/MSP
        self.osc_handler = osc_handler or OSCHandler()
        
        # Current sound parameters
        self.tempo = 120.0  # BPM
        self.pitch = 1.0    # Pitch multiplier (1.0 = normal)
        self.volume = 0.5   # Volume (0.0 to 1.0)
        self.bass = 0.5     # Bass level (0.0 to 1.0)
        self.effects = {
            'reverb': 0.0,
            'echo': 0.0,
            'filter': 0.0
        }
        
        # Track playback state
        self.current_track = None
        self.is_playing = False
        
    def adjust_tempo(self, value):
        """Adjust the tempo (BPM)"""
        self.tempo = max(60.0, min(200.0, self.tempo + value))
        
        # Send OSC message to Max/MSP
        if self.osc_handler:
            self.osc_handler.send_message("/tempo", self.tempo)
            
        return self.tempo
    
    def adjust_pitch(self, value):
        """Adjust the pitch"""
        self.pitch = max(0.5, min(2.0, self.pitch + value))
        
        # Send OSC message to Max/MSP
        if self.osc_handler:
            self.osc_handler.send_message("/pitch", self.pitch)
            
        return self.pitch
    
    def adjust_volume(self, value):
        """Adjust the volume"""
        self.volume = max(0.0, min(1.0, self.volume + value))
        pygame.mixer.music.set_volume(self.volume)
        
        # Send OSC message to Max/MSP
        if self.osc_handler:
            self.osc_handler.send_message("/volume", self.volume)
            
        return self.volume
    
    def adjust_bass(self, value):
        """Adjust the bass level"""
        self.bass = max(0.0, min(1.0, self.bass + value))
        
        # Send OSC message to Max/MSP
        if self.osc_handler:
            self.osc_handler.send_message("/bass", self.bass)
            
        return self.bass
    
    def apply_effect(self, effect_name, value):
        """Apply an audio effect"""
        if effect_name in self.effects:
            self.effects[effect_name] = max(0.0, min(1.0, value))
            
            # Send OSC message to Max/MSP
            if self.osc_handler:
                self.osc_handler.send_message(f"/effect/{effect_name}", 
                                             self.effects[effect_name])
                
        return self.effects.get(effect_name, 0.0)
    
    def control_playback(self, command, track_path=None):
        """Control track playback (play, pause, stop, etc.)"""
        if command == "play" and track_path:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.current_track = track_path
            self.is_playing = True
        elif command == "pause":
            pygame.mixer.music.pause()
            self.is_playing = False
        elif command == "resume":
            pygame.mixer.music.unpause()
            self.is_playing = True
        elif command == "stop":
            pygame.mixer.music.stop()
            self.is_playing = False
            
        # Send OSC message to Max/MSP
        if self.osc_handler:
            self.osc_handler.send_message("/playback", command)
