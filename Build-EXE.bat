@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
 echo Run Setup-and-Run.bat first, then quit the tray app.
 pause
 exit /b 1
)
.venv\Scripts\python.exe -m pip install pyinstaller==6.16.0
if errorlevel 1 goto failed
.venv\Scripts\python.exe -c "from PIL import Image; Image.open('applogo.png').save('applogo.ico', format='ICO', sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])"
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --distpath . --name Vader5Juice --icon applogo.ico --collect-all hid --hidden-import pystray._win32 app.py
if errorlevel 1 goto failed
echo EXE created in the project folder: Vader5Juice.exe
pause
exit /b 0
:failed
echo Build failed. See the message above.
pause
exit /b 1
