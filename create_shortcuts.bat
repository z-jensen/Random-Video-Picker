@echo off
echo Creating shortcuts for Random Video Picker...

REM Get current directory
set "APP_DIR=%~dp0dist"
set "EXE_PATH=%APP_DIR%\RandomVideoPicker.exe"

REM Create desktop shortcut
powershell -Command "$shell = New-Object -ComObject WScript.Shell; $shortcut = $shell.CreateShortcut('%USERPROFILE%\Desktop\Random Video Picker.lnk'); $shortcut.TargetPath = '%EXE_PATH%'; $shortcut.WorkingDirectory = '%APP_DIR%'; $shortcut.Save()"

REM Create start menu shortcut
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Random Video Picker" mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Random Video Picker"
powershell -Command "$shell = New-Object -ComObject WScript.Shell; $shortcut = $shell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Random Video Picker\Random Video Picker.lnk'); $shortcut.TargetPath = '%EXE_PATH%'; $shortcut.WorkingDirectory = '%APP_DIR%'; $shortcut.Save()"

echo Shortcuts created successfully!
echo Desktop: %USERPROFILE%\Desktop\Random Video Picker.lnk
echo Start Menu: %APPDATA%\Microsoft\Windows\Start Menu\Programs\Random Video Picker\Random Video Picker.lnk
pause
