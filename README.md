# 3D Interactive Graph with Gesture and Voice Control

## Project Overview
This project creates an interactive 3D network graph that responds to hand gestures and voice commands. The 3D graph is **overlaid directly on the camera feed**, allowing you to see your hands and the graph simultaneously for intuitive control, just like in AR/VR applications.

## Key Features
- **Camera Overlay Visualization**: 3D graph appears directly on your camera feed
- **Hand Gesture Control**: Pinch-drag nodes, fist-rotate graph, two-hand zoom
- **Voice Commands**: Switch modes and control graph with speech
- **Real-time Interaction**: Smooth, responsive control with minimal latency
- **Offline Speech Recognition**: Uses Vosk for privacy-friendly voice control

## Directory Structure
```
3d_interactive_graph/
├── main.py                      # Main application entry point
├── requirements.txt             # Updated Python dependencies
├── install_dependencies.bat     # Windows installation script
├── setup_vosk.py               # Automatic Vosk model download
├── modules/
│   ├── __init__.py
│   ├── gesture_detector.py     # Hand gesture recognition
│   ├── voice_controller.py     # Voice command recognition (updated for Vosk)
│   └── overlay_visualizer.py   # NEW: Camera overlay 3D visualization
├── data/
│   └── sample_graph.json      # Sample graph data
└── README.md                  # This file
```

## Installation Requirements

### Prerequisites
- Windows 10/11
- Python 3.8 or newer
- VS Code
- Webcam and microphone

### Step 1: Install Python Dependencies
Your updated requirements.txt works perfectly:

```bash
pip install -r requirements.txt
```

Or run the batch script:
```bash
install_dependencies.bat
```

### Step 2: Setup Vosk Speech Model
Run the automatic setup:
```bash
python setup_vosk.py
```

Or download manually:
1. Download: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
2. Extract to project directory
3. Rename folder to: `vosk-model-small-en-us-0.15`

## Updated Dependencies Explained

### Changes Made:
1. **MediaPipe**: Updated to 0.10.21 (latest stable)
2. **Removed PyAudio/PocketSphinx**: These caused your installation errors
3. **Added Vosk**: Better offline speech recognition
4. **Added SoundDevice**: More reliable audio capture
5. **Updated NumPy/Pandas**: Latest stable versions

### Why These Changes:
- **PyAudio issues**: Notoriously difficult to install on Windows
- **PocketSphinx problems**: Deprecated distutils caused your error
- **Vosk advantages**: Better accuracy, easier installation, fully offline

## Running the Application

### Step 1: Setup Project
```bash
mkdir 3d_interactive_graph
cd 3d_interactive_graph
# Copy all files to appropriate locations
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
python setup_vosk.py
```

### Step 3: Run Application
```bash
python main.py
```

### Step 4: Using the Camera Overlay Interface
1. **Camera opens** showing your video feed
2. **3D graph appears overlaid** on the camera view
3. **Your hands are visible** along with the graph
4. **Use gestures** to interact directly with the 3D visualization
5. **Speak commands** to switch interaction modes

## Gesture Controls
- **Pinch + Drag**: Make pinch gesture (thumb + index finger) and move to drag nodes
- **Fist + Move**: Make fist and move hand to rotate entire graph
- **Two Hands Zoom**: Move both hands apart/together to zoom in/out

## Voice Commands
- **"rotate mode"** - Switch to rotation mode
- **"drag mode"** - Switch to drag mode  
- **"zoom mode"** - Switch to zoom mode
- **"reset view"** - Reset camera to default position

## Keyboard Controls
- **'r'** - Reset graph view
- **'q' or ESC** - Quit application

## Updated Troubleshooting

### Installation Issues (Fixed!)
1. **PyAudio errors**: No longer needed - using SoundDevice
2. **PocketSphinx distutils error**: Replaced with Vosk
3. **Version conflicts**: All dependencies updated to compatible versions

### Common Issues and Solutions

1. **Vosk model not found**:
   ```bash
   python setup_vosk.py
   ```

2. **Camera not working**:
   - Check Windows camera permissions
   - Close other camera applications
   - Try different camera index in main.py

3. **Voice recognition not working**:
   - Check microphone permissions
   - Speak clearly and loudly
   - Test with: `python -c "import sounddevice; print(sounddevice.query_devices())"`

4. **Graph not visible**:
   - Ensure good lighting
   - Move closer/further from camera
   - Press 'r' to reset view

5. **Gesture detection issues**:
   - Keep hands clearly visible
   - Use contrasting background
   - Check MediaPipe version compatibility

## Performance Requirements
- **CPU**: Intel i5 or AMD Ryzen 5 (minimum)
- **RAM**: 8GB (minimum), 16GB (recommended)
- **Camera**: Any USB webcam or built-in camera (720p recommended)
- **Microphone**: Any USB or built-in microphone

## What's New in This Version

### Major Improvements:
1. **Camera Overlay Interface**: 3D graph appears directly on camera feed (like your image!)
2. **Better Speech Recognition**: Vosk provides more reliable offline recognition
3. **Simplified Installation**: No more PyAudio/PocketSphinx headaches
4. **Enhanced Visualization**: Better 3D projection and node interaction
5. **Improved Performance**: More efficient rendering and gesture processing

### Visual Experience:
- See your hands and the 3D graph simultaneously
- Real-time visual feedback for all interactions
- Professional AR-like interface
- Smooth animations and transitions

## Debug Mode
Enable verbose logging:
```bash
python main.py --debug
```

This shows detailed information about:
- Gesture detection accuracy
- Voice recognition results  
- 3D graph transformations
- Performance metrics

## Code Architecture

### Key Changes Made:
1. **New OverlayGraphVisualizer**: Replaces browser-based visualization
2. **Updated VoiceController**: Uses Vosk instead of SpeechRecognition/PocketSphinx  
3. **Enhanced GestureDetector**: Works with newer MediaPipe version
4. **Streamlined Main App**: Direct camera overlay, no separate browser window

The updated code addresses all the dependency issues you encountered while providing a much better user experience with the camera overlay interface!