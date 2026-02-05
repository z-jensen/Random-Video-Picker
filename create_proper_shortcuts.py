"""
Create proper Windows shortcuts that launch the GUI app without terminal windows.
Uses PowerShell to create .lnk shortcut files.
"""

import os
import sys
import subprocess
from pathlib import Path

def create_shortcut(target_path, shortcut_path, working_dir=None):
    """Create a Windows shortcut using PowerShell"""
    if working_dir is None:
        working_dir = os.path.dirname(target_path)
    
    # Use pythonw.exe for GUI apps (no console window)
    if target_path.endswith('.py'):
        target_exe = sys.executable.replace('python.exe', 'pythonw.exe')
        args = f'"{target_path}"'
    else:
        target_exe = target_path
        args = ""
    
    powershell_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{target_exe}"
$Shortcut.Arguments = "{args}"
$Shortcut.WorkingDirectory = "{working_dir}"
$Shortcut.Save()
'''
    
    try:
        result = subprocess.run(['powershell', '-Command', powershell_script], 
                      capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(shortcut_path):
            print(f"✅ Successfully created: {shortcut_path}")
            return True
        else:
            print(f"❌ Failed to create shortcut: {shortcut_path}")
            print(f"PowerShell output: {result.stdout}")
            print(f"PowerShell errors: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        return False

def main():
    """Create shortcuts for Random Video Picker"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_script = os.path.join(script_dir, "random_video_picker.py")
    
    if not os.path.exists(target_script):
        print(f"❌ Cannot find random_video_picker.py in {script_dir}")
        return 1
    
    # Create desktop shortcut
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    desktop_shortcut = os.path.join(desktop, "Random Video Picker.lnk")
    
    print(f"Looking for Desktop at: {desktop}")
    if not os.path.exists(desktop):
        print(f"⚠️  Desktop folder not found, checking OneDrive...")
        # Try OneDrive Desktop
        desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
        desktop_shortcut = os.path.join(desktop, "Random Video Picker.lnk")
        print(f"Trying OneDrive Desktop at: {desktop}")
        
        if not os.path.exists(desktop):
            print("⚠️  Neither Desktop nor OneDrive Desktop found. Creating in app directory.")
            desktop = os.path.dirname(os.path.abspath(__file__))
            desktop_shortcut = os.path.join(desktop, "Random Video Picker.lnk")
    
    if create_shortcut(target_script, desktop_shortcut):
        print(f"✅ Created desktop shortcut: {desktop_shortcut}")
    
    # Create start menu shortcut
    start_menu = os.path.expanduser("~/AppData/Roaming/Microsoft/Windows/Start Menu/Programs")
    start_menu_shortcut = os.path.join(start_menu, "Random Video Picker.lnk")
    
    os.makedirs(start_menu, exist_ok=True)
    if create_shortcut(target_script, start_menu_shortcut):
        print(f"✅ Created start menu shortcut: {start_menu_shortcut}")
    
    print("\n🚀 Shortcuts created! Double-click the desktop shortcut to launch the app.")
    print("The app will open with no terminal window visible.")
    return 0

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.exit(main())
    else:
        print("This script is for Windows only.")
        sys.exit(1)