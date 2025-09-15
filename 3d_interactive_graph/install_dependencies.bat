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
pip install mediapipe==0.10.7

echo.
echo Installing Plotly and Dash...
pip install plotly==5.17.0
pip install dash==2.14.2
pip install dash-bootstrap-components==1.5.0

echo.
echo Installing Scientific Computing libraries...
pip install numpy==1.24.3
pip install pandas==1.5.3
pip install networkx==3.2.1

echo.
echo Installing Speech Recognition...
pip install SpeechRecognition==3.10.0
pip install pocketsphinx==5.0.0

echo.
echo Installing PyAudio (this might take a while)...
pip install pyaudio==0.2.11

if errorlevel 1 (
    echo.
    echo PyAudio installation failed. Trying alternative method...
    echo Please download the appropriate PyAudio wheel from:
    echo https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
    echo Then install manually with: pip install PyAudio-X.X.X-cpXX-cpXX-win_amd64.whl
    echo.
)

echo.
echo Installation complete!
echo.
echo To run the application:
echo   python main.py
echo.
echo For debug mode:
echo   python main.py --debug
echo.
pause