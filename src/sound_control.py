import pygame
import numpy as np
from utils.osc_handler import OSCHandler
from pyo import *
import time

class SoundController:
    def __init__(self, osc_handler=None):
        print("SoundController: Initializing audio system...")

        pygame.mixer.init(frequency=48000, size=-16, channels=2, buffer=512)

        self.server = Server(sr=48000, nchnls=2, buffersize=512, winhost="wasapi")
        self.server.boot()
        if not self.server.getIsBooted():
            raise RuntimeError("Pyo server failed to boot at 48000 Hz.")
        self.server.start()
        print("Pyo server booted at 48000 Hz")

        # --- INITIALIZE PARAMETERS BEFORE _setup_metro ---
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

        # --- NOW SAFE TO SETUP METRO ---
        self._setup_metro()

        # --- CREATE PYO AUDIO OBJECTS ONLY AFTER SERVER IS BOOTED ---
        self.noise = Noise(mul=0.5)
        self.bass_filter = ButLP(self.noise, freq=1000)
        self.envelope = Sig(1)
        self.output = self.bass_filter * self.envelope * 0.1
        self.output.out()

        self.osc_handler = osc_handler or OSCHandler()

    def _setup_metro(self):
        """Setup the metro for tempo-based effects"""
        def trigger_env():
            # Create a short percussive envelope (attack=0.001s, decay=0.1s)
            env = Adsr(attack=0.001, decay=0.1, sustain=0, release=0, dur=0.101)
            self.envelope.value = env
            env.play()
        self.metro = Metro(time=60.0/self.tempo)
        self.metro.function = trigger_env
        self.metro.play()

    def adjust_tempo(self, value):
        self.tempo = max(60.0, min(200.0, self.tempo + value))
        print(f"SoundController: Adjusting tempo to {self.tempo}")
        self.metro.time = 60.0 / self.tempo
        if self.osc_handler:
            self.osc_handler.send_message("/tempo", self.tempo)
        return self.tempo

    def adjust_pitch(self, value):
        self.pitch = max(0.5, min(2.0, self.pitch + value))
        print(f"SoundController: Adjusting pitch to {self.pitch}")
        # Implement pitch control with Pyo if needed
        if self.osc_handler:
            self.osc_handler.send_message("/pitch", self.pitch)
        return self.pitch

    def adjust_volume(self, value):
        self.volume = max(0.0, min(1.0, self.volume + value))
        print(f"SoundController: Adjusting volume to {self.volume}")
        pygame.mixer.music.set_volume(self.volume)
        self.output.mul = Port(self.volume * 0.2, risetime=0.01, falltime=0.01)
        if self.osc_handler:
            self.osc_handler.send_message("/volume", self.volume)
        return self.volume

    def adjust_bass(self, value):
        self.bass = max(0.0, min(1.0, self.bass + value))
        print(f"SoundController: Adjusting bass to {self.bass}")
        cutoff = self.bass * 4980 + 20  # Map 0-1 to 20-5000 Hz
        self.bass_filter.freq = Port(cutoff, risetime=0.05, falltime=0.05)
        if self.osc_handler:
            self.osc_handler.send_message("/bass", self.bass)
        return self.bass

    def apply_effect(self, effect_name, value):
        if effect_name in self.effects:
            self.effects[effect_name] = max(0.0, min(1.0, value))
            print(f"SoundController: Applying effect {effect_name} with value {self.effects[effect_name]}")
            # Implement Pyo effects here if needed
            if self.osc_handler:
                self.osc_handler.send_message(f"/effect/{effect_name}", self.effects[effect_name])
        return self.effects.get(effect_name, 0.0)

    def control_playback(self, command, track_path=None):
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

    def cleanup(self):
        """Clean up resources when done"""
        try:
            self.server.stop()
            print("SoundController: Pyo server stopped")
        except:
            pass
