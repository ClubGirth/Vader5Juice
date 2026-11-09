@echo off
cd /d "%~dp0"
py -3 --version >nul 2>&1
if errorlevel 1 (
 echo Install Python 3.12 or 3.13 from https://www.python.org/downloads/windows/
 echo Include the Python launcher, then run this file again.
 pause
 exit /b 1
)
if not exist .venv\Scripts\python.exe py -3 -m venv .venv
if not exist .venv\Scripts\python.exe (
 echo Could not create the Python environment.
 pause
 exit /b 1
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
 echo Dependency installation failed. See the message above.
 pause
 exit /b 1
)
.venv\Scripts\python.exe app.py
if errorlevel 1 pause
