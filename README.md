# 🎬 Random Video Picker

A simple, cross-platform desktop application for randomly selecting and playing videos from your collection.

## Features

- **Simple Core Functionality**: Choose folder, pick random video
- **Session Management**: Track played videos to avoid repeats
- **Optimized Video Preview**: Background thumbnails and detailed information
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Keyboard Shortcuts**: Spacebar plays random video
- **Smart UI Layout**: Progressive disclosure with advanced features
- **Interactive Recent Videos**: Double-click to replay
- **Background Scanning**: No UI freeze on large folders
- **Fast Thumbnails**: Quick 20-second seek preview generation
- **Portable Mode**: Run from USB drives without installation

## Quick Start

### Requirements
- Python 3.9+
- Tkinter (included with Python)

### Optional Dependencies
- Pillow (for video thumbnails)
- ffmpeg (for video info extraction and thumbnails)

### Installation

**Option 1: Direct Download**
```bash
# Clone or download the repository
git clone https://github.com/z-jensen/Random-Video-Picker.git
cd random-video-picker

# Install dependencies (optional)
pip install -r requirements.txt

# Run the app
python3 random_video_picker.py
```

**Option 2: Install via pip (from GitHub)**
```bash
pip install git+https://github.com/z-jensen/Random-Video-Picker.git
random-video-picker
```

## Portable Mode

Run the app from a USB drive or portable directory without installation:

### On Windows
```bash
# Run the make_portable.bat script
make_portable.bat

# Or create empty .portable file manually
# Then run the app
python random_video_picker.py
```

### On macOS/Linux
```bash
# Run the make_portable.sh script
./make_portable.sh

# Or create empty .portable file manually
touch .portable

# Then run the app
python3 random_video_picker.py
```

In portable mode, all settings and state are saved in the `.random_video_picker/` folder instead of your home folder, making it perfect for USB drives.

## Documentation

For detailed information, see the [public-docs/](public-docs/) folder:

- [CONTRIBUTING.md](public-docs/CONTRIBUTING.md) - How to contribute to the project

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and detailed changes.

## Project Structure

```
random-video-picker/
├── random_video_picker.py    # Main GUI application
├── video_scanner.py          # Video discovery and session management
├── video_player.py           # Cross-platform video playback
├── video_preview.py          # Thumbnail and metadata extraction
├── install_deps.py           # Dependency installation script
├── make_portable.bat        # Windows portable mode script
├── make_portable.sh         # macOS/Linux portable mode script
├── requirements.txt          # Python dependencies
├── setup.py                 # Package installation
├── LICENSE                  # MIT License
├── .gitignore               # Git ignore patterns
├── README.md                # This file
├── CHANGELOG.md             # Version history
├── public-docs/            # Public documentation
│   ├── CONTRIBUTING.md
│   ├── AGENTS.md
│   ├── UI_DESIGN.md
│   ├── FEATURE_SPEC.md
│   ├── ARCHITECTURE.md
│   └── PERFORMANCE.md
└── private-docs/           # Private documentation (not in repo)
```

## Keyboard Shortcuts

- **Spacebar**: Pick and play a random video
- **Double-click** on recent videos: Replay without affecting progress

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
