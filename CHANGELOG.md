# Changelog

All notable changes to the Random Video Picker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-02-05

### Added
- **Standalone executable distribution**: Build with PyInstaller for fast startup
- **Optimized executables**: Changed from --onefile to --onedir for much faster launch
- **Simple shortcut creation**: Streamlined `install_shortcuts_simple.py` for basic desktop shortcuts
- **Cross-platform builds**: Works on Windows, macOS, and Linux without Python

### Improved
- **Faster executable startup**: Optimized PyInstaller flags for better performance
- **Simplified installation**: Streamlined options and removed complex dependency chains
- **Cleaner documentation**: Focused on what actually matters to users

### Documentation
- Updated README.md with simplified installation options
- Added AGENTS.md with development commands and architecture details

## [1.1.0] - 2026-02-04

### Security
- **CRITICAL**: Fixed path traversal vulnerability in state file loading
  - Added `_validate_path()` method to VideoScanner to validate all loaded paths
  - Paths are now checked to ensure they're within the expected base directory
  - Malicious state files with `..` sequences are now rejected
  - Invalid paths are logged and skipped rather than causing crashes
- Added input validation for folder selection
  - Verifies folder exists before scanning
  - Verifies path is actually a directory
  - Tests read permissions before attempting scan
  - Shows user-friendly error messages for each failure case

### Fixed
- **CRITICAL**: Fixed silent exception swallowing throughout codebase
  - Replaced all `except Exception: pass` patterns with proper logging
  - video_scanner.py: save_state(), load_state(), clear_saved_state() now log errors
  - video_preview.py: All cleanup and generation functions log warnings/errors
  - Added `logger = logging.getLogger(__name__)` to all modules
- Fixed race condition in VideoPreview cache size management
  - Cache eviction (removing old entries) now happens inside the lock
  - Prevents race condition between size check and key removal
  - Added MAX_CACHE_SIZE and CACHE_EVICTION_COUNT constants
- Fixed thread safety issues in preview generation
  - Each background thread now creates its own VideoPreview instance
  - Prevents concurrent access to shared cache from multiple threads
  - Added request ID tracking to prevent stale UI updates
  - Old preview requests are now invalidated when new preview is triggered
- Fixed closure bug in preview callbacks
  - Lambda functions in callbacks could show wrong video if user clicked rapidly
  - Now uses request IDs to ensure only current preview updates UI
- Fixed bare exception handlers throughout codebase
  - Specific exception types now caught (OSError, PermissionError, ValueError, etc.)
  - Better error messages for users
  - Proper logging of all error conditions
- Removed redundant `hasattr()` checks
  - All attributes now initialized in `__init__` with proper typing
  - `current_preview_video` now typed as `Optional[Path]` and initialized to None
  - Cleaner code without defensive hasattr checks

### Changed
- Added subprocess timeouts to prevent hanging operations
  - Video player launch: 30 seconds
  - ffmpeg version check: 1 second
  - ffprobe metadata: 2 seconds
  - thumbnail generation: 3 seconds
- Moved all imports to module level (following best practices)
  - Removed redundant local imports of `time` in multiple methods
  - VideoPreview now imported at module level in random_video_picker.py
  - datetime imported at top level in video_preview.py
- Converted magic numbers to module-level constants
  - PICK_DEBOUNCE_MS = 500 (spacebar debounce)
  - MAX_CACHE_SIZE = 50 (cache limit)
  - CACHE_EVICTION_COUNT = 25 (how many to remove when limit reached)
  - THUMBNAIL_MAX_AGE_SECONDS = 86400 (24 hours)
  - Various subprocess timeouts
- Added `takefocus=0` to all buttons
  - Prevents buttons from receiving keyboard focus
  - Spacebar now only triggers video picker, not button activation
  - Fixed issue where spacebar would toggle More/Less button

### Documentation
- Updated AGENTS.md with new security and threading guidelines
- Updated ARCHITECTURE.md with thread safety patterns
- Added detailed error handling patterns
- Documented request ID tracking for async operations
- Added security testing examples

## [1.0.0] - Initial Release

### Features
- Simple core functionality: Choose folder, pick random video
- Session management: Track played videos to avoid repeats
- Optimized video preview: Background thumbnails and detailed information
- Cross-platform compatibility: Works on Windows, macOS, Linux
- Keyboard shortcuts: Spacebar plays random video
- Smart UI layout: Progressive disclosure with advanced features
- Interactive recent videos: Double-click to replay
- Background scanning: Folder scanning runs in background thread
- Fast thumbnails: Fixed 20-second seek for quick preview generation
- Portable mode: Run from USB drives without installation
- Modern UI design: Enhanced color scheme and styling
- Status indicators: Real-time status with colored dots
- Responsive layout: Optimized for small windows
- Touchpad support: Momentum detection and smooth scrolling
