import pygame
from utils.osc_handler import OSCHandler
import time
import traceback

class SoundController:
    def __init__(self, osc_handler=None):
        print("SoundController: Initializing audio system...")
        
        # Initialize basic audio with pygame only
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            print("[DEBUG] pygame.mixer initialized successfully")
            self.audio_available = True
        except Exception as e:
            print(f"[ERROR] Failed to initialize pygame.mixer: {e}")
            self.audio_available = False

        # Skip Pyo entirely for now - use simple pygame-based audio
        self.server = None
        self.tempo = 1.0
        self.pitch = 1.0
        self.volume = 0.7
        self.bass = 0.5
        self.current_track = None
        self.is_playing = False
        
        # Initialize simple audio controls
        self._initialize_simple_audio()
        self.osc_handler = osc_handler or OSCHandler()
        print("[DEBUG] SoundController initialized in simple mode")

    def _initialize_simple_audio(self):
        """Initialize simple pygame-based audio controls"""
        print("[DEBUG] Initializing simple audio controls...")
        
        # Set fallback values for all audio objects
        self.snd_table = None
        self.looper = None
        self.bass_filter = None
        self.output = None
        self.volume_sig = None
        self.bass_freq = None
        
        print("[DEBUG] Simple audio controls initialized")

    def adjust_bass(self, value):
        """Control bass with range 0.0-1.0 (0-100%)"""
        print(f"[DEBUG] Adjusting bass by {value}")
        self.bass = max(0.0, min(1.0, self.bass + value))
        print(f"Bass: {self.bass*100:.0f}% (simple mode)")
            
        if self.osc_handler:
            self.osc_handler.send_message("/bass", self.bass)
        return self.bass

    def adjust_pitch(self, value):
        """Adjust playback pitch (0.5x to 2.0x)"""
        print(f"[DEBUG] Adjusting pitch by {value}")
        self.pitch = max(0.5, min(2.0, self.pitch + value))
        print(f"Pitch: {self.pitch:.2f}x (simple mode)")
            
        if self.osc_handler:
            self.osc_handler.send_message("/pitch", self.pitch)
        return self.pitch

    def adjust_tempo(self, value):
        """Adjust playback speed (0.5x to 2.0x)"""
        print(f"[DEBUG] Adjusting tempo by {value}")
        self.tempo = max(0.5, min(2.0, self.tempo + value))
        print(f"Tempo: {self.tempo:.2f}x (simple mode)")
            
        if self.osc_handler:
            self.osc_handler.send_message("/tempo", self.tempo)
        return self.tempo

    def adjust_volume(self, value):
        """Control master volume (0.0 to 1.0)"""
        print(f"[DEBUG] Adjusting volume by {value}")
        self.volume = max(0.0, min(1.0, self.volume + value))
        
        if self.audio_available:
            try:
                pygame.mixer.music.set_volume(self.volume)
                print(f"Volume: {self.volume*100:.0f}%")
            except:
                print(f"Volume: {self.volume*100:.0f}% (pygame not available)")
        else:
            print(f"Volume: {self.volume*100:.0f}% (audio not available)")
            
        if self.osc_handler:
            self.osc_handler.send_message("/volume", self.volume)
        return self.volume

    def control_playback(self, command, track_path=None):
        """Control audio playback using pygame"""
        print(f"[DEBUG] Control playback command: {command}, track_path: {track_path}")
        
        if not self.audio_available:
            print("[WARNING] Audio not available, playback command ignored")
            return
            
        if command == "play":
            if track_path:
                try:
                    pygame.mixer.music.load(track_path)
                    self.current_track = track_path
                    print(f"Loaded: {track_path}")
                except Exception as e:
                    print(f"Load error: {e}")
                    return

            try:
                pygame.mixer.music.play()
                self.is_playing = True
                print("Playback started")
            except Exception as e:
                print(f"Playback error: {e}")

        elif command == "stop":
            try:
                pygame.mixer.music.stop()
                self.is_playing = False
                print("Playback stopped")
            except Exception as e:
                print(f"Stop error: {e}")

        if self.osc_handler:
            self.osc_handler.send_message("/playback", command)

    def cleanup(self):
        """Clean up resources"""
        print("SoundController: Cleaning up audio system...")
        try:
            if self.audio_available:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            print("Audio system cleaned up")
        except Exception as e:
            print(f"Cleanup error: {e}")
