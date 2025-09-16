@echo off
echo Installing 3D Interactive Graph Dependencies...
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install basic dependencies
echo.
echo Installing OpenCV and MediaPipe...
pip install opencv-python==4.8.1.78
pip install mediapipe==0.10.21

echo.
echo Installing Plotly and Dash...
pip install plotly==5.17.0
pip install dash==2.14.2
pip install dash-bootstrap-components==1.5.0

echo.
echo Installing Scientific Computing libraries...
pip install numpy==1.26.4
pip install pandas==2.2.3
pip install networkx==3.2.1

echo.
echo Installing Speech Recognition with Vosk...
pip install SpeechRecognition==3.10.0
pip install vosk==0.3.45
pip install sounddevice==0.5.2

echo.
echo Downloading Vosk speech model...
echo Please download the small English model from:
echo https://alphacephei.com/vosk/models
echo Download: vosk-model-small-en-us-0.15.zip
echo Extract it to the project directory and rename folder to: vosk-model-small-en-us-0.15
echo.

echo Installation complete!
echo.
echo IMPORTANT: Don't forget to download the Vosk model!
echo.
echo To run the application:
echo   python main.py
echo.
echo For debug mode:
echo   python main.py --debug
echo.
echo Controls:
echo   - Pinch + drag: Move nodes
echo   - Fist + move: Rotate graph
echo   - Two hands: Zoom in/out
echo   - Voice: "rotate mode", "drag mode", "zoom mode", "reset view"
echo   - Press 'r' to reset view, 'q' to quit
echo.
pause