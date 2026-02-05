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

**Option 1: Standalone Executable (Recommended)**
```bash
# Clone or download the repository
git clone https://github.com/z-jensen/Random-Video-Picker.git
cd random-video-picker

# Build executable (fast startup, no Python required)
python build_executable.py

# Run the app
dist/RandomVideoPicker/RandomVideoPicker.exe  # Windows
./dist/RandomVideoPicker/RandomVideoPicker     # macOS/Linux
```

**Option 2: Python Package**
```bash
# Clone or download the repository
git clone https://github.com/z-jensen/Random-Video-Picker.git
cd random-video-picker

# Install dependencies
pip install -r requirements.txt

# Run the app
python random_video_picker.py

# Optional: Create shortcuts
python install_shortcuts_simple.py
```

**Option 3: Install via pip**
```bash
pip install git+https://github.com/z-jensen/Random-Video-Picker.git
random-video-picker
```

## Portable Mode

Run the app from a USB drive or portable directory without installation.

### What is Portable Mode?

Portable mode saves all application data locally instead of in system folders:
- **Normal mode**: Settings saved in your home directory
- **Portable mode**: Settings saved in `.random_video_picker/` folder next to the app

This makes it perfect for:
- Running from USB drives
- Keeping the app self-contained
- Moving between different computers

### How to Enable Portable Mode

**Option 1: Use the provided scripts**

### On Windows
```bash
# Run the batch script (from Command Prompt or PowerShell)
.\make_portable.bat
```

### On macOS/Linux
```bash
# Run the shell script
./make_portable.sh
```

**Option 2: Create the marker file manually**

### On Windows
```bash
# Create empty .portable file
type nul > .portable
```

### On macOS/Linux
```bash
# Create empty .portable file
touch .portable
```

### How to Use Portable Mode

1. **Enable it**: Run one of the commands above to create the `.portable` file
2. **Keep the file**: The `.portable` file must remain in the same directory as the app
3. **Run normally**: Launch the app with `python random_video_picker.py`
4. **Data location**: All settings and recent videos will be saved in `.random_video_picker/` folder

### Making it Truly Portable

To run from a USB drive:
1. Copy the entire application folder to your USB drive
2. Run the portable mode command (or create `.portable` file)
3. Launch the app - it will always use local storage

**Note**: The `.portable` file is just a marker - it tells the app where to save data but doesn't contain any settings itself.

## Documentation

See the [public-docs/](public-docs/) folder:
- [CONTRIBUTING.md](public-docs/CONTRIBUTING.md) - How to contribute to the project
- [AGENTS.md](public-docs/AGENTS.md) - Development commands and architecture
- [PERFORMANCE_GUIDE.md](PERFORMANCE_GUIDE.md) - Performance optimization guide

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and detailed changes.

## Project Structure

```
random-video-picker/
├── random_video_picker.py       # Main GUI application
├── video_scanner.py           # Video discovery and session management
├── video_player.py            # Cross-platform video playback
├── video_preview.py           # Thumbnail and metadata extraction
├── install_deps.py            # Dependency installation script
├── build_executable.py        # Build standalone executables
├── install_shortcuts_simple.py # Simple shortcut creator
├── make_portable.bat         # Windows portable mode script
├── make_portable.sh          # macOS/Linux portable mode script
├── requirements.txt           # Python dependencies
├── setup.py                  # Package installation
├── LICENSE                   # MIT License
├── .gitignore                # Git ignore patterns
├── README.md                 # This file
├── CHANGELOG.md              # Version history
├── LAUNCHER_INSTALLATION.md  # Installation guide
├── public-docs/             # Public documentation
│   ├── CONTRIBUTING.md
│   ├── AGENTS.md
│   ├── UI_DESIGN.md
│   ├── FEATURE_SPEC.md
│   ├── ARCHITECTURE.md
│   └── PERFORMANCE.md
└── private-docs/            # Private documentation (not in repo)
```

## Keyboard Shortcuts

- **Spacebar**: Pick and play a random video
- **Double-click** on recent videos: Replay without affecting progress

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
