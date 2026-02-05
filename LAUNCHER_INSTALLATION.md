# 🚀 Launcher Installation Guide

This document explains how to create desktop and start menu shortcuts for Random Video Picker across different platforms.

## Quick Setup (Recommended)

### Option 1: Standalone Executable (Best for Distribution)

```bash
# Build standalone executable
python build_executable.py

# Then run the platform-specific shortcut script:
# Windows: .\create_shortcuts.bat
# macOS/Linux: ./create_shortcuts.sh
```

**Note**: If you encounter PATH issues with PyInstaller, the script now uses `python -m PyInstaller` to avoid this problem.

### Option 2: Python Package Installation

```bash
# Install with Python shortcuts
python install_shortcuts.py
```

## Platform-Specific Instructions

### Windows

**Method 1: PyInstaller Executable**
1. Run `python build_executable.py`
2. Run `.\create_shortcuts.bat`
3. Shortcuts created on Desktop and Start Menu

**Method 2: Python Package**
1. Run `python install_shortcuts.py`
2. Shortcuts automatically created

**Manual Method:**
- Create shortcut to `python random_video_picker.py`
- Set working directory to the app folder

### macOS

**Method 1: PyInstaller App Bundle**
1. Run `python build_executable.py`
2. Run `./create_shortcuts.sh`
3. App bundle created in Applications folder
4. Drag to Dock if desired

**Method 2: Python Package**
1. Run `python install_shortcuts.py`
2. App bundle created in Applications folder

**Manual Method:**
- Use Automator to create app that runs the Python script
- Or create shell script with proper shebang

### Linux

**Method 1: PyInstaller Binary**
1. Run `python build_executable.py`
2. Run `./install_linux.sh`
3. .desktop file installed to applications menu

**Method 2: Python Package**
1. Run `python install_shortcuts.py`
2. .desktop file created automatically

**Manual Method:**
Create `~/.local/share/applications/RandomVideoPicker.desktop`:
```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=Random Video Picker
Comment=Randomly select and play videos
Exec=/path/to/python /path/to/random_video_picker.py
Icon=applications-multimedia
Terminal=false
Categories=AudioVideo;Video;Player;
```

## Distribution Options

### For End Users (Recommended)
- Use PyInstaller to create standalone executables
- Include platform-specific installer scripts
- Users don't need Python installed

### For Developers
- Use pip install: `pip install git+https://github.com/your-repo.git`
- Run `python install_shortcuts.py` for shortcuts
- Requires Python environment

## File Structure After Installation

```
Random Video Picker/
├── dist/                          # PyInstaller output
│   └── RandomVideoPicker.exe      # Windows executable
│   └── RandomVideoPicker          # macOS/Linux binary
├── create_shortcuts.bat           # Windows shortcut creator
├── create_shortcuts.sh            # macOS/Linux shortcut creator
├── install_shortcuts.py           # Python package installer
└── build_executable.py            # Build script
```

## Troubleshooting

### Windows
- If shortcuts don't work, check Python path in shortcut target
- Run as administrator if start menu creation fails
- Ensure antivirus doesn't block the executable

### macOS
- If app doesn't launch, check executable permissions: `chmod +x`
- Gatekeeper may block unsigned apps - right-click → Open
- Python script needs proper shebang: `#!/usr/bin/env python3`

### Linux
- Ensure .desktop file has execute permissions: `chmod +x`
- Check that the Python path in Exec= line is correct
- Some desktop environments may require logout/login to see new entries