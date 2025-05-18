import pygame
from utils.osc_handler import OSCHandler
from pyo import *
import time

class SoundController:
    def __init__(self, osc_handler=None):
        print("SoundController: Initializing audio system...")

        pygame.mixer.init()
        self.server = Server(sr=48000, nchnls=2, buffersize=512, winhost="wasapi")
        self.server.boot().start()
        print("Pyo server booted at 48000 Hz")

        self.tempo = 1.0   # 1.0 = normal speed
        self.pitch = 1.0   # 1.0 = normal pitch
        self.volume = 0.7
        self.bass = 0.5    # Changed to 0.5 (50%) as default, range 0.0-1.0
        self.current_track = None

        self._initialize_dsp()
        self.osc_handler = osc_handler or OSCHandler()

    def _initialize_dsp(self):
        """Initialize audio processing chain"""
        self.snd_table = SndTable()
        
        # Looper for playback (pitch and speed are linked)
        self.looper = Looper(
            table=self.snd_table,
            pitch=self.pitch,
            start=0,
            dur=self.snd_table.getDur(),
            mul=0.5
        )

        # Changed to frequency-based bass control (more noticeable)
        self.bass_freq = SigTo(value=1000, time=0.1)  # Start at midpoint
        self.bass_filter = ButLP(  # Use ButLP instead of EQ for more dramatic filtering
            self.looper,
            freq=self.bass_freq,
            mul=1.0
        )

        self.volume_sig = SigTo(value=self.volume, time=0.05)
        self.output = self.bass_filter * self.volume_sig
        self.output.out()

    def adjust_bass(self, value):
        """Control bass with range 0.0-1.0 (0-100%)"""
        self.bass = max(0.0, min(1.0, self.bass + value))
        
        # Map 0-1 range to a dramatic filter cutoff frequency (20Hz-5000Hz)
        # Lower values = more bass (lower cutoff frequency)
        cutoff = 20 + (self.bass * 4980)
        self.bass_freq.value = cutoff
        
        print(f"Bass: {self.bass*100:.0f}% (cutoff: {cutoff:.0f}Hz)")
        if self.osc_handler:
            self.osc_handler.send_message("/bass", self.bass)
        return self.bass

    def adjust_pitch(self, value):
        """Adjust playback pitch (0.5x to 2.0x)"""
        self.pitch = max(0.5, min(2.0, self.pitch + value))
        self.looper.pitch = self.pitch
        print(f"Pitch adjustment: {self.pitch:.2f}x (linked to tempo)")
        if self.osc_handler:
            self.osc_handler.send_message("/pitch", self.pitch)
        return self.pitch

    def adjust_tempo(self, value):
        """Adjust playback speed (0.5x to 2.0x)"""
        self.tempo = max(0.5, min(2.0, self.tempo + value))
        self.looper.speed = self.tempo
        print(f"Tempo adjustment: {self.tempo:.2f}x (linked to pitch)")
        if self.osc_handler:
            self.osc_handler.send_message("/tempo", self.tempo)
        return self.tempo

    def adjust_volume(self, value):
        """Control master volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, self.volume + value))
        self.volume_sig.value = self.volume
        print(f"Volume: {self.volume*100:.0f}%")
        if self.osc_handler:
            self.osc_handler.send_message("/volume", self.volume)
        return self.volume

    def control_playback(self, command, track_path=None):
        """Control audio playback"""
        if command == "play":
            if track_path:
                try:
                    self.snd_table.setSound(track_path)
                    self.looper.dur = self.snd_table.getDur()
                    self.current_track = track_path
                    print(f"Loaded: {track_path}")
                except Exception as e:
                    print(f"Load error: {e}")
                    return
            self.looper.play()
            print("Playback started")
        elif command == "stop":
            self.looper.stop()
            print("Playback stopped")
        if self.osc_handler:
            self.osc_handler.send_message("/playback", command)

    def cleanup(self):
        """Clean up resources"""
        try:
            self.server.stop()
            self.looper.stop()
            pygame.mixer.quit()
            print("Audio system cleaned up")
        except Exception as e:
            print(f"Cleanup error: {e}")
