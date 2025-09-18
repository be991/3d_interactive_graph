"""
gesture_detector.py - Hand gesture recognition using MediaPipe
Detects pinch, fist, and two-hand zoom gestures
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, Any, Optional, List, Tuple
import math

class GestureDetector:
    """Hand gesture detector using MediaPipe"""
    
    def __init__(self, debug=False):
        self.debug = debug
        
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        
        # Hand detection configuration
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # FIXED: Proper drawing specifications for MediaPipe
        self.landmark_drawing_spec = self.mp_draw.DrawingSpec(
            color=(0, 0, 255),  # BGR: Red dots for landmarks
            thickness=2, 
            circle_radius=3
        )
        
        self.connection_drawing_spec = self.mp_draw.DrawingSpec(
            color=(0, 255, 0),  # BGR: Green lines for connections
            thickness=2
        )
        
        # Gesture state tracking
        self.prev_positions = {}
        self.gesture_history = []
        self.history_length = 5
        
        # Gesture thresholds
        self.pinch_threshold = 0.05  # Distance threshold for pinch
        self.fist_threshold = 0.15   # Distance threshold for fist
        self.zoom_threshold = 0.1    # Movement threshold for zoom
        
        if debug:
            print("👋 GestureDetector initialized with fixed landmark drawing")
    
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def detect_pinch(self, landmarks) -> Dict[str, Any]:
        """Detect pinch gesture (thumb tip close to index finger tip)"""
        # Get thumb tip and index finger tip positions
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        # Calculate distance
        distance = self.calculate_distance(thumb_tip, index_tip)
        
        if distance < self.pinch_threshold:
            # Calculate pinch center position
            center_x = (thumb_tip[0] + index_tip[0]) / 2
            center_y = (thumb_tip[1] + index_tip[1]) / 2
            
            # Calculate movement if we have previous position
            movement = (0, 0)
            if 'pinch' in self.prev_positions:
                prev_center = self.prev_positions['pinch']
                movement = (center_x - prev_center[0], center_y - prev_center[1])
            
            # Store current position
            self.prev_positions['pinch'] = (center_x, center_y)
            
            return {
                'gesture_type': 'pinch',
                'position': (center_x, center_y),
                'movement': movement,
                'confidence': max(0, 1 - distance / self.pinch_threshold)
            }
        
        return None
    
    def detect_fist(self, landmarks) -> Dict[str, Any]:
        """Detect fist gesture (all fingertips close to palm)"""
        # Get palm center (approximate)
        palm_center = landmarks[0]  # Wrist
        
        # Get fingertip positions
        fingertips = [landmarks[4], landmarks[8], landmarks[12], landmarks[16], landmarks[20]]
        
        # Calculate average distance from palm to fingertips
        total_distance = 0
        for tip in fingertips:
            total_distance += self.calculate_distance(palm_center, tip)
        
        avg_distance = total_distance / len(fingertips)
        
        if avg_distance < self.fist_threshold:
            # Calculate hand center position
            center_x = sum([lm[0] for lm in landmarks]) / len(landmarks)
            center_y = sum([lm[1] for lm in landmarks]) / len(landmarks)
            
            # Calculate movement if we have previous position
            movement = (0, 0)
            if 'fist' in self.prev_positions:
                prev_center = self.prev_positions['fist']
                movement = (center_x - prev_center[0], center_y - prev_center[1])
            
            # Store current position
            self.prev_positions['fist'] = (center_x, center_y)
            
            return {
                'gesture_type': 'fist',
                'position': (center_x, center_y),
                'movement': movement,
                'confidence': max(0, 1 - avg_distance / self.fist_threshold)
            }
        
        return None
    
    def detect_two_hand_zoom(self, left_landmarks, right_landmarks) -> Dict[str, Any]:
        """Detect two-hand zoom gesture"""
        # Get center positions of both hands
        left_center = (
            sum([lm[0] for lm in left_landmarks]) / len(left_landmarks),
            sum([lm[1] for lm in left_landmarks]) / len(left_landmarks)
        )
        
        right_center = (
            sum([lm[0] for lm in right_landmarks]) / len(right_landmarks),
            sum([lm[1] for lm in right_landmarks]) / len(right_landmarks)
        )
        
        # Calculate distance between hands
        current_distance = self.calculate_distance(left_center, right_center)
        
        # Calculate zoom factor based on distance change
        zoom_factor = 1.0
        if 'two_hand_distance' in self.prev_positions:
            prev_distance = self.prev_positions['two_hand_distance']
            if prev_distance > 0:
                zoom_factor = current_distance / prev_distance
                
                # Only register significant zoom changes
                if abs(zoom_factor - 1.0) < self.zoom_threshold:
                    zoom_factor = 1.0
        
        # Store current distance
        self.prev_positions['two_hand_distance'] = current_distance
        
        return {
            'gesture_type': 'two_hand_zoom',
            'zoom_factor': zoom_factor,
            'left_position': left_center,
            'right_position': right_center,
            'distance': current_distance
        }
    
    def normalize_landmarks(self, landmarks, frame_width, frame_height):
        """Convert MediaPipe landmarks to normalized coordinates"""
        normalized = []
        for landmark in landmarks.landmark:
            x = landmark.x
            y = landmark.y
            normalized.append((x, y))
        return normalized
    
    def detect_gestures(self, frame) -> Optional[Dict[str, Any]]:
        """Main gesture detection method - FIXED VERSION"""
        if frame is None:
            return None
        
        height, width, _ = frame.shape
        
        # FIXED: Process with MediaPipe (RGB conversion)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if not results.multi_hand_landmarks:
            return {'gesture_type': 'none'}
        
        num_hands = len(results.multi_hand_landmarks)
        hands_drawn = 0
        
        # FIXED: Always draw landmarks with proper specifications
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks and connections on the original BGR frame
            self.mp_draw.draw_landmarks(
                frame, 
                hand_landmarks, 
                self.mp_hands.HAND_CONNECTIONS,
                landmark_drawing_spec=self.landmark_drawing_spec,
                connection_drawing_spec=self.connection_drawing_spec
            )
            hands_drawn += 1
        
        if self.debug:
            print(f"🖐️ Drew landmarks for {hands_drawn} hands")
        
        # Single hand gestures
        if num_hands == 1:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Normalize landmarks
            landmarks = self.normalize_landmarks(hand_landmarks, width, height)
            
            # Try to detect pinch first (higher priority)
            pinch_gesture = self.detect_pinch(landmarks)
            if pinch_gesture:
                if self.debug:
                    print(f"📌 Pinch detected at {pinch_gesture['position']}")
                return pinch_gesture
            
            # Try to detect fist
            fist_gesture = self.detect_fist(landmarks)
            if fist_gesture:
                if self.debug:
                    print(f"✊ Fist detected at {fist_gesture['position']}")
                return fist_gesture
        
        # Two hand gestures
        elif num_hands == 2:
            left_hand = results.multi_hand_landmarks[0]
            right_hand = results.multi_hand_landmarks[1]
            
            # Normalize landmarks
            left_landmarks = self.normalize_landmarks(left_hand, width, height)
            right_landmarks = self.normalize_landmarks(right_hand, width, height)
            
            # Detect two-hand zoom
            zoom_gesture = self.detect_two_hand_zoom(left_landmarks, right_landmarks)
            if zoom_gesture and abs(zoom_gesture['zoom_factor'] - 1.0) > 0.05:
                if self.debug:
                    print(f"🔍 Two-hand zoom: {zoom_gesture['zoom_factor']:.2f}")
                return zoom_gesture
        
        return {'gesture_type': 'none'}
    
    def get_gesture_info(self) -> str:
        """Get current gesture information as string"""
        if hasattr(self, 'last_gesture') and self.last_gesture:
            gesture_type = self.last_gesture.get('gesture_type', 'none')
            if gesture_type == 'pinch':
                pos = self.last_gesture.get('position', (0, 0))
                return f"Pinch at ({pos[0]:.2f}, {pos[1]:.2f})"
            elif gesture_type == 'fist':
                return "Fist detected"
            elif gesture_type == 'two_hand_zoom':
                zoom = self.last_gesture.get('zoom_factor', 1.0)
                return f"Zoom factor: {zoom:.2f}"
        return "No gesture"
    
    def reset_tracking(self):
        """Reset gesture tracking state"""
        self.prev_positions = {}
        self.gesture_history = []
        if self.debug:
            print("🔄 Gesture tracking reset")