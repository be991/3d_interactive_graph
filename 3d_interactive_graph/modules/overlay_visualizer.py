"""
overlay_visualizer.py - 3D graph visualization overlaid on camera feed
Creates interactive 3D network graph directly on camera view
"""

import cv2
import numpy as np
import networkx as nx
from typing import Dict, Any, List, Tuple, Optional
import math
import random

class OverlayGraphVisualizer:
    """3D graph visualizer that overlays on camera feed"""
    
    def __init__(self, debug=False):
        self.debug = debug
        
        # Graph data
        self.graph = None
        self.node_positions = {}  # 3D positions
        self.node_screen_positions = {}  # 2D screen positions
        self.edge_data = []
        
        # 3D camera parameters - FIXED: Camera looks towards negative Z
        self.camera_pos = np.array([0, 0, 8])  # Further back to see all nodes
        self.camera_target = np.array([0, 0, 0])
        self.camera_up = np.array([0, 1, 0])
        self.fov = 60  # Wider field of view
        self.zoom_factor = 1.5  # Start with some zoom
        
        # Rotation parameters
        self.rotation_x = 0
        self.rotation_y = 0
        
        # Screen parameters
        self.screen_width = 640
        self.screen_height = 480
        self.screen_center = (self.screen_width // 2, self.screen_height // 2)
        
        # Interaction parameters
        self.drag_sensitivity = 100
        self.rotate_sensitivity = 2.0
        self.zoom_sensitivity = 0.1
        
        # Visual parameters
        self.node_colors = {}
        self.selected_node = None
        
        # Initialize sample graph
        self._create_sample_graph()
        
        if debug:
            print("📊 OverlayGraphVisualizer initialized")
            print(f"🎥 Camera at: {self.camera_pos}, looking at: {self.camera_target}")
    
    def _create_sample_graph(self):
        """Create a sample 3D network graph"""
        # Create random network graph
        self.graph = nx.random_geometric_graph(25, 0.4, dim=3, seed=42)
        
        # Generate 3D positions
        pos = nx.spring_layout(self.graph, dim=3, k=2, iterations=100)
        
        # FIXED: Scale and position nodes in front of camera
        for node in pos:
            x, y, z = pos[node]
            self.node_positions[node] = np.array([
                (x - 0.5) * 3,  # X: -1.5 to 1.5
                (y - 0.5) * 3,  # Y: -1.5 to 1.5  
                (z - 0.5) * 2   # Z: -1 to 1 (in front of camera at z=8)
            ])
        
        # Generate node colors based on degree
        max_degree = max([self.graph.degree(node) for node in self.graph.nodes()])
        for node in self.graph.nodes():
            degree = self.graph.degree(node)
            # Color based on degree (blue to red)
            color_intensity = degree / max_degree if max_degree > 0 else 0
            self.node_colors[node] = (
                int(255 * color_intensity),      # Red
                int(100 * (1 - color_intensity)), # Green
                int(255 * (1 - color_intensity))  # Blue
            )
        
        # Prepare edge data
        self.edge_data = []
        for edge in self.graph.edges():
            node1, node2 = edge
            self.edge_data.append((node1, node2))
        
        if self.debug:
            print(f"📈 Created overlay graph: {len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges")
            # Debug: Print a few node positions
            for i, (node, pos) in enumerate(list(self.node_positions.items())[:3]):
                print(f"🔍 Node {node} at 3D position: {pos}")
    
    def _project_3d_to_2d(self, point_3d: np.ndarray) -> Tuple[int, int]:
        """Project 3D point to 2D screen coordinates - FIXED VERSION"""
        # Apply rotations
        # Rotate around Y axis (horizontal rotation)
        cos_y, sin_y = np.cos(self.rotation_y), np.sin(self.rotation_y)
        rotation_y = np.array([
            [cos_y, 0, sin_y],
            [0, 1, 0],
            [-sin_y, 0, cos_y]
        ])
        
        # Rotate around X axis (vertical rotation)
        cos_x, sin_x = np.cos(self.rotation_x), np.sin(self.rotation_x)
        rotation_x = np.array([
            [1, 0, 0],
            [0, cos_x, -sin_x],
            [0, sin_x, cos_x]
        ])
        
        # Apply rotations
        rotated_point = rotation_y @ rotation_x @ point_3d
        
        # FIXED: Calculate relative position correctly
        # Camera looks down negative Z, so points should be at negative Z relative to camera
        relative_pos = rotated_point - self.camera_pos
        
        # FIXED: Check if point is in front of camera (negative Z in our coordinate system)
        if relative_pos[2] >= -0.1:  # Point is behind or too close to camera
            return (-1000, -1000)  # Off-screen marker
        
        # FIXED: Perspective projection with correct Z handling
        focal_length = self.screen_height / (2 * np.tan(np.radians(self.fov / 2)))
        
        # Project to screen coordinates (note: we use -relative_pos[2] since camera looks down -Z)
        screen_x = int(self.screen_center[0] + (focal_length * relative_pos[0] / (-relative_pos[2])) * self.zoom_factor)
        screen_y = int(self.screen_center[1] - (focal_length * relative_pos[1] / (-relative_pos[2])) * self.zoom_factor)
        
        return (screen_x, screen_y)
    
    def _update_screen_positions(self):
        """Update 2D screen positions for all nodes"""
        visible_count = 0
        for node in self.graph.nodes():
            pos_3d = self.node_positions[node]
            screen_pos = self._project_3d_to_2d(pos_3d)
            self.node_screen_positions[node] = screen_pos
            
            # Count visible nodes for debugging
            if (0 <= screen_pos[0] < self.screen_width and 
                0 <= screen_pos[1] < self.screen_height):
                visible_count += 1
        
        if self.debug and visible_count == 0:
            print("⚠️ GRAPH DEBUG: No nodes visible on screen!")
            # Debug: Show first few node positions
            for i, (node, pos_3d) in enumerate(list(self.node_positions.items())[:3]):
                screen_pos = self._project_3d_to_2d(pos_3d)
                print(f"🔍 Node {node}: 3D{pos_3d} -> 2D{screen_pos}")
        elif self.debug:
            print(f"✅ GRAPH DEBUG: {visible_count} nodes visible on screen")
    
    def draw_graph_on_frame(self, frame: np.ndarray) -> np.ndarray:
        """Draw the 3D graph overlay on the camera frame"""
        if frame is None:
            return frame
        
        # Update frame dimensions if changed
        h, w = frame.shape[:2]
        if w != self.screen_width or h != self.screen_height:
            self.screen_width, self.screen_height = w, h
            self.screen_center = (w // 2, h // 2)
            if self.debug:
                print(f"📺 Screen size updated: {w}x{h}")
        
        # Update screen positions
        self._update_screen_positions()
        
        # Draw edges first (so they appear behind nodes)
        self._draw_edges(frame)
        
        # Draw nodes
        self._draw_nodes(frame)
        
        # Draw UI elements
        self._draw_ui_elements(frame)
        
        # KEEP: Debug green circle to confirm drawing pipeline works
        cv2.circle(frame, (50, 50), 10, (0, 255, 0), -1)
        
        return frame
    
    def _draw_edges(self, frame: np.ndarray):
        """Draw graph edges"""
        edges_drawn = 0
        for node1, node2 in self.edge_data:
            pos1 = self.node_screen_positions.get(node1, (-1000, -1000))
            pos2 = self.node_screen_positions.get(node2, (-1000, -1000))
            
            # Only draw if both nodes are on screen
            if (0 <= pos1[0] < self.screen_width and 0 <= pos1[1] < self.screen_height and
                0 <= pos2[0] < self.screen_width and 0 <= pos2[1] < self.screen_height):
                
                cv2.line(frame, pos1, pos2, (100, 100, 100), 2)
                edges_drawn += 1
        
        if self.debug and edges_drawn > 0:
            print(f"📏 Drew {edges_drawn} edges")
    
    def _draw_nodes(self, frame: np.ndarray):
        """Draw graph nodes"""
        # Sort nodes by Z distance (draw far nodes first)
        nodes_with_z = []
        for node in self.graph.nodes():
            pos_3d = self.node_positions[node]
            # Calculate distance from camera
            dist = np.linalg.norm(pos_3d - self.camera_pos)
            nodes_with_z.append((node, dist))
        
        # Sort by distance (farthest first)
        nodes_with_z.sort(key=lambda x: x[1], reverse=True)
        
        nodes_drawn = 0
        for node, _ in nodes_with_z:
            screen_pos = self.node_screen_positions.get(node, (-1000, -1000))
            
            # Only draw if node is on screen
            if (0 <= screen_pos[0] < self.screen_width and 
                0 <= screen_pos[1] < self.screen_height):
                
                color = self.node_colors[node]
                radius = 8
                
                # Highlight selected node
                if node == self.selected_node:
                    radius = 12
                    cv2.circle(frame, screen_pos, radius + 2, (255, 255, 0), 2)
                
                # Draw node
                cv2.circle(frame, screen_pos, radius, color, -1)
                cv2.circle(frame, screen_pos, radius, (255, 255, 255), 1)
                
                # Draw node label
                label = f"{node}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.4
                font_thickness = 1
                
                (label_w, label_h), _ = cv2.getTextSize(label, font, font_scale, font_thickness)
                label_pos = (screen_pos[0] - label_w // 2, screen_pos[1] + radius + label_h + 2)
                
                # Draw label background
                cv2.rectangle(frame, 
                             (label_pos[0] - 2, label_pos[1] - label_h - 2),
                             (label_pos[0] + label_w + 2, label_pos[1] + 2),
                             (0, 0, 0), -1)
                
                cv2.putText(frame, label, label_pos, font, font_scale, (255, 255, 255), font_thickness)
                nodes_drawn += 1
        
        if self.debug and nodes_drawn > 0:
            print(f"🔵 Drew {nodes_drawn} nodes")
    
    def _draw_ui_elements(self, frame: np.ndarray):
        """Draw UI elements and instructions"""
        # Draw instructions
        instructions = [
            "Pinch + drag to move nodes",
            "Fist + move to rotate graph", 
            "Two hands to zoom in/out",
            "Voice: 'rotate mode', 'drag mode', 'zoom mode'"
        ]
        
        y_offset = 30
        for i, instruction in enumerate(instructions):
            cv2.putText(frame, instruction, (10, y_offset + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw mode indicator in top-right
        mode_text = f"Zoom: {self.zoom_factor:.1f}x"
        cv2.putText(frame, mode_text, (self.screen_width - 150, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    def find_closest_node(self, screen_position: Tuple[int, int]) -> Optional[int]:
        """Find the closest node to a screen position"""
        min_distance = float('inf')
        closest_node = None
        
        for node in self.graph.nodes():
            node_pos = self.node_screen_positions.get(node, (-1000, -1000))
            
            # Only consider nodes on screen
            if (0 <= node_pos[0] < self.screen_width and 
                0 <= node_pos[1] < self.screen_height):
                
                distance = np.sqrt((node_pos[0] - screen_position[0])**2 + 
                                 (node_pos[1] - screen_position[1])**2)
                
                if distance < min_distance and distance < 50:  # Within 50 pixels
                    min_distance = distance
                    closest_node = node
        
        return closest_node
    
    def drag_node(self, gesture_position: Tuple[float, float], movement: Tuple[float, float]):
        """Handle node dragging based on gesture"""
        if not movement or (movement[0] == 0 and movement[1] == 0):
            return
        
        # Convert normalized gesture position to screen coordinates
        screen_x = int(gesture_position[0] * self.screen_width)
        screen_y = int(gesture_position[1] * self.screen_height)
        
        # Find closest node
        closest_node = self.find_closest_node((screen_x, screen_y))
        
        if closest_node is not None:
            self.selected_node = closest_node
            
            # Convert movement to 3D space
            movement_3d = np.array([
                movement[0] * self.drag_sensitivity * 0.01,
                -movement[1] * self.drag_sensitivity * 0.01,  # Invert Y
                0
            ])
            
            # Apply movement
            self.node_positions[closest_node] += movement_3d
            
            if self.debug:
                print(f"🖱️ Dragged node {closest_node}")
    
    def rotate_graph(self, movement: Tuple[float, float]):
        """Handle graph rotation based on gesture"""
        if not movement or (movement[0] == 0 and movement[1] == 0):
            return
        
        # Update rotation angles
        self.rotation_y += movement[0] * self.rotate_sensitivity * 0.01
        self.rotation_x += movement[1] * self.rotate_sensitivity * 0.01
        
        # Clamp rotation_x to avoid gimbal lock
        self.rotation_x = max(-np.pi/2, min(np.pi/2, self.rotation_x))
        
        if self.debug:
            print(f"🔄 Rotated graph: X={self.rotation_x:.2f}, Y={self.rotation_y:.2f}")
    
    def zoom_graph(self, zoom_factor: float):
        """Handle graph zoom based on gesture"""
        if abs(zoom_factor - 1.0) < 0.05:  # Ignore small changes
            return
        
        # Update zoom factor
        self.zoom_factor *= zoom_factor
        
        # Clamp zoom levels
        self.zoom_factor = max(0.2, min(5.0, self.zoom_factor))
        
        if self.debug:
            print(f"🔍 Zoomed graph to {self.zoom_factor:.2f}x")
    
    def reset_camera(self):
        """Reset camera to default position"""
        self.camera_pos = np.array([0, 0, 8])  # FIXED: Further back
        self.rotation_x = 0
        self.rotation_y = 0
        self.zoom_factor = 1.5  # Start with some zoom
        self.selected_node = None
        
        if self.debug:
            print("🏠 Camera view reset")
    
    def get_graph_info(self) -> str:
        """Get current graph information"""
        return f"Nodes: {len(self.graph.nodes)}, Edges: {len(self.graph.edges)}, Zoom: {self.zoom_factor:.1f}x"