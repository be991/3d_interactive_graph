"""
main.py - Main application entry point for 3D Interactive Graph
Coordinates gesture detection, voice commands, and 3D visualization with camera overlay
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
from modules.overlay_visualizer import OverlayGraphVisualizer


class InteractiveGraphApp:
    """Main application class that coordinates all components"""

    def __init__(self, debug=False):
        self.debug = debug
        self.running = False

        # Initialize components
        self.gesture_detector = GestureDetector(debug=debug)
        self.voice_controller = VoiceController(debug=debug)
        self.graph_visualizer = OverlayGraphVisualizer(debug=debug)

        # Application state
        self.current_mode = "rotate"  # rotate, drag, zoom
        self.gesture_data = {}
        self.voice_commands = queue.Queue()

        # Threading
        self.voice_thread = None

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
        """Main camera loop for gesture detection and graph overlay"""
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
        print("👋 Use hand gestures to control the 3D graph overlay")
        print("⌨️ Press 'r' to reset view, 'q' or ESC to quit")

        frame_count = 0
        fps_counter = time.time()

        while self.running:
            try:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to read camera frame")
                    break

                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)

                # Process gestures on original frame
                gesture_data = self.process_gestures(frame.copy())
                if gesture_data:
                    self.apply_gesture_to_graph(gesture_data)

                # Process voice commands
                while not self.voice_commands.empty():
                    try:
                        command = self.voice_commands.get_nowait()
                        self.handle_voice_command(command)
                    except queue.Empty:
                        break

                # Draw 3D graph overlay on frame
                frame_with_graph = self.graph_visualizer.draw_graph_on_frame(frame)

                # Debug: Check if nodes are being positioned correctly
                if self.debug or True:  # Force debug for now
                    nodes_on_screen = sum(
                        1
                        for pos in self.graph_visualizer.node_screen_positions.values()
                        if 0 <= pos[0] < frame.shape[1] and 0 <= pos[1] < frame.shape[0]
                    )
                    if nodes_on_screen == 0:
            
                        # Draw a test marker to confirm drawing works
                        cv2.circle(frame_with_graph, (100, 100), 20, (0, 255, 0), -1)
                        cv2.putText(
                            frame_with_graph,
                            "GRAPH DEBUG: No nodes visible",
                            (10, 200),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2,
                        )

                # Add UI overlays
                self._draw_ui_overlays(frame_with_graph, gesture_data)

                # Show camera feed with 3D graph overlay
                cv2.imshow("3D Interactive Graph - Camera View", frame_with_graph)

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == 27:  # 'q' or ESC key
                    break
                elif key == ord("r"):  # 'r' for reset
                    self.graph_visualizer.reset_camera()
                    print("🔄 Graph view reset")
                elif key == ord("1"):  # Quick mode switches
                    self.current_mode = "rotate"
                    print("🔄 Switched to ROTATE mode")
                elif key == ord("2"):
                    self.current_mode = "drag"
                    print("🖱️ Switched to DRAG mode")
                elif key == ord("3"):
                    self.current_mode = "zoom"
                    print("🔍 Switched to ZOOM mode")

                frame_count += 1

                # Show FPS every second
                if self.debug and frame_count % 30 == 0:
                    current_time = time.time()
                    fps = 30 / (current_time - fps_counter)
                    print(f"📊 FPS: {fps:.1f}")
                    fps_counter = current_time

            except Exception as e:
                if self.debug:
                    print(f"❌ Camera loop error: {e}")
                time.sleep(0.1)

        cap.release()
        cv2.destroyAllWindows()

    def _draw_ui_overlays(self, frame, gesture_data):
        """Draw UI overlays on the frame"""
        h, w = frame.shape[:2]

        # Mode indicator (top-left)
        mode_color = {
            "rotate": (0, 255, 255),  # Yellow
            "drag": (255, 0, 255),  # Magenta
            "zoom": (0, 255, 0),  # Green
        }

        cv2.rectangle(frame, (5, 5), (120, 45), (0, 0, 0), -1)
        cv2.rectangle(
            frame, (5, 5), (120, 45), mode_color.get(self.current_mode, (255, 255, 255)), 2
        )
        cv2.putText(
            frame,
            f"Mode: {self.current_mode.upper()}",
            (10, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            mode_color.get(self.current_mode, (255, 255, 255)),
            2,
        )

        # Gesture status (top-right)
        if gesture_data and gesture_data.get("gesture_type") != "none":
            gesture_text = f"Gesture: {gesture_data.get('gesture_type')}"
            text_size = cv2.getTextSize(gesture_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(frame, (w - text_size[0] - 15, 5), (w - 5, 35), (0, 0, 0), -1)
            cv2.putText(
                frame,
                gesture_text,
                (w - text_size[0] - 10, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (100, 255, 100),
                2,
            )

        # Graph info (bottom-left)
        graph_info = self.graph_visualizer.get_graph_info()
        cv2.rectangle(frame, (5, h - 30), (300, h - 5), (0, 0, 0), -1)
        cv2.putText(
            frame, graph_info, (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1
        )

        # Quick help (bottom-right)
        help_text = "Press: R=Reset, Q=Quit, 1=Rotate, 2=Drag, 3=Zoom"
        text_size = cv2.getTextSize(help_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
        cv2.rectangle(frame, (w - text_size[0] - 10, h - 25), (w - 5, h - 5), (0, 0, 0), -1)
        cv2.putText(
            frame,
            help_text,
            (w - text_size[0] - 5, h - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (180, 180, 180),
            1,
        )

    def start(self):
        """Start the interactive graph application"""
        print("🚀 Starting 3D Interactive Graph Application...")
        print("=" * 50)
        print("📋 Instructions:")
        print("   🎯 GESTURES:")
        print("     - Pinch + drag: Move nodes (drag mode)")
        print("     - Fist + move: Rotate graph (rotate mode)")
        print("     - Two hands: Zoom in/out (zoom mode)")
        print("   🗣️ VOICE COMMANDS:")
        print("     - 'rotate mode', 'drag mode', 'zoom mode'")
        print("     - 'reset view'")
        print("   ⌨️ KEYBOARD:")
        print("     - 'r': Reset view")
        print("     - 'q' or ESC: Quit")
        print("     - '1': Rotate mode, '2': Drag mode, '3': Zoom mode")
        print("   📺 3D graph will appear overlaid on camera feed")
        print("=" * 50)
        print()

        self.running = True

        try:
            # Start voice recognition thread
            print("🎤 Starting voice recognition...")
            if self.voice_controller.model:  # Only start if Vosk is properly initialized
                self.voice_thread = threading.Thread(
                    target=self.process_voice_commands, daemon=True
                )
                self.voice_thread.start()
                print("✅ Voice recognition started")
            else:
                print("⚠️ Voice recognition disabled (Vosk model not found)")

            # Small delay to let voice thread initialize
            time.sleep(1)

            # Start camera loop (runs in main thread)
            print("📹 Starting camera feed with 3D graph overlay...")
            self.run_camera_loop()

        except KeyboardInterrupt:
            print("\n⚠️ Application interrupted by user")
        except Exception as e:
            print(f"❌ Application error: {e}")
            if self.debug:
                import traceback

                traceback.print_exc()
        finally:
            self.stop()

    def stop(self):
        """Stop the application and cleanup resources"""
        print("\n🛑 Stopping application...")
        self.running = False

        # Stop voice recognition
        if self.voice_controller:
            self.voice_controller.stop()

        # Wait for voice thread to finish
        if self.voice_thread and self.voice_thread.is_alive():
            self.voice_thread.join(timeout=2)

        print("✅ Application stopped successfully")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="3D Interactive Graph with Gesture and Voice Control")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    # Print startup banner
    print("=" * 60)
    print("🎯 3D INTERACTIVE GRAPH - GESTURE & VOICE CONTROL")
    print("=" * 60)
    print("🚀 Initializing components...")

    # Create and start application
    app = InteractiveGraphApp(debug=args.debug)

    try:
        app.start()
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
