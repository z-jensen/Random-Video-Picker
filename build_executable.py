"""
Build standalone executables using PyInstaller for cross-platform distribution.
Creates .exe for Windows, .app for macOS, and binary for Linux.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    """Build standalone executable using PyInstaller"""
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Build for current platform
    print("Building standalone executable...")
    
    # PyInstaller command for GUI application
    cmd = [
        "pyinstaller",
        "--name=RandomVideoPicker",
        "--windowed",  # Hide console for GUI app
        "--onefile",   # Single executable
        "--add-data=README.md:.",  # Include documentation
        "--add-data=LICENSE:.",    # Include license
        "--icon=icon.ico",         # Add icon if available
        "random_video_picker.py"
    ]
    
    # Remove icon option if icon doesn't exist
    if not os.path.exists("icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
    
    try:
        subprocess.check_call(cmd)
        print("✅ Build successful!")
        print(f"Executable created in: {os.path.join('dist', 'RandomVideoPicker')}")
        
        # Create shortcuts script
        create_shortcut_script()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    return True

def create_shortcut_script():
    """Create platform-specific shortcut creation scripts"""
    
    if sys.platform == "win32":
        create_windows_shortcut()
    elif sys.platform == "darwin":
        create_macos_shortcut()
    else:
        create_linux_shortcut()

def create_windows_shortcut():
    """Create Windows batch script for desktop/start menu shortcuts"""
    script = """@echo off
echo Creating shortcuts for Random Video Picker...

REM Get current directory
set "APP_DIR=%~dp0dist"
set "EXE_PATH=%APP_DIR%\\RandomVideoPicker.exe"

REM Create desktop shortcut
powershell "$shell = New-Object -ComObject WScript.Shell; $shortcut = $shell.CreateShortcut('%USERPROFILE%\\Desktop\\Random Video Picker.lnk'); $shortcut.TargetPath = '%EXE_PATH%'; $shortcut.WorkingDirectory = '%APP_DIR%'; $shortcut.Save()"

REM Create start menu shortcut
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Random Video Picker" mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Random Video Picker"
powershell "$shell = New-Object -ComObject WScript.Shell; $shortcut = $shell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Random Video Picker\\Random Video Picker.lnk'); $shortcut.TargetPath = '%EXE_PATH%'; $shortcut.WorkingDirectory = '%APP_DIR%'; $shortcut.Save()"

echo ✅ Shortcuts created successfully!
echo Desktop: %USERPROFILE%\\Desktop\\Random Video Picker.lnk
echo Start Menu: %APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Random Video Picker\\Random Video Picker.lnk
pause
"""
    
    with open("create_shortcuts.bat", "w") as f:
        f.write(script)
    
    os.chmod("create_shortcuts.bat", 0o755)
    print("📝 Created create_shortcuts.bat")

def create_macos_shortcut():
    """Create macOS script for dock/applications folder shortcuts"""
    script = """#!/bin/bash
echo "Creating shortcuts for Random Video Picker..."

# Get current directory
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/dist"
EXE_PATH="$APP_DIR/RandomVideoPicker"

# Create .app bundle
APP_NAME="Random Video Picker.app"
APP_CONTENTS="$APP_NAME/Contents"
APP_MACOS="$APP_CONTENTS/MacOS"
APP_RESOURCES="$APP_CONTENTS/Resources"

mkdir -p "$APP_MACOS" "$APP_RESOURCES"

# Create Info.plist
cat > "$APP_CONTENTS/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>RandomVideoPicker</string>
    <key>CFBundleIdentifier</key>
    <string>com.randomvideopicker.app</string>
    <key>CFBundleName</key>
    <string>Random Video Picker</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Copy executable
cp "$EXE_PATH" "$APP_MACOS/"
chmod +x "$APP_MACOS/RandomVideoPicker"

# Create Applications folder shortcut
if [ -d "/Applications" ]; then
    if [ ! -L "/Applications/Random Video Picker.app" ]; then
        ln -s "$PWD/$APP_NAME" "/Applications/Random Video Picker.app"
        echo "✅ Created Applications folder shortcut"
    fi
fi

echo "✅ App bundle created: $APP_NAME"
echo "You can now drag this app to your Dock"
"""
    
    with open("create_shortcuts.sh", "w") as f:
        f.write(script)
    
    os.chmod("create_shortcuts.sh", 0o755)
    print("📝 Created create_shortcuts.sh")

def create_linux_shortcut():
    """Create Linux .desktop file for application menu"""
    desktop_entry = """[Desktop Entry]
Version=1.0
Type=Application
Name=Random Video Picker
Comment=A simple application for randomly selecting and playing videos
Exec={}/dist/RandomVideoPicker
Icon=applications-multimedia
Terminal=false
Categories=AudioVideo;Video;Player;
Keywords=video;random;player;media;
""".format(os.getcwd())
    
    # Create .desktop file
    with open("RandomVideoPicker.desktop", "w") as f:
        f.write(desktop_entry)
    
    os.chmod("RandomVideoPicker.desktop", 0o755)
    print("📝 Created RandomVideoPicker.desktop")
    
    # Create installation script
    install_script = """#!/bin/bash
echo "Installing Random Video Picker to system..."

APP_DIR="$(pwd)"
DESKTOP_FILE="$APP_DIR/RandomVideoPicker.desktop"

# Install to applications directory
if [ -d "/usr/share/applications" ]; then
    sudo cp "$DESKTOP_FILE" "/usr/share/applications/"
    echo "✅ Installed to system applications menu"
elif [ -d "$HOME/.local/share/applications" ]; then
    cp "$DESKTOP_FILE" "$HOME/.local/share/applications/"
    echo "✅ Installed to user applications menu"
fi

# Create desktop shortcut if desired
read -p "Create desktop shortcut? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cp "$DESKTOP_FILE" "$HOME/Desktop/"
    echo "✅ Desktop shortcut created"
fi

echo "🎉 Installation complete!"
"""
    
    with open("install_linux.sh", "w") as f:
        f.write(install_script)
    
    os.chmod("install_linux.sh", 0o755)
    print("📝 Created install_linux.sh")

if __name__ == "__main__":
    if build_executable():
        print("\n🚀 Build complete! Next steps:")
        print("1. Run the shortcut creation script for your platform")
        print("2. Test the shortcuts")
        print("3. Distribute the executable to users")