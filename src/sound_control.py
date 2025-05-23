import pygame
from utils.osc_handler import OSCHandler
from pyo import *
import time
import traceback

class SoundController:
    def __init__(self, osc_handler=None):
        print("SoundController: Initializing audio system...")
        
        try:
            pygame.mixer.init()
            print("[DEBUG] pygame.mixer initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize pygame.mixer: {e}")
            print("[ERROR] Stack trace:")
            traceback.print_exc()

        # Fix 1: Try multiple audio configurations
        self.server = None
        audio_configs = [
            {"sr": 44100, "nchnls": 2, "buffersize": 1024, "winhost": "wasapi"},
            {"sr": 48000, "nchnls": 2, "buffersize": 512, "winhost": "directsound"},
            {"sr": 44100, "nchnls": 2, "buffersize": 1024, "winhost": "directsound"},
            {"sr": 22050, "nchnls": 2, "buffersize": 2048, "winhost": "mme"},
        ]
        
        for config in audio_configs:
            try:
                print(f"[DEBUG] Trying audio config: {config}")
                self.server = Server(**config)
                self.server.boot()
                # Wait for server to fully boot
                time.sleep(0.5)
                self.server.start()
                print(f"Pyo server booted successfully with config: {config}")
                break
            except Exception as e:
                print(f"[DEBUG] Audio config failed: {config}, error: {e}")
                if self.server:
                    try:
                        self.server.stop()
                        self.server.shutdown()
                    except:
                        pass
                self.server = None
                continue
        
        if self.server is None:
            print("[ERROR] Failed to initialize any Pyo server configuration")
            # Create a dummy server for fallback
            try:
                self.server = Server(sr=44100, nchnls=2, buffersize=1024)
                self.server.boot()
                time.sleep(0.5)
                self.server.start()
                print("[DEBUG] Fallback server created")
            except Exception as e:
                print(f"[ERROR] Even fallback server failed: {e}")
                self.server = None

        self.tempo = 1.0
        self.pitch = 1.0
        self.volume = 0.7
        self.bass = 0.5
        self.current_track = None
        
        # Only initialize DSP if server is working
        if self.server:
            self._initialize_dsp()
        else:
            print("[WARNING] No audio server available, running in silent mode")
            
        self.osc_handler = osc_handler or OSCHandler()

    def _initialize_dsp(self):
        """Initialize audio processing chain"""
        print("[DEBUG] Initializing DSP chain...")
        
        if not self.server:
            print("[WARNING] No server available for DSP initialization")
            return
            
        try:
            # Fix 2: Add server state check
            if not hasattr(self.server, '_server') or not self.server._server:
                print("[WARNING] Server not properly booted, skipping DSP initialization")
                return
                
            self.snd_table = SndTable()
            print("[DEBUG] SndTable initialized")

            # Looper for playback
            self.looper = Looper(
                table=self.snd_table,
                pitch=self.pitch,
                start=0,
                dur=self.snd_table.getDur(),
                mul=0.5
            )
            print("[DEBUG] Looper initialized")

            # Bass control
            self.bass_freq = SigTo(value=1000, time=0.1)
            self.bass_filter = ButLP(
                self.looper,
                freq=self.bass_freq,
                mul=1.0
            )
            print("[DEBUG] Bass filter initialized")

            self.volume_sig = SigTo(value=self.volume, time=0.05)
            self.output = self.bass_filter * self.volume_sig
            self.output.out()
            print("[DEBUG] DSP chain initialized and output started")

        except Exception as e:
            print(f"[ERROR] Failed to initialize DSP chain: {e}")
            print("[ERROR] Stack trace:")
            traceback.print_exc()
            # Set fallback values
            self.snd_table = None
            self.looper = None
            self.bass_filter = None
            self.output = None

    def adjust_bass(self, value):
        """Control bass with range 0.0-1.0 (0-100%)"""
        print(f"[DEBUG] Adjusting bass by {value}")
        self.bass = max(0.0, min(1.0, self.bass + value))
        
        if hasattr(self, 'bass_freq') and self.bass_freq:
            cutoff = 20 + (self.bass * 4980)
            self.bass_freq.value = cutoff
            print(f"Bass: {self.bass*100:.0f}% (cutoff: {cutoff:.0f}Hz)")
        else:
            print(f"Bass: {self.bass*100:.0f}% (audio engine not available)")
            
        if self.osc_handler:
            self.osc_handler.send_message("/bass", self.bass)
        return self.bass

    def adjust_pitch(self, value):
        """Adjust playback pitch (0.5x to 2.0x)"""
        print(f"[DEBUG] Adjusting pitch by {value}")
        self.pitch = max(0.5, min(2.0, self.pitch + value))
        
        if hasattr(self, 'looper') and self.looper:
            self.looper.pitch = self.pitch
            print(f"Pitch adjustment: {self.pitch:.2f}x")
        else:
            print(f"Pitch: {self.pitch:.2f}x (audio engine not available)")
            
        if self.osc_handler:
            self.osc_handler.send_message("/pitch", self.pitch)
        return self.pitch

    def adjust_tempo(self, value):
        """Adjust playback speed (0.5x to 2.0x)"""
        print(f"[DEBUG] Adjusting tempo by {value}")
        self.tempo = max(0.5, min(2.0, self.tempo + value))
        
        if hasattr(self, 'looper') and self.looper:
            self.looper.speed = self.tempo
            print(f"Tempo adjustment: {self.tempo:.2f}x")
        else:
            print(f"Tempo: {self.tempo:.2f}x (audio engine not available)")
            
        if self.osc_handler:
            self.osc_handler.send_message("/tempo", self.tempo)
        return self.tempo

    def adjust_volume(self, value):
        """Control master volume (0.0 to 1.0)"""
        print(f"[DEBUG] Adjusting volume by {value}")
        self.volume = max(0.0, min(1.0, self.volume + value))
        
        if hasattr(self, 'volume_sig') and self.volume_sig:
            self.volume_sig.value = self.volume
            print(f"Volume: {self.volume*100:.0f}%")
        else:
            print(f"Volume: {self.volume*100:.0f}% (audio engine not available)")
            
        if self.osc_handler:
            self.osc_handler.send_message("/volume", self.volume)
        return self.volume

    def control_playback(self, command, track_path=None):
        """Control audio playback"""
        print(f"[DEBUG] Control playback command: {command}, track_path: {track_path}")
        
        if not hasattr(self, 'looper') or not self.looper:
            print("[WARNING] Audio engine not available, playback command ignored")
            return
            
        if command == "play":
            if track_path:
                try:
                    self.snd_table.setSound(track_path)
                    self.looper.dur = self.snd_table.getDur()
                    self.current_track = track_path
                    print(f"Loaded: {track_path}")
                except Exception as e:
                    print(f"Load error: {e}")
                    print("[ERROR] Stack trace:")
                    traceback.print_exc()
                    return

            try:
                self.looper.play()
                print("Playback started")
            except Exception as e:
                print(f"Playback error: {e}")

        elif command == "stop":
            try:
                self.looper.stop()
                print("Playback stopped")
            except Exception as e:
                print(f"Stop error: {e}")

        if self.osc_handler:
            self.osc_handler.send_message("/playback", command)

    def cleanup(self):
        """Clean up resources"""
        print("SoundController: Cleaning up audio system...")
        try:
            if hasattr(self, 'looper') and self.looper:
                self.looper.stop()
            if self.server:
                self.server.stop()
                self.server.shutdown()
            pygame.mixer.quit()
            print("Audio system cleaned up")
        except Exception as e:
            print(f"Cleanup error: {e}")
            print("[ERROR] Stack trace:")
            traceback.print_exc()
