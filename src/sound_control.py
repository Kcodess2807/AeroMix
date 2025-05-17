import pygame
import numpy as np
from utils.osc_handler import OSCHandler

class SoundController:
    def __init__(self, osc_handler=None):
        print("SoundController: Initializing pygame mixer...")
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.osc_handler = osc_handler or OSCHandler()
        self.tempo = 120.0
        self.pitch = 1.0
        self.volume = 0.5
        self.bass = 0.5
        self.effects = {
            'reverb': 0.0,
            'echo': 0.0,
            'filter': 0.0
        }
        self.current_track = None
        self.is_playing = False

    def adjust_tempo(self, value):
        self.tempo = max(60.0, min(200.0, self.tempo + value))
        print(f"SoundController: Adjusting tempo to {self.tempo}")
        if self.osc_handler:
            self.osc_handler.send_message("/tempo", self.tempo)
        return self.tempo

    def adjust_pitch(self, value):
        self.pitch = max(0.5, min(2.0, self.pitch + value))
        print(f"SoundController: Adjusting pitch to {self.pitch}")
        if self.osc_handler:
            self.osc_handler.send_message("/pitch", self.pitch)
        return self.pitch

    def adjust_volume(self, value):
        self.volume = max(0.0, min(1.0, self.volume + value))
        print(f"SoundController: Adjusting volume to {self.volume}")
        pygame.mixer.music.set_volume(self.volume)
        if self.osc_handler:
            self.osc_handler.send_message("/volume", self.volume)
        return self.volume

    def adjust_bass(self, value):
        self.bass = max(0.0, min(1.0, self.bass + value))
        print(f"SoundController: Adjusting bass to {self.bass}")
        if self.osc_handler:
            self.osc_handler.send_message("/bass", self.bass)
        return self.bass

    def apply_effect(self, effect_name, value):
        if effect_name in self.effects:
            self.effects[effect_name] = max(0.0, min(1.0, value))
            print(f"SoundController: Applying effect {effect_name} with value {self.effects[effect_name]}")
            if self.osc_handler:
                self.osc_handler.send_message(f"/effect/{effect_name}", self.effects[effect_name])
        return self.effects.get(effect_name, 0.0)

    def control_playback(self, command, track_path=None):
        # Default to your custom audio file if none specified
        if track_path is None:
            track_path = "data/audio/audio3.mp3"
        print(f"SoundController: Playback command {command}, track: {track_path}")
        if command == "play":
            try:
                pygame.mixer.music.load(track_path)
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play()
                self.current_track = track_path
                self.is_playing = True
                print("SoundController: Playing audio.")
            except Exception as e:
                print(f"SoundController: Failed to play audio: {e}")
        elif command == "pause":
            pygame.mixer.music.pause()
            self.is_playing = False
            print("SoundController: Paused audio.")
        elif command == "resume":
            pygame.mixer.music.unpause()
            self.is_playing = True
            print("SoundController: Resumed audio.")
        elif command == "stop":
            pygame.mixer.music.stop()
            self.is_playing = False
            print("SoundController: Stopped audio.")
        if self.osc_handler:
            self.osc_handler.send_message("/playback", command)
