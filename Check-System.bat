@echo off
REM Vader5Juice - Diagnostic/Verification Script
REM Use this to check if your system is properly set up for running Vader5Juice

setlocal enabledelayedexpansion
cls

echo.
echo ======================================================================
echo                Vader5Juice - System Diagnostics
echo ======================================================================
echo.

REM Check Python
echo [CHECK 1] Python Installation
py -3 --version >nul 2>&1
if errorlevel 1 (
    echo Status: ❌ FAILED
    echo Python launcher not found. Install Python 3.12+ from python.org
) else (
    for /f "tokens=*" %%i in ('py -3 --version') do echo Status: ✓ PASSED - %%i
)
echo.

REM Check Virtual Environment
echo [CHECK 2] Virtual Environment
if exist .venv\Scripts\python.exe (
    for /f "tokens=*" %%i in ('.venv\Scripts\python.exe --version') do echo Status: ✓ PASSED - %%i (in .venv)
) else (
    echo Status: ❌ NOT CREATED
    echo Run Setup-and-Run.bat to create it
)
echo.

REM Check Dependencies
echo [CHECK 3] Required Dependencies
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe -m pip list 2>nul | findstr /I "hidapi pystray pillow" >nul
    if errorlevel 1 (
        echo Status: ❌ MISSING
        echo Run Setup-and-Run.bat to install dependencies
    ) else (
        echo Status: ✓ PASSED
        .venv\Scripts\python.exe -m pip list 2>nul | findstr /I "hidapi pystray pillow"
    )
) else (
    echo Status: ⚠ CANNOT CHECK (Virtual environment not created)
)
echo.

REM Check Source Files
echo [CHECK 4] Source Files
set files_ok=1
for %%F in (app.py protocol.py requirements.txt) do (
    if exist %%F (
        echo   ✓ %%F
    ) else (
        echo   ❌ %%F NOT FOUND
        set files_ok=0
    )
)
if !files_ok! equ 1 (
    echo Status: ✓ PASSED
) else (
    echo Status: ❌ MISSING FILES
)
echo.

REM Check Batch Scripts
echo [CHECK 5] Launch Scripts
for %%B in (Setup-and-Run.bat Run.bat) do (
    if exist %%B (
        echo   ✓ %%B
    ) else (
        echo   ❌ %%B NOT FOUND
    )
)
echo.

REM Check Local AppData Folder
echo [CHECK 6] Settings/Logs Folder
set appdata_path=%LOCALAPPDATA%\Vader5Juice
if exist "%appdata_path%" (
    echo Status: ✓ PASSED
    echo Location: %appdata_path%
    if exist "%appdata_path%\settings.json" (
        echo   - settings.json found
    )
    if exist "%appdata_path%\diagnostics.log" (
        echo   - diagnostics.log found
    )
) else (
    echo Status: ⚠ NOT YET CREATED (will be created on first run)
)
echo.

REM Summary
echo ======================================================================
echo                           SUMMARY
echo ======================================================================
echo.
echo If all checks passed, you're ready to run Vader5Juice!
echo.
echo NEXT STEPS:
echo 1. Close FlyDigi Space Station
echo 2. Plug in the receiver and wake your Vader 5
echo 3. Double-click: Setup-and-Run.bat
echo.
echo For help, see: QUICK_START.md or WINDOWS_SETUP.md
echo.
pause
