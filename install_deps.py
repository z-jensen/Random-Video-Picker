#!/usr/bin/env python3
"""
Install optional dependencies for Random Video Picker.
This script installs PIL/Pillow for thumbnail support and checks for ffmpeg.
"""

import subprocess
import sys
from pathlib import Path


def install_pillow():
    """Install Pillow for thumbnail support."""
    print("Installing Pillow for thumbnail support...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        print("✅ Pillow installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Pillow automatically.")
        print("Please install it manually with: pip install Pillow")
        return False


def check_ffmpeg():
    """Check if ffmpeg is available."""
    print("Checking for ffmpeg...")
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅ ffmpeg is available!")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ffmpeg not found.")
        print("To install ffmpeg:")
        print("  - Windows: Download from https://ffmpeg.org/download.html")
        print("  - macOS: brew install ffmpeg")
        print("  - Linux: sudo apt install ffmpeg (Ubuntu/Debian)")
        return False


def main():
    """Main installation function."""
    print("Random Video Picker - Optional Dependencies Setup")
    print("=" * 50)
    
    # Check and install Pillow
    try:
        import PIL
        print("✅ Pillow is already installed!")
    except ImportError:
        install_pillow()
    
    # Check for ffmpeg
    check_ffmpeg()
    
    print("\n" + "=" * 50)
    print("Setup complete! The app will work even without these dependencies,")
    print("but thumbnails and video details will be limited.")
    print("\nNote: ffmpeg is used for:")
    print("  - Generating video thumbnails")
    print("  - Extracting video duration and resolution")
    print("  - Better video information")


if __name__ == "__main__":
    main()