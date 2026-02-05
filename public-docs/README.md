# Random Video Picker

A simple, cross-platform desktop application that randomly selects and plays videos from your collection.

## Features

- **Random Video Selection**: Pick videos from any folder with a single click
- **Progress Tracking**: Never watch the same video twice in a session
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Portable Mode**: Run from USB drives without installation
- **Keyboard Shortcuts**: Press spacebar to quickly pick and play videos

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/z-jensen/Random-Video-Picker.git
cd random-video-picker

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 random_video_picker.py
```

### Requirements

### Core Dependencies
- Python 3.12+
- tkinter (included with most Python installations)

### Optional Dependencies (for enhanced features)
- FFmpeg (for video thumbnails and metadata)
- Pillow (for image processing)

Install optional dependencies with:
```bash
pip install -r requirements.txt  # Includes all optional dependencies
```

## Requirements

### Core Dependencies
- Python 3.7+
- tkinter (included with most Python installations)

### Optional Dependencies (for enhanced features)
- FFmpeg (for video thumbnails and metadata)
- Pillow (for image processing)

Install optional dependencies with:
```bash
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