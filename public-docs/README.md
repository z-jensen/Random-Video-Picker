# Random Video Picker

A simple, cross-platform desktop application that randomly selects and plays videos from your collection.

## Features

- **Simple Core Functionality**: Choose folder, pick random video
- **Session Management**: Track played videos to avoid repeats
- **Optimized Video Preview**: Background thumbnails and detailed information
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Desktop Shortcuts**: Install to desktop/start menu easily
- **Keyboard Shortcuts**: Spacebar plays random video
- **Smart UI Layout**: Progressive disclosure with advanced features
- **Interactive Recent Videos**: Double-click to replay
- **Background Scanning**: No UI freeze on large folders
- **Fast Thumbnails**: Quick 20-second seek preview generation
- **Portable Mode**: Run from USB drives without installation

## Quick Start

### Installation

**Option 1: Standalone Executable (Recommended)**
```bash
# Clone the repository
git clone https://github.com/z-jensen/Random-Video-Picker.git
cd random-video-picker

# Build standalone executable (no Python required)
python build_executable.py

# Create desktop shortcuts
# Windows: .\create_shortcuts.bat
# macOS/Linux: ./create_shortcuts.sh
```

**Option 2: Python Package**
```bash
# Clone the repository
git clone https://github.com/z-jensen/Random-Video-Picker.git
cd random-video-picker

# Install dependencies
pip install -r requirements.txt

# Create desktop/start menu shortcuts
python install_shortcuts.py

# Run the application
python3 random_video_picker.py
```

### Requirements

### Core Dependencies
- Python 3.9+
- tkinter (included with most Python installations)

### Optional Dependencies (for enhanced features)
- FFmpeg (for video thumbnails and metadata)
- Pillow (for image processing)

Install optional dependencies with:
```bash
pip install -r requirements.txt  # Includes all optional dependencies
# or
python3 install_deps.py
```

## Supported Video Formats

- MP4 (.mp4)
- AVI (.avi)
- MKV (.mkv)
- MOV (.mov)
- WMV (.wmv)
- FLV (.flv)
- WebM (.webm)

## Keyboard Shortcuts

- **Spacebar**: Pick and play a random video
- **Escape**: Close the application

## Troubleshooting

### Video Won't Play
- Ensure you have a video player installed (VLC, Windows Media Player, etc.)
- Check that the video file isn't corrupted
- Try playing the file directly with your video player

### App Won't Start
- Verify Python 3.7+ is installed: `python3 --version`
- Install required dependencies: `pip install -r requirements.txt`

### No Videos Found
- Check that your folder contains supported video formats
- Ensure the folder and files are readable
- Try selecting a different folder

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have suggestions, please file an issue on GitHub.