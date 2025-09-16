"""
setup_vosk.py - Download and setup Vosk speech recognition model
"""

import os
import urllib.request
import zipfile
import sys

def download_vosk_model():
    """Download and extract Vosk small English model"""
    
    model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    model_zip = "vosk-model-small-en-us-0.15.zip"
    model_dir = "vosk-model-small-en-us-0.15"
    
    # Check if model already exists
    if os.path.exists(model_dir):
        print(f"✅ Vosk model already exists at: {model_dir}")
        return True
    
    print("📥 Downloading Vosk speech recognition model...")
    print(f"   URL: {model_url}")
    print("   This may take a few minutes (approx 40MB)...")
    
    try:
        # Download with progress
        def show_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded * 100) // total_size)
                print(f"\r   Progress: {percent}% ({downloaded // (1024*1024):.1f}/{total_size // (1024*1024):.1f} MB)", end="")
        
        urllib.request.urlretrieve(model_url, model_zip, show_progress)
        print("\n✅ Download complete!")
        
        # Extract zip file
        print("📂 Extracting model...")
        with zipfile.ZipFile(model_zip, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # Clean up zip file
        os.remove(model_zip)
        
        print(f"✅ Vosk model setup complete!")
        print(f"   Model location: {os.path.abspath(model_dir)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to download Vosk model: {e}")
        print("\nManual setup instructions:")
        print("1. Download: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
        print("2. Extract to project directory")
        print("3. Ensure folder is named: vosk-model-small-en-us-0.15")
        return False

def test_vosk_setup():
    """Test if Vosk is properly set up"""
    try:
        import vosk
        model_dir = "vosk-model-small-en-us-0.15"
        
        if not os.path.exists(model_dir):
            print("❌ Vosk model directory not found")
            return False
        
        # Try to load model
        model = vosk.Model(model_dir)
        print("✅ Vosk model loaded successfully!")
        return True
        
    except ImportError:
        print("❌ Vosk not installed. Run: pip install vosk")
        return False
    except Exception as e:
        print(f"❌ Vosk setup error: {e}")
        return False

def main():
    print("🎤 Vosk Speech Recognition Setup")
    print("=" * 40)
    
    # Check if vosk is installed
    try:
        import vosk
        print("✅ Vosk library found")
    except ImportError:
        print("❌ Vosk not installed!")
        print("Run: pip install vosk==0.3.45")
        sys.exit(1)
    
    # Download model
    if download_vosk_model():
        # Test setup
        if test_vosk_setup():
            print("\n🎉 Vosk setup completed successfully!")
            print("You can now run the main application:")
            print("   python main.py")
        else:
            print("\n⚠️ Setup completed but testing failed")
            print("Try running the main application anyway")
    else:
        print("\n⚠️ Automatic setup failed")
        print("Please follow manual setup instructions above")

if __name__ == "__main__":
    main()