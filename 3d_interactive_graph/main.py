"""
main.py - Main application entry point for 3D Interactive Graph
Coordinates gesture detection, voice commands, and 3D visualization
"""

import sys
import time
import threading
import queue
import argparse
from typing import Dict, Any, Optional
import cv2
import numpy as np

# Import custom modules
from modules.gesture_detector import GestureDetector
from modules.voice_controller import VoiceController  
from modules.graph_visualizer import GraphVisualizer

class InteractiveGraphApp:
    """Main application class that coordinates all components"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.running = False
        
        # Initialize components
        self.gesture_detector = GestureDetector(debug=debug)
        self.voice_controller = VoiceController(debug=debug)
        self.graph_visualizer = GraphVisualizer(debug=debug)
        
        # Application state
        self.current_mode = "rotate"  # rotate, drag, zoom
        self.gesture_data = {}
        self.voice_commands = queue.Queue()
        
        # Threading
        self.voice_thread = None
        self.gesture_thread = None
        
        if debug:
            print("🚀 InteractiveGraphApp initialized")
    
    def process_voice_commands(self):
        """Process voice commands in separate thread"""
        while self.running:
            try:
                command = self.voice_controller.listen_for_command()
                if command:
                    self.voice_commands.put(command)
                    if self.debug:
                        print(f"🎤 Voice command received: {command}")
                time.sleep(0.1)
            except Exception as e:
                if self.debug:
                    print(f"❌ Voice processing error: {e}")
                time.sleep(1)
    
    def process_gestures(self, frame):
        """Process hand gestures from camera frame"""
        try:
            gesture_data = self.gesture_detector.detect_gestures(frame)
            if gesture_data:
                self.gesture_data = gesture_data
                if self.debug and gesture_data.get('gesture_type') != 'none':
                    print(f"👋 Gesture detected: {gesture_data.get('gesture_type')}")
            return gesture_data
        except Exception as e:
            if self.debug:
                print(f"❌ Gesture processing error: {e}")
            return None
    
    def handle_voice_command(self, command: str):
        """Handle incoming voice commands"""
        command = command.lower().strip()
        
        if "rotate" in command and "mode" in command:
            self.current_mode = "rotate"
            print("🔄 Switched to ROTATE mode")
            
        elif "drag" in command and "mode" in command:
            self.current_mode = "drag" 
            print("🖱️ Switched to DRAG mode")
            
        elif "zoom" in command and "mode" in command:
            self.current_mode = "zoom"
            print("🔍 Switched to ZOOM mode")
            
        elif "reset" in command and "view" in command:
            self.graph_visualizer.reset_camera()
            print("🏠 Camera view reset")
            
        else:
            if self.debug:
                print(f"❓ Unknown command: {command}")
    
    def apply_gesture_to_graph(self, gesture_data: Dict[str, Any]):
        """Apply gesture data to 3D graph visualization"""
        if not gesture_data or gesture_data.get('gesture_type') == 'none':
            return
            
        gesture_type = gesture_data.get('gesture_type')
        
        try:
            if gesture_type == 'pinch' and self.current_mode == 'drag':
                # Drag individual nodes
                position = gesture_data.get('position', (0, 0))
                movement = gesture_data.get('movement', (0, 0))
                self.graph_visualizer.drag_node(position, movement)
                
            elif gesture_type == 'fist' and self.current_mode == 'rotate':
                # Rotate entire graph
                movement = gesture_data.get('movement', (0, 0))
                self.graph_visualizer.rotate_graph(movement)
                
            elif gesture_type == 'two_hand_zoom' and self.current_mode == 'zoom':
                # Zoom in/out
                zoom_factor = gesture_data.get('zoom_factor', 1.0)
                self.graph_visualizer.zoom_graph(zoom_factor)
                
        except Exception as e:
            if self.debug:
                print(f"❌ Error applying gesture: {e}")
    
    def run_camera_loop(self):
        """Main camera loop for gesture detection"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return
            
        print("📹 Camera initialized successfully")
        print("🎯 Current mode:", self.current_mode.upper())
        print("🗣️ Say 'rotate mode', 'drag mode', 'zoom mode', or 'reset view'")
        
        frame_count = 0
        
        while self.running:
            try:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to read camera frame")
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Process gestures
                gesture_data = self.process_gestures(frame)
                if gesture_data:
                    self.apply_gesture_to_graph(gesture_data)
                
                # Process voice commands
                while not self.voice_commands.empty():
                    try:
                        command = self.voice_commands.get_nowait()
                        self.handle_voice_command(command)
                    except queue.Empty:
                        break
                
                # Display current mode on frame
                cv2.putText(frame, f"Mode: {self.current_mode.upper()}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Display gesture info
                if gesture_data and gesture_data.get('gesture_type') != 'none':
                    gesture_text = f"Gesture: {gesture_data.get('gesture_type')}"
                    cv2.putText(frame, gesture_text, (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                # Show camera feed
                cv2.imshow('3D Graph Controller', frame)
                
                # Check for exit
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC key
                    break
                    
                frame_count += 1
                
            except Exception as e:
                if self.debug:
                    print(f"❌ Camera loop error: {e}")
                time.sleep(0.1)
        
        cap.release()
        cv2.destroyAllWindows()
    
    def start(self):
        """Start the interactive graph application"""
        print("🚀 Starting 3D Interactive Graph Application...")
        print("📋 Instructions:")
        print("   - Use hand gestures in front of camera")
        print("   - Speak voice commands to switch modes")
        print("   - Press 'q' or ESC to quit")
        print("   - Check browser for 3D visualization")
        print()
        
        self.running = True
        
        try:
            # Start 3D graph visualization server
            print("🌐 Starting 3D visualization server...")
            self.graph_visualizer.start_server()
            time.sleep(2)  # Wait for server to start
            
            # Start voice recognition thread
            print("🎤 Starting voice recognition...")
            self.voice_thread = threading.Thread(target=self.process_voice_commands, daemon=True)
            self.voice_thread.start()
            
            # Start camera loop (runs in main thread)
            print("📹 Starting camera feed...")
            self.run_camera_loop()
            
        except KeyboardInterrupt:
            print("\n⚠️ Application interrupted by user")
        except Exception as e:
            print(f"❌ Application error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the application and cleanup resources"""
        print("\n🛑 Stopping application...")
        self.running = False
        
        # Stop voice recognition
        if self.voice_controller:
            self.voice_controller.stop()
            
        # Stop visualization server
        if self.graph_visualizer:
            self.graph_visualizer.stop_server()
        
        print("✅ Application stopped successfully")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='3D Interactive Graph with Gesture and Voice Control')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    # Create and start application
    app = InteractiveGraphApp(debug=args.debug)
    
    try:
        app.start()
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()