# 🤖 AGENTS.md

This file contains instructions for AI agents and developers working on the Random Video Picker project.

## Development Commands

### Installation & Setup
```bash
# Clone the repository
git clone https://github.com/z-jensen/Random-Video-Picker.git
cd random-video-picker

# Install dependencies
pip install -r requirements.txt

# Run the application
python random_video_picker.py

# Create desktop/start menu shortcuts
python install_shortcuts.py
```

### Building Executables
```bash
# Build standalone executables for distribution
python build_executable.py

# After building, create platform-specific shortcuts:
# Windows: .\create_shortcuts.bat
# macOS/Linux: ./create_shortcuts.sh
```

### Testing
```bash
# Run basic functionality test
python -m pytest tests/  # If tests exist

# Manual testing checklist:
# 1. Application launches without errors
# 2. Can select video folder
# 3. Can pick and play random video
# 4. Thumbnails generate correctly
# 5. Recent videos list works
# 6. Portable mode functions properly
```

### Code Quality
```bash
# Check code style (if configured)
flake8 *.py
black *.py

# Type checking (if configured)
mypy *.py
```

## Project Architecture

### Core Components
- **random_video_picker.py**: Main GUI application using Tkinter
- **video_scanner.py**: Video discovery and session management
- **video_player.py**: Cross-platform video playback functionality
- **video_preview.py**: Thumbnail generation and metadata extraction
- **install_deps.py**: Dependency installation helper

### Build & Distribution Components
- **build_executable.py**: PyInstaller-based executable builder
- **install_shortcuts.py**: Cross-platform shortcut creator
- **setup.py**: Python package setup configuration

### Configuration Files
- **requirements.txt**: Python dependencies
- **make_portable.bat/.sh**: Portable mode scripts
- **LAUNCHER_INSTALLATION.md**: Installation documentation

## Development Guidelines

### Code Style
- Use Python 3.9+ features
- Follow PEP 8 style guidelines
- Add type hints where beneficial
- Include docstrings for new functions

### Platform Support
- Ensure cross-platform compatibility (Windows, macOS, Linux)
- Test on all target platforms when possible
- Use platform-specific code only when necessary
- Handle path separators and file system differences

### GUI Development
- Use Tkinter for the main interface
- Ensure responsive UI with background processing
- Implement keyboard shortcuts
- Provide visual feedback for user actions

### Video Processing
- Handle various video formats and codecs
- Implement graceful fallbacks when ffmpeg unavailable
- Optimize thumbnail generation for performance
- Manage large video libraries efficiently

## Testing Strategy

### Manual Testing Checklist
1. **Basic Functionality**
   - [ ] Application launches without errors
   - [ ] Can select video directory
   - [ ] Random video selection works
   - [ ] Video playback functions

2. **User Interface**
   - [ ] All buttons and controls work
   - [ ] Keyboard shortcuts function
   - [ ] Window resizing works properly
   - [ ] Error messages are user-friendly

3. **Advanced Features**
   - [ ] Thumbnail generation works
   - [ ] Recent videos list updates
   - [ ] Session management persists
   - [ ] Portable mode functions

4. **Platform-Specific**
   - [ ] Shortcuts install correctly on Windows
   - [ ] App bundle works on macOS
   - [ ] .desktop file works on Linux
   - [ ] Executable builds run standalone

## Deployment Process

### For Development
1. Make code changes
2. Test manually using checklist above
3. Update documentation as needed
4. Commit changes with descriptive messages

### For Release
1. Update version numbers in setup.py
2. Run `python build_executable.py` to create distributables
3. Test executables on all target platforms
4. Update CHANGELOG.md with version notes
5. Create GitHub release with executables

## Common Issues & Solutions

### PyInstaller Issues
- If build fails, check for missing data files
- Include all necessary modules in --hidden-import
- Test with --onedir before --onefile for debugging

### Platform-Specific Issues
- **Windows**: Check for DLL dependencies
- **macOS**: Handle code signing and Gatekeeper
- **Linux**: Verify library dependencies and desktop entry format

### Video Processing Issues
- Ensure ffmpeg is available for thumbnails
- Handle corrupt video files gracefully
- Implement timeout for long-running operations

## Documentation Updates

When making changes:
1. Update README.md if user-facing
2. Update relevant docs in public-docs/
3. Update CHANGELOG.md for release notes
4. Update this AGENTS.md for developer changes

## Git Workflow

### Branch Strategy
- `main`: Stable, release-ready code
- `develop`: Integration branch for features
- `feature/*`: Individual feature branches

### Commit Messages
- Use present tense: "Add feature" not "Added feature"
- Be specific about what was changed
- Reference issue numbers when applicable

### Before Pushing
1. Run all tests
2. Check code style
3. Verify documentation is updated
4. Ensure no sensitive data is committed