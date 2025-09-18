"""
voice_controller.py - Voice command recognition using Vosk
Recognizes voice commands for mode switching and graph control
"""

import json
import os
import sys
import threading
import time
import queue
from typing import Optional, List

try:
    import vosk
    import sounddevice as sd
    import numpy as np
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required packages: pip install vosk sounddevice")
    sys.exit(1)

class VoiceController:
    """Voice command controller using Vosk offline speech recognition"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.running = False
        
        # Audio settings
        self.sample_rate = 16000
        self.device = None  # Use default device
        
        # Voice commands mapping
        self.commands = {
            'rotate mode': 'rotate_mode',
            'rotation mode': 'rotate_mode', 
            'drag mode': 'drag_mode',
            'dragging mode': 'drag_mode',
            'zoom mode': 'zoom_mode',
            'zooming mode': 'zoom_mode',
            'reset view': 'reset_view',
            'reset camera': 'reset_view',
            'center view': 'reset_view'
        }
        
        # Initialize Vosk
        self.model = None
        self.rec = None
        self._initialize_vosk()
        
        if debug:
            print("🎤 VoiceController initialized with Vosk")
    
    def _initialize_vosk(self):
        """Initialize Vosk speech recognition model"""
        try:
            # Find Vosk model directory
            model_paths = [
                "vosk-model-small-en-us-0.15",
                os.path.join(".", "vosk-model-small-en-us-0.15"),
                os.path.join(os.path.dirname(__file__), "..", "vosk-model-small-en-us-0.15")
            ]
            
            model_path = None
            for path in model_paths:
                if os.path.exists(path) and os.path.isdir(path):
                    model_path = path
                    break
            
            if not model_path:
                raise FileNotFoundError("Vosk model not found. Please run 'python setup_vosk.py'")
            
            # Set Vosk log level (0 = silent, 1 = errors only)
            vosk.SetLogLevel(0 if not self.debug else 1)
            
            # Initialize model and recognizer
            self.model = vosk.Model(model_path)
            self.rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
            
            print("✅ Vosk model initialized successfully")
            if self.debug:
                print(f"   Model path: {model_path}")
                print(f"   Sample rate: {self.sample_rate}")
            
        except Exception as e:
            print(f"❌ Failed to initialize Vosk: {e}")
            print("   Make sure Vosk model is downloaded. Run 'python setup_vosk.py'")
            self.model = None
            self.rec = None
    
    def listen_for_command(self) -> Optional[str]:
        """Listen for a single voice command using Vosk"""
        if not self.model or not self.rec:
            return None
            
        try:
            if self.debug:
                print("🎧 Listening for command...")
            
            # Record audio for 2 seconds
            duration = 2
            audio_data = sd.rec(
                int(duration * self.sample_rate), 
                samplerate=self.sample_rate, 
                channels=1, 
                dtype='int16',
                device=self.device
            )
            sd.wait()  # Wait for recording to complete
            
            # Convert to bytes for Vosk
            audio_bytes = audio_data.tobytes()
            
            # Process with Vosk
            if self.rec.AcceptWaveform(audio_bytes):
                result = json.loads(self.rec.Result())
            else:
                result = json.loads(self.rec.PartialResult())
            
            text = result.get('text', '').strip()
            
            if text and self.debug:
                print(f"🗣️ Recognized: '{text}'")
            
            # Process recognized text
            if text:
                return self._process_command(text.lower())
                
        except Exception as e:
            if self.debug:
                print(f"❌ Voice listening error: {e}")
            return None
        
        return None
    
    def _process_command(self, text: str) -> Optional[str]:
        """Process recognized text and extract commands"""
        if not text:
            return None
            
        # Check for exact command matches
        for command, action in self.commands.items():
            if command in text:
                if self.debug:
                    print(f"✅ Command matched: '{command}' -> {action}")
                return command
        
        # Check for partial matches
        if any(word in text for word in ['rotate', 'rotation']):
            return 'rotate mode'
        elif any(word in text for word in ['drag', 'move']):
            return 'drag mode' 
        elif any(word in text for word in ['zoom', 'scale']):
            return 'zoom mode'
        elif any(word in text for word in ['reset', 'center', 'home']):
            return 'reset view'
        
        if self.debug:
            print(f"❓ No command found in: '{text}'")
        return None
    
    def get_available_commands(self) -> List[str]:
        """Get list of available voice commands"""
        return list(self.commands.keys())
    
    def test_microphone(self) -> bool:
        """Test if microphone is working with Vosk"""
        if not self.model:
            return False
            
        try:
            print("🎤 Testing microphone... say something!")
            duration = 3
            audio_data = sd.rec(int(duration * self.sample_rate), 
                              samplerate=self.sample_rate, 
                              channels=1, 
                              dtype='int16',
                              device=self.device)
            sd.wait()
            
            # Process with Vosk
            audio_bytes = audio_data.tobytes()
            if self.rec.AcceptWaveform(audio_bytes):
                result = json.loads(self.rec.Result())
                text = result.get('text', '')
                if text:
                    print(f"✅ Microphone test successful! Heard: '{text}'")
                    return True
                else:
                    print("⚠️ Microphone working but no speech detected")
                    return False
            
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            return False
    
    def calibrate_microphone(self):
        """Calibrate microphone (not needed for Vosk)"""
        print("ℹ️ Vosk doesn't require calibration")
        return True
    
    def stop(self):
        """Stop voice recognition"""
        self.running = False
        if self.debug:
            print("🛑 Voice recognition stopped")