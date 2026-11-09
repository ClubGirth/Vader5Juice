@echo off
REM Vader5Juice First-Time Setup and Run Script (Enhanced for Fresh Windows Installs)
REM This script checks for Python, creates a virtual environment, installs dependencies, and runs the app.

setlocal enabledelayedexpansion
cd /d "%~dp0"

REM Colors and formatting
cls
echo.
echo ======================================================================
echo                    Vader5Juice - Initial Setup
echo ======================================================================
echo.

REM Check if Python launcher is installed
echo [1/4] Checking Python installation...
py -3 --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python launcher not found!
    echo.
    echo This app requires Python 3.12 or 3.13 on a fresh Windows install.
    echo.
    echo SOLUTION:
    echo 1. Go to: https://www.python.org/downloads/windows/
    echo 2. Download Python 3.12.x or 3.13.x
    echo 3. Run the installer and IMPORTANT: Check these boxes:
    echo    - [X] Install launcher for all users
    echo    - [X] Add python.exe to PATH
    echo 4. Complete the installation
    echo 5. Restart this command prompt
    echo 6. Run this script again
    echo.
    echo For detailed instructions, see: WINDOWS_SETUP.md
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('py -3 --version') do set PYTHON_VERSION=%%i
echo [OK] Found %PYTHON_VERSION%
echo.

REM Create virtual environment if it doesn't exist
echo [2/4] Setting up Python environment...
if not exist .venv\Scripts\python.exe (
    echo Creating virtual environment...
    py -3 -m venv .venv
    if errorlevel 1 (
        echo.
        echo ERROR: Could not create Python virtual environment.
        echo.
        echo SOLUTION:
        echo - Ensure you have write permissions in this folder
        echo - Try running Command Prompt as Administrator
        echo - Check that Python installation is complete
        echo.
        pause
        exit /b 1
    )
)

if not exist .venv\Scripts\python.exe (
    echo.
    echo ERROR: Virtual environment creation failed!
    echo.
    pause
    exit /b 1
)
echo [OK] Virtual environment ready
echo.

REM Install dependencies
echo [3/4] Installing dependencies...
echo (hidapi, pystray, Pillow - this may take a minute...)
.venv\Scripts\python.exe -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Dependency installation failed!
    echo.
    echo SOLUTION:
    echo - Check that you have an internet connection
    echo - Ensure pip is up to date:
    echo   .venv\Scripts\python.exe -m pip install --upgrade pip
    echo - See the detailed error message above
    echo.
    pause
    exit /b 1
)
echo [OK] All dependencies installed
echo.

REM Launch the app
echo [4/4] Launching Vader5Juice...
echo.
echo ======================================================================
echo                  Keep this window open during first run
echo              (used for troubleshooting and startup messages)
echo ======================================================================
echo.

.venv\Scripts\python.exe app.py
if errorlevel 1 (
    echo.
    echo ERROR: Application crashed or exited with an error.
    echo.
    echo SOLUTION:
    echo - Check the error message above
    echo - Ensure the FlyDigi receiver is plugged in
    echo - Ensure the Vader 5 controller is powered on and in PC/XInput mode
    echo - Close FlyDigi Space Station before running this app
    echo - Check diagnostics at: %LOCALAPPDATA%\Vader5Juice\diagnostics.log
    echo.
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo Setup complete! For future runs, double-click RUN.BAT
echo ======================================================================
echo.
pause
