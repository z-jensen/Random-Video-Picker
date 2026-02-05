# Contributing to Random Video Picker

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

### Prerequisites
- Python 3.12 or higher
- Git
- A code editor (VS Code recommended)

### Setting Up Your Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/z-jensen/Random-Video-Picker.git
   cd random-video-picker
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install development dependencies**
   ```bash
   pip install black isort flake8 mypy pytest
   ```

5. **Verify installation**
   ```bash
   python3 random_video_picker.py
   ```

## Code Style

We use automated tools to maintain consistent code style:

### Before committing
```bash
# Format code
python3 -m black *.py

# Sort imports
python3 -m isort *.py

# Lint code
python3 -m flake8 *.py

# Type checking
python3 -m mypy *.py
```

### Or run all at once
```bash
python3 -m black *.py && python3 -m isort *.py && python3 -m flake8 *.py && python3 -m mypy *.py
```

## Project Structure

```
random-video-picker/
├── random_video_picker.py    # Main GUI application
├── video_scanner.py          # Video discovery and session management
├── video_player.py           # Cross-platform video playback
├── video_preview.py          # Thumbnail and metadata extraction
├── install_deps.py           # Dependency installation script
├── build_executable.py       # Build standalone executables
├── install_shortcuts.py      # Create desktop/start menu shortcuts
├── setup.py                  # Package configuration
├── requirements.txt          # Dependencies
└── tests/                    # Test files (when implemented)
```

## Making Changes

### Types of Contributions

1. **Bug Fixes**: Report bugs with detailed reproduction steps
2. **New Features**: Open an issue to discuss before implementing
3. **Documentation**: Improvements to README and comments
4. **Performance**: Optimization suggestions and implementations

### Development Workflow

1. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our code style guidelines

3. **Test your changes**:
   ```bash
   python3 random_video_picker.py
   ```

4. **Commit your changes** with descriptive messages:
   ```bash
   git commit -m "Add feature: brief description"
   ```

5. **Push and create a pull request**:
   ```bash
   git push origin feature/your-feature-name
   ```

## Testing

Currently, manual testing is required:

1. Test the application on your platform (Windows/macOS/Linux)
2. Test with various video formats and folder structures
3. Test edge cases (empty folders, corrupted files, etc.)

We plan to add automated tests in the future.

## Guidelines

### Code Style
- Use type hints for all function parameters and return values
- Follow the existing naming conventions (snake_case for functions/variables, PascalCase for classes)
- Add logging for error handling and debugging
- Use pathlib.Path for file operations

### Security
- Validate all file paths to prevent path traversal attacks
- Use subprocess timeouts to prevent hanging
- Never trust external config files without validation

### Performance
- Use threading for blocking operations
- Implement caching for expensive operations
- Keep the UI responsive during background operations

## Submitting Pull Requests

1. **Update documentation** if your changes affect user-facing features
2. **Test thoroughly** on multiple platforms if possible
3. **Ensure all style checks pass**
4. **Provide a clear description** of your changes and why they're needed

## Getting Help

- Check existing issues for similar problems
- Read the private documentation (available to maintainers)
- Ask questions in your pull request description

Thank you for contributing!