"""
modules package - Contains gesture detection, voice control, and visualization modules
"""

# Remove the imports from __init__.py to avoid circular import issues
# The main.py file will import directly from each module

__all__ = ['GestureDetector', 'VoiceController', 'OverlayGraphVisualizer']