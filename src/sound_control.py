import pygame
from utils.osc_handler import OSCHandler
from pyo import *
import time

class SoundController:
    def __init__(self, osc_handler=None):
        print("SoundController: Initializing audio system...")

        pygame.mixer.init()

        # Pyo server setup
        self.server = Server(sr=48000, nchnls=2, buffersize=512, winhost="wasapi")
        self.server.boot().start()
        print("Pyo server booted at 48000 Hz")

        # Audio parameters
        self.tempo = 1.0   # 1.0 = normal speed
        self.pitch = 1.0   # 1.0 = normal pitch
        self.volume = 0.7
        self.bass = 1.0
        self.current_track = None

        # Initialize DSP chain
        self._initialize_dsp()

        # OSC handler
        self.osc_handler = osc_handler or OSCHandler()

    def _initialize_dsp(self):
        """Initialize audio processing chain with independent pitch/tempo"""
        # Audio file playback system
        self.snd_table = SndTable()

        # Phase vocoder for time-stretching and pitch-shifting
        self.pvoc = PVoc(self.snd_table, size=2048, overlaps=8)
        self.pvoc_looper = PVocLooper(
            self.pvoc,
            pitch=self.pitch,    # Transposition (0.5 to 2.0)
            time=self.tempo,     # Speed (0.5 to 2.0)
            start=0,
            dur=self.snd_table.getDur(),
            mul=0.5
        )

        # Bass control (Parametric EQ for low frequencies)
        self.bass_freq = SigTo(value=100, time=0.1)
        self.bass_gain = SigTo(value=0, time=0.1)
        self.bass_filter = EQ(
            self.pvoc_looper,
            freq=self.bass_freq,
            q=0.7,
            boost=self.bass_gain,
            type=0 # Low shelf filter
        )

        # Volume control
        self.volume_sig = SigTo(value=self.volume, time=0.05)

        # Final output
        self.output = self.bass_filter * self.volume_sig
        self.output.out()

    def adjust_bass(self, value):
        """Control bass levels (-12dB to +12dB)"""
        self.bass = max(-1.0, min(1.0, self.bass + value))
        self.bass_gain.value = self.bass * 12 # Convert to dB
        print(f"Bass gain: {self.bass_gain.value:.1f}dB")
        if self.osc_handler:
            self.osc_handler.send_message("/bass", self.bass)

    def adjust_pitch(self, value):
        """Adjust playback pitch (0.5x to 2.0x) independently of tempo"""
        self.pitch = max(0.5, min(2.0, self.pitch + value/10))
        self.pvoc_looper.pitch = self.pitch
        print(f"Pitch adjustment: {self.pitch:.2f}x (independent)")
        if self.osc_handler:
            self.osc_handler.send_message("/pitch", self.pitch)

    def adjust_tempo(self, value):
        """Adjust playback speed (0.5x to 2.0x) independently of pitch"""
        self.tempo = max(0.5, min(2.0, self.tempo + value/20))
        self.pvoc_looper.time = self.tempo
        print(f"Tempo adjustment: {self.tempo:.2f}x (independent)")
        if self.osc_handler:
            self.osc_handler.send_message("/tempo", self.tempo)

    def adjust_volume(self, value):
        """Control master volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, self.volume + value))
        self.volume_sig.value = self.volume
        print(f"Volume: {self.volume*100:.0f}%")
        if self.osc_handler:
            self.osc_handler.send_message("/volume", self.volume)

    def control_playback(self, command, track_path=None):
        """Control audio playback"""
        if command == "play":
            if track_path:
                try:
                    self.snd_table.setSound(track_path)
                    self.pvoc_looper.dur = self.snd_table.getDur()
                    self.current_track = track_path
                    print(f"Loaded: {track_path}")
                except Exception as e:
                    print(f"Load error: {e}")
                    return
            self.pvoc_looper.play()
            print("Playback started")
        elif command == "stop":
            self.pvoc_looper.stop()
            print("Playback stopped")
        if self.osc_handler:
            self.osc_handler.send_message("/playback", command)

    def cleanup(self):
        """Clean up resources"""
        try:
            self.server.stop()
            self.pvoc_looper.stop()
            pygame.mixer.quit()
            print("Audio system cleaned up")
        except Exception as e:
            print(f"Cleanup error: {e}")
