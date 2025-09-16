"""
voice_controller.py - Voice command recognition using SpeechRecognition
Recognizes voice commands for mode switching and graph control
"""

import speech_recognition as sr
import threading
import time
import queue
from typing import Optional, List
import sys

class VoiceController:
    """Voice command controller using SpeechRecognition library"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.running = False
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
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
        
        # Recognition settings
        self.energy_threshold = 4000
        self.dynamic_energy_threshold = True
        self.timeout = 1.0
        self.phrase_timeout = 0.3
        
        # Initialize microphone
        self._initialize_microphone()
        
        if debug:
            print("🎤 VoiceController initialized")
    
    def _initialize_microphone(self):
        """Initialize microphone for speech recognition"""
        try:
            # Try to get default microphone
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            print("🎤 Adjusting microphone for ambient noise... (please be quiet)")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            # Set recognition parameters
            self.recognizer.energy_threshold = self.energy_threshold
            self.recognizer.dynamic_energy_threshold = self.dynamic_energy_threshold
            
            print("✅ Microphone initialized successfully")
            if self.debug:
                print(f"   Energy threshold: {self.recognizer.energy_threshold}")
            
        except Exception as e:
            print(f"❌ Failed to initialize microphone: {e}")
            print("   Make sure microphone is connected and accessible")
            self.microphone = None
    
    def listen_for_command(self) -> Optional[str]:
        """Listen for a single voice command"""
        if not self.microphone:
            return None
            
        try:
            # Listen for audio
            with self.microphone as source:
                if self.debug:
                    print("🎧 Listening for command...")
                
                # Listen with timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.timeout, 
                    phrase_time_limit=self.phrase_timeout
                )
                
            # Recognize speech
            try:
                # Try Windows Speech Recognition first (offline)
                text = self.recognizer.recognize_sphinx(audio)
                if self.debug:
                    print(f"🗣️ Sphinx recognized: '{text}'")
            except (sr.UnknownValueError, sr.RequestError):
                try:
                    # Fallback to Google Speech Recognition (online)
                    text = self.recognizer.recognize_google(audio, language='en-US')
                    if self.debug:
                        print(f"🗣️ Google recognized: '{text}'")
                except (sr.UnknownValueError, sr.RequestError) as e:
                    if self.debug:
                        print(f"❌ Speech recognition error: {e}")
                    return None
            
            # Process recognized text
            if text:
                return self._process_command(text.lower().strip())
                
        except sr.WaitTimeoutError:
            # Normal timeout - no speech detected
            return None
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