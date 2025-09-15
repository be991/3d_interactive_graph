"""
graph_visualizer.py - 3D graph visualization using Plotly and Dash
Creates interactive 3D network graph with gesture/voice control
"""

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import numpy as np
import threading
import time
import json
import webbrowser
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd

class GraphVisualizer:
    """3D graph visualizer using Plotly and Dash"""
    
    def __init__(self, debug=False):
        self.debug = debug
        
        # Graph data
        self.graph = None
        self.node_positions = {}
        self.edge_data = []
        
        # Camera and interaction state
        self.camera_position = {
            'eye': {'x': 1.5, 'y': 1.5, 'z': 1.5},
            'center': {'x': 0, 'y': 0, 'z': 0},
            'up': {'x': 0, 'y': 0, 'z': 1}
        }
        
        # Dash app
        self.app = None
        self.server_thread = None
        self.running = False
        
        # Interaction parameters
        self.drag_sensitivity = 0.5
        self.rotate_sensitivity = 2.0
        self.zoom_sensitivity = 1.5
        
        # Initialize sample graph
        self._create_sample_graph()
        
        if debug:
            print("📊 GraphVisualizer initialized")
    
    def _create_sample_graph(self):
        """Create a sample 3D network graph"""
        # Create random network graph
        self.graph = nx.random_geometric_graph(20, 0.3, dim=3, seed=42)
        
        # Generate 3D positions
        pos = nx.spring_layout(self.graph, dim=3, k=1, iterations=50)
        
        # Scale positions
        for node in pos:
            x, y, z = pos[node]
            self.node_positions[node] = {
                'x': x * 2,
                'y': y * 2, 
                'z': z * 2
            }
        
        # Prepare edge data
        self.edge_data = []
        for edge in self.graph.edges():
            node1, node2 = edge
            pos1 = self.node_positions[node1]
            pos2 = self.node_positions[node2]
            
            self.edge_data.append({
                'x_start': pos1['x'], 'y_start': pos1['y'], 'z_start': pos1['z'],
                'x_end': pos2['x'], 'y_end': pos2['y'], 'z_end': pos2['z']
            })
        
        if self.debug:
            print(f"📈 Created sample graph: {len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges")
    
    def _create_dash_app(self):
        """Create and configure Dash application"""
        self.app = dash.Dash(__name__)
        
        # App layout
        self.app.layout = html.Div([
            html.H1("3D Interactive Graph", 
                   style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
            
            html.Div([
                html.Div(id='status-display', 
                        style={'fontSize': '16px', 'marginBottom': '10px', 'textAlign': 'center'}),
                
                dcc.Graph(
                    id='3d-graph',
                    figure=self._create_graph_figure(),
                    style={'height': '80vh'},
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
                    }
                ),
                
                dcc.Interval(
                    id='update-interval',
                    interval=100,  # Update every 100ms
                    n_intervals=0
                ),
                
                # Hidden div to store graph state
                html.Div(id='graph-state', style={'display': 'none'})
            ])
        ])
        
        # Callbacks
        self._setup_callbacks()
    
    def _create_graph_figure(self):
        """Create 3D graph figure"""
        fig = go.Figure()
        
        # Add edges
        for edge in self.edge_data:
            fig.add_trace(go.Scatter3d(
                x=[edge['x_start'], edge['x_end'], None],
                y=[edge['y_start'], edge['y_end'], None],
                z=[edge['z_start'], edge['z_end'], None],
                mode='lines',
                line=dict(color='rgba(125, 125, 125, 0.5)', width=2),
                showlegend=False,
                hoverinfo='none'
            ))
        
        # Add nodes
        node_x = [self.node_positions[node]['x'] for node in self.graph.nodes()]
        node_y = [self.node_positions[node]['y'] for node in self.graph.nodes()]
        node_z = [self.node_positions[node]['z'] for node in self.graph.nodes()]
        
        # Color nodes by degree
        node_colors = [self.graph.degree(node) for node in self.graph.nodes()]
        
        fig.add_trace(go.Scatter3d(
            x=node_x,
            y=node_y,
            z=node_z,
            mode='markers',
            marker=dict(
                size=8,
                color=node_colors,
                colorscale='Viridis',
                colorbar=dict(title="Node Degree"),
                line=dict(width=0.5, color='white')
            ),
            text=[f'Node {i}<br>Degree: {self.graph.degree(i)}' for i in self.graph.nodes()],
            hoverinfo='text',
            name='Nodes'
        ))
        
        # Update layout
        fig.update_layout(
            title='3D Network Graph - Gesture & Voice Controlled',
            scene=dict(
                xaxis=dict(title='X', showbackground=True, backgroundcolor="rgba(0,0,0,0.1)"),
                yaxis=dict(title='Y', showbackground=True, backgroundcolor="rgba(0,0,0,0.1)"),
                zaxis=dict(title='Z', showbackground=True, backgroundcolor="rgba(0,0,0,0.1)"),
                camera=self.camera_position,
                bgcolor='rgba(240,240,240,0.8)'
            ),
            width=1200,
            height=800,
            margin=dict(r=20, b=10, l=10, t=40),
            showlegend=True
        )
        
        return fig
    
    def _setup_callbacks(self):
        """Setup Dash callbacks"""
        
        @self.app.callback(
            Output('3d-graph', 'figure'),
            [Input('update-interval', 'n_intervals')],
            [State('3d-graph', 'figure')]
        )
        def update_graph(n, current_fig):
            """Update graph based on gesture/voice input"""
            if current_fig is None:
                return self._create_graph_figure()
            
            # Update camera position
            if current_fig and 'layout' in current_fig:
                current_fig['layout']['scene']['camera'] = self.camera_position
            
            return current_fig
        
        @self.app.callback(
            Output('status-display', 'children'),
            [Input('update-interval', 'n_intervals')]
        )
        def update_status(n):
            """Update status display"""
            return html.Div([
                html.Span("🎯 Ready for gesture and voice commands", 
                         style={'color': 'green', 'fontWeight': 'bold'}),
                html.Br(),
                html.Span(f"Camera: Eye({self.camera_position['eye']['x']:.1f}, "
                         f"{self.camera_position['eye']['y']:.1f}, "
                         f"{self.camera_position['eye']['z']:.1f})",
                         style={'fontSize': '12px', 'color': 'gray'})
            ])
    
    def start_server(self):
        """Start Dash server in separate thread"""
        if self.running:
            return
        
        self._create_dash_app()
        
        def run_server():
            self.app.run_server(
                debug=False,
                host='127.0.0.1',
                port=8050,
                use_reloader=False,
                dev_tools_silence_routes_logging=True
            )
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.running = True
        
        # Wait a moment then open browser
        time.sleep(2)
        try:
            webbrowser.open('http://127.0.0.1:8050')
            if self.debug:
                print("🌐 Browser opened to http://127.0.0.1:8050")
        except Exception as e:
            print(f"❌ Could not open browser automatically: {e}")
            print("   Please manually open: http://127.0.0.1:8050")
    
    def stop_server(self):
        """Stop Dash server"""
        self.running = False
        if self.debug:
            print("🛑 Graph visualization server stopped")
    
    def drag_node(self, gesture_position: Tuple[float, float], movement: Tuple[float, float]):
        """Handle node dragging based on gesture"""
        if not movement or (movement[0] == 0 and movement[1] == 0):
            return
        
        # Find closest node to gesture position
        min_distance = float('inf')
        closest_node = None
        
        for node in self.graph.nodes():
            pos = self.node_positions[node]
            # Simple 2D distance for screen-space interaction
            distance = np.sqrt((pos['x'] - gesture_position[0])**2 + 
                             (pos['y'] - gesture_position[1])**2)
            if distance < min_distance:
                min_distance = distance
                closest_node = node
        
        # Move closest node
        if closest_node is not None:
            pos = self.node_positions[closest_node]
            pos['x'] += movement[0] * self.drag_sensitivity
            pos['y'] += movement[1] * self.drag_sensitivity
            
            if self.debug:
                print(f"🖱️ Dragged node {closest_node} by {movement}")
    
    def rotate_graph(self, movement: Tuple[float, float]):
        """Handle graph rotation based on gesture"""
        if not movement or (movement[0] == 0 and movement[1] == 0):
            return
        
        # Update camera eye position for rotation
        eye = self.camera_position['eye']
        
        # Convert movement to rotation
        rotation_x = movement[1] * self.rotate_sensitivity * 0.01  # Vertical movement -> X rotation
        rotation_y = movement[0] * self.rotate_sensitivity * 0.01  # Horizontal movement -> Y rotation
        
        # Simple rotation around center
        current_radius = np.sqrt(eye['x']**2 + eye['y']**2 + eye['z']**2)
        
        # Update eye position
        eye['x'] += rotation_y
        eye['y'] += rotation_x
        
        # Maintain distance from center
        actual_radius = np.sqrt(eye['x']**2 + eye['y']**2 + eye['z']**2)
        if actual_radius > 0:
            scale_factor = current_radius / actual_radius
            eye['x'] *= scale_factor
            eye['y'] *= scale_factor
            eye['z'] *= scale_factor
        
        if self.debug:
            print(f"🔄 Rotated graph by {movement}")
    
    def zoom_graph(self, zoom_factor: float):
        """Handle graph zoom based on gesture"""
        if abs(zoom_factor - 1.0) < 0.05:  # Ignore small changes
            return
        
        # Update camera eye position for zoom
        eye = self.camera_position['eye']
        
        # Scale eye position to zoom in/out
        inverse_zoom = 1.0 / (zoom_factor * self.zoom_sensitivity)
        
        eye['x'] *= inverse_zoom
        eye['y'] *= inverse_zoom  
        eye['z'] *= inverse_zoom
        
        # Clamp zoom levels
        current_distance = np.sqrt(eye['x']**2 + eye['y']**2 + eye['z']**2)
        if current_distance < 0.5:  # Too close
            scale = 0.5 / current_distance
            eye['x'] *= scale
            eye['y'] *= scale
            eye['z'] *= scale
        elif current_distance > 10.0:  # Too far
            scale = 10.0 / current_distance
            eye['x'] *= scale
            eye['y'] *= scale
            eye['z'] *= scale
        
        if self.debug:
            print(f"🔍 Zoomed graph by factor {zoom_factor}")
    
    def reset_camera(self):
        """Reset camera to default position"""
        self.camera_position = {
            'eye': {'x': 1.5, 'y': 1.5, 'z': 1.5},
            'center': {'x': 0, 'y': 0, 'z': 0},
            'up': {'x': 0, 'y': 0, 'z': 1}
        }
        if self.debug:
            print("🏠 Camera position reset")
    
    def load_graph_from_file(self, filepath: str):
        """Load graph from file (JSON or GraphML)"""
        try:
            if filepath.endswith('.json'):
                with open(filepath, 'r') as f:
                    graph_data = json.load(f)
                self.graph = nx.node_link_graph(graph_data)
            elif filepath.endswith('.graphml'):
                self.graph = nx.read_graphml(filepath)
            else:
                print(f"❌ Unsupported file format: {filepath}")
                return False
            
            # Regenerate positions
            pos = nx.spring_layout(self.graph, dim=3, k=1, iterations=50)
            for node in pos:
                x, y, z = pos[node]
                self.node_positions[node] = {'x': x * 2, 'y': y * 2, 'z': z * 2}
            
            print(f"✅ Loaded graph from {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load graph from {filepath}: {e}")
            return False