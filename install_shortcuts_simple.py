#!/usr/bin/env python3
"""
Simple Windows shortcut creator for Random Video Picker.
Creates a batch file launcher that works reliably on all Windows systems.
"""

import os
import sys
import platform
from pathlib import Path

def get_script_directory():
    """Get the directory where this script and the main app are located"""
    return os.path.dirname(os.path.abspath(__file__))

def create_windows_launcher():
    """Create a simple batch file launcher for Windows"""
    
    if platform.system() != "Windows":
        print("❌ This script is designed for Windows only")
        return False
    
    script_dir = get_script_directory()
    target_script = os.path.join(script_dir, "random_video_picker.py")
    
    if not os.path.exists(target_script):
        print(f"❌ Cannot find random_video_picker.py in {script_dir}")
        return False
    
    # Create batch file content
    batch_content = f"""@echo off
cd /d "{script_dir}"
start /MIN pythonw random_video_picker.py
"""
    
    # Try to create on desktop first
    desktop_paths = [
        os.path.join(os.path.expanduser("~"), "Desktop"),
        os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop"),
        script_dir  # Always create in app directory
    ]
    
    created_files = []
    
    for desktop_path in desktop_paths:
        try:
            if os.path.exists(desktop_path) or desktop_path == script_dir:
                batch_file = os.path.join(desktop_path, "Random Video Picker.bat")
                with open(batch_file, "w", encoding="utf-8") as f:
                    f.write(batch_content)
                
                if desktop_path == script_dir:
                    print(f"✅ Created launcher: {batch_file}")
                    print("   Double-click this file to launch Random Video Picker")
                    print("   You can copy this file to your Desktop or Start Menu")
                else:
                    print(f"✅ Created desktop shortcut: {batch_file}")
                
                created_files.append(batch_file)
                
                # Only create one shortcut outside of app directory
                if desktop_path != script_dir:
                    break
                    
        except (OSError, PermissionError) as e:
            print(f"Could not create launcher in {desktop_path}: {e}")
            continue
    
    if created_files:
        print(f"\n🚀 Success! Created {len(created_files)} launcher(s)")
        print("You can now double-click the .bat file(s) to start Random Video Picker")
        return True
    else:
        print("❌ Could not create any launchers")
        return False

def create_linux_launcher():
    """Create .desktop file for Linux"""
    script_dir = get_script_directory()
    python_exe = sys.executable
    target_script = os.path.join(script_dir, "random_video_picker.py")
    
    desktop_entry = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Random Video Picker
Comment=A simple application for randomly selecting and playing videos
Exec={python_exe} "{target_script}"
Icon=applications-multimedia
Terminal=false
Categories=AudioVideo;Video;Player;
Keywords=video;random;player;media;
Path={script_dir}
"""
    
    # Create .desktop file in user's applications directory
    user_apps = os.path.expanduser("~/.local/share/applications")
    os.makedirs(user_apps, exist_ok=True)
    
    desktop_file = os.path.join(user_apps, "RandomVideoPicker.desktop")
    with open(desktop_file, "w", encoding="utf-8") as f:
        f.write(desktop_entry)
    
    os.chmod(desktop_file, 0o755)
    print(f"✅ Created applications menu entry: {desktop_file}")
    
    # Also create on desktop if it exists
    desktop_dir = os.path.expanduser("~/Desktop")
    if os.path.exists(desktop_dir):
        desktop_shortcut = os.path.join(desktop_dir, "RandomVideoPicker.desktop")
        with open(desktop_shortcut, "w", encoding="utf-8") as f:
            f.write(desktop_entry)
        os.chmod(desktop_shortcut, 0o755)
        print(f"✅ Created desktop shortcut: {desktop_shortcut}")

def create_macos_launcher():
    """Create app bundle for macOS"""
    script_dir = get_script_directory()
    python_exe = sys.executable
    target_script = os.path.join(script_dir, "random_video_picker.py")
    
    # Create .app bundle
    app_name = "Random Video Picker.app"
    app_path = os.path.join("/Applications", app_name)
    
    if os.path.exists(app_path):
        print(f"⚠️  App bundle already exists at: {app_path}")
        return True
    
    # Create app bundle structure
    contents_dir = os.path.join(app_path, "Contents")
    macos_dir = os.path.join(contents_dir, "MacOS")
    
    os.makedirs(macos_dir, exist_ok=True)
    
    # Create Info.plist
    info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>randomvideopicker.sh</string>
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
</plist>"""
    
    with open(os.path.join(contents_dir, "Info.plist"), "w", encoding="utf-8") as f:
        f.write(info_plist)
    
    # Create executable script
    launcher_script = f"""#!/bin/bash
cd "{script_dir}"
"{python_exe}" "{target_script}"
"""
    
    launcher_path = os.path.join(macos_dir, "randomvideopicker.sh")
    with open(launcher_path, "w", encoding="utf-8") as f:
        f.write(launcher_script)
    
    os.chmod(launcher_path, 0o755)
    
    print(f"✅ Created app bundle: {app_path}")
    print("   You can now add this to your Dock")
    return True

def main():
    """Main installation function"""
    print("🚀 Creating launcher for Random Video Picker...")
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.executable}")
    print(f"Script Directory: {get_script_directory()}")
    print()
    
    system = platform.system()
    
    if system == "Windows":
        success = create_windows_launcher()
    elif system == "Darwin":  # macOS
        success = create_macos_launcher()
    elif system == "Linux":
        create_linux_launcher()
        success = True
    else:
        print(f"❌ Unsupported platform: {system}")
        return 1
    
    if success:
        print("\n✅ Installation complete!")
        print("You can now launch Random Video Picker using the created launcher.")
        return 0
    else:
        print("\n❌ Installation failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())