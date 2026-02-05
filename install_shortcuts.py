#!/usr/bin/env python3
"""
Cross-platform installation script for Random Video Picker.
Creates desktop/start menu shortcuts for the Python application.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def get_python_executable():
    """Get the Python executable path"""
    return sys.executable

def get_script_directory():
    """Get the directory where this script and the main app are located"""
    return os.path.dirname(os.path.abspath(__file__))

def create_windows_shortcuts():
    """Create Windows desktop and start menu shortcuts"""
    try:
        import winshell
        from win32com.client import Dispatch
    except ImportError:
        print("Installing required packages for Windows shortcuts...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "winshell pywin32"])
        import winshell
        from win32com.client import Dispatch
    
    python_exe = get_python_executable()
    script_dir = get_script_directory()
    target_script = os.path.join(script_dir, "random_video_picker.py")
    
    # Create desktop shortcut
    desktop = winshell.desktop()
    path = os.path.join(desktop, "Random Video Picker.lnk")
    target = python_exe
    wDir = script_dir
    icon = target_script
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.Arguments = f'"{target_script}"'
    shortcut.WorkingDirectory = wDir
    shortcut.IconLocation = icon
    shortcut.save()
    
    # Create start menu shortcut
    start_menu = winshell.start_menu()
    programs = os.path.join(start_menu, "Programs")
    
    # Create app folder in start menu
    app_folder = os.path.join(programs, "Random Video Picker")
    os.makedirs(app_folder, exist_ok=True)
    
    start_path = os.path.join(app_folder, "Random Video Picker.lnk")
    shortcut = shell.CreateShortCut(start_path)
    shortcut.Targetpath = target
    shortcut.Arguments = f'"{target_script}"'
    shortcut.WorkingDirectory = wDir
    shortcut.IconLocation = icon
    shortcut.save()
    
    print(f"✅ Windows shortcuts created:")
    print(f"   Desktop: {path}")
    print(f"   Start Menu: {start_path}")

def create_macos_shortcuts():
    """Create macOS Applications folder shortcut and dock option"""
    script_dir = get_script_directory()
    python_exe = get_python_executable()
    target_script = os.path.join(script_dir, "random_video_picker.py")
    
    # Create .app bundle
    app_name = "Random Video Picker.app"
    app_path = os.path.join("/Applications", app_name)
    
    if not os.path.exists(app_path):
        # Create app bundle structure
        contents_dir = os.path.join(app_path, "Contents")
        macos_dir = os.path.join(contents_dir, "MacOS")
        resources_dir = os.path.join(contents_dir, "Resources")
        
        os.makedirs(macos_dir, exist_ok=True)
        os.makedirs(resources_dir, exist_ok=True)
        
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
        
        print(f"✅ macOS app bundle created: {app_path}")
        print("   You can now add this to your Dock")
    else:
        print(f"⚠️  App bundle already exists at: {app_path}")

def create_linux_shortcuts():
    """Create Linux .desktop file for application menu"""
    script_dir = get_script_directory()
    python_exe = get_python_executable()
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
    
    # Create desktop shortcut
    desktop_dir = os.path.expanduser("~/Desktop")
    if os.path.exists(desktop_dir):
        desktop_shortcut = os.path.join(desktop_dir, "RandomVideoPicker.desktop")
        with open(desktop_shortcut, "w", encoding="utf-8") as f:
            f.write(desktop_entry)
        os.chmod(desktop_shortcut, 0o755)
        print(f"✅ Linux shortcuts created:")
        print(f"   Applications Menu: {desktop_file}")
        print(f"   Desktop: {desktop_shortcut}")
    else:
        print(f"✅ Linux applications menu shortcut created: {desktop_file}")

def main():
    """Main installation function"""
    print("🚀 Creating shortcuts for Random Video Picker...")
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.executable}")
    print(f"Script Directory: {get_script_directory()}")
    print()
    
    system = platform.system()
    
    if system == "Windows":
        create_windows_shortcuts()
    elif system == "Darwin":  # macOS
        create_macos_shortcuts()
    elif system == "Linux":
        create_linux_shortcuts()
    else:
        print(f"❌ Unsupported platform: {system}")
        return 1
    
    print("\n✅ Installation complete!")
    print("You can now launch Random Video Picker from your desktop or applications menu.")
    return 0

if __name__ == "__main__":
    sys.exit(main())