# 3D Interactive Graph with Gesture and Voice Control

## Project Overview
This project creates an interactive 3D network graph that responds to hand gestures and voice commands using MediaPipe for gesture recognition, SpeechRecognition for voice commands, and Plotly for 3D visualization.

## Directory Structure
```
3d_interactive_graph/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── modules/
│   ├── __init__.py
│   ├── gesture_detector.py # Hand gesture recognition
│   ├── voice_controller.py # Voice command recognition
│   └── graph_visualizer.py # 3D graph visualization
├── data/
│   └── sample_graph.json  # Sample graph data
└── README.md              # This file
```

## Installation Requirements

### Prerequisites
- Windows 10/11
- Python 3.8 or newer
- VS Code
- Webcam and microphone
- Chrome browser (for Plotly visualization)

### Step 1: Install Python Dependencies
Create a `requirements.txt` file and install packages:

```bash
pip install opencv-python==4.8.1.78
pip install mediapipe==0.10.21
pip install plotly==5.17.0
pip install dash==2.14.2
pip install dash-bootstrap-components==1.5.0
pip install SpeechRecognition==3.10.0
pip install sounddevice==0.5.2
pip install numpy==1.26.4
pip install pandas==2.2.3
pip install networkx==3.2.1
pip install threading-timer==0.1.2
pip install vosk==0.3.45
```

**Note for PyAudio**: If PyAudio installation fails, download the appropriate wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio and install manually:
```bash
pip install PyAudio-0.2.11-cp311-cp311-win_amd64.whl
```

## Module Breakdown

### 1. Hand Gesture Detection Module (`gesture_detector.py`)
- Uses MediaPipe to detect hand landmarks
- Recognizes gestures: pinch, fist, two-hand zoom
- Calculates gesture positions and movements
- Handles gesture state transitions

### 2. Voice Command Module (`voice_controller.py`)
- Uses SpeechRecognition with Windows Speech Recognition
- Recognizes commands: "rotate mode", "drag mode", "zoom mode", "reset view"
- Runs in separate thread to avoid blocking
- Handles microphone permissions and errors

### 3. 3D Graph Visualization Module (`graph_visualizer.py`)
- Creates interactive 3D network graph using Plotly
- Handles node positioning and edge rendering
- Manages camera transformations (rotate, zoom, pan)
- Updates visualization based on gesture/voice input

### 4. Main Application (`main.py`)
- Coordinates all modules
- Handles mode switching
- Manages real-time updates
- Provides user interface

## Running the Application

### Step 1: Setup Project
1. Create project directory: `3d_interactive_graph`
2. Copy all code files to appropriate locations
3. Open folder in VS Code

### Step 2: Install Dependencies
Open VS Code terminal (Ctrl+`) and run:
```bash
cd 3d_interactive_graph
pip install -r requirements.txt
```

### Step 3: Grant Permissions
- Allow camera access when prompted
- Allow microphone access when prompted
- Ensure Chrome is set as default browser

### Step 4: Run Application
```bash
python main.py
```

### Step 5: Using the Application
1. Application opens webcam window and browser
2. Hold hand in front of camera for gesture control
3. Speak voice commands clearly
4. Browser shows 3D graph that responds to gestures

## Gesture Controls
- **Pinch + Drag**: Move individual nodes (make pinch gesture with thumb/index finger)
- **Fist + Move**: Rotate entire graph (make fist with hand)
- **Two Hands Zoom**: Move hands apart/together to zoom in/out

## Voice Commands
- "rotate mode" - Switch to rotation mode
- "drag mode" - Switch to drag mode  
- "zoom mode" - Switch to zoom mode
- "reset view" - Reset camera to default position

## Troubleshooting

### Common Issues and Solutions

1. **Camera not working**:
   - Check if other applications are using camera
   - Restart application
   - Check Windows camera permissions

2. **Voice recognition not working**:
   - Speak clearly and loudly
   - Check microphone permissions
   - Ensure Windows Speech Recognition is enabled

3. **Gesture detection lag**:
   - Close other applications using camera
   - Reduce lighting variations
   - Keep hands clearly visible

4. **Browser not opening**:
   - Set Chrome as default browser
   - Check if port 8050 is available
   - Manually open http://localhost:8050

5. **PyAudio installation errors**:
   - Use precompiled wheel for Windows
   - Install Microsoft Visual C++ Build Tools
   - Try alternative: `pip install pipwin && pipwin install pyaudio`

### Performance Optimization
- Close unnecessary applications
- Use good lighting for gesture detection
- Keep microphone close for voice commands
- Use dedicated graphics card if available

## System Requirements
- **CPU**: Intel i5 or AMD Ryzen 5 (minimum)
- **RAM**: 8GB (minimum), 16GB (recommended)
- **Camera**: Any USB webcam or built-in camera
- **Microphone**: Any USB microphone or built-in microphone
- **Browser**: Chrome/Chromium (recommended)

## Known Limitations
1. Voice recognition requires internet connection for best results
2. Gesture detection works best in good lighting
3. May have slight latency on older hardware
4. Requires Chrome browser for optimal 3D visualization

## Debug Mode
Add `--debug` flag when running to enable verbose logging:
```bash
python main.py --debug
```

This will show detailed information about gesture detection and voice recognition in the console.