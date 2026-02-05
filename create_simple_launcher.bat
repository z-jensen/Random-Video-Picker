@echo off
echo Creating simple launcher for Random Video Picker...

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Create a simple batch file that launches the app
echo @echo off > "%SCRIPT_DIR%Launch Random Video Picker.bat"
echo cd /d "%SCRIPT_DIR%" >> "%SCRIPT_DIR%Launch Random Video Picker.bat"
echo python random_video_picker.py >> "%SCRIPT_DIR%Launch Random Video Picker.bat"
echo pause >> "%SCRIPT_DIR%Launch Random Video Picker.bat"

echo ✅ Created launcher: "%SCRIPT_DIR%Launch Random Video Picker.bat"
echo You can now double-click "Launch Random Video Picker.bat" to start the app
echo.
echo You can also copy this .bat file to your desktop if you want a shortcut there.
pause