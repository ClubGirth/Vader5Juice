@echo off
REM Vader5Juice - HID Device Enumeration Tool
REM Shows all connected HID devices to help diagnose controller/dock detection issues

setlocal enabledelayedexpansion
cd /d "%~dp0"
cls

echo.
echo ======================================================================
echo            Vader5Juice - HID Device Enumeration
echo ======================================================================
echo.
echo This tool shows all HID devices connected to your system.
echo Look for FlyDigi devices with these IDs:
echo   - Controller/Receiver: VID_37D7 PID_2401
echo   - Dock (Charging Station 2 Pro): VID_37D7 PID_6001
echo.

REM Check if Python is available
py -3 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please run Setup-and-Run.bat first to install Python.
    echo.
    pause
    exit /b 1
)

REM Check if hidapi is installed
py -3 -c "import hid" >nul 2>&1
if errorlevel 1 (
    echo ERROR: hidapi not installed!
    echo Please run Setup-and-Run.bat first.
    echo.
    pause
    exit /b 1
)

REM Run the Python enumeration script
py -3 - %*  << 'PYTHON_EOF'
import sys
import hid

print("Enumerating HID devices...")
print()

devices = hid.enumerate()
if not devices:
    print("No HID devices found!")
    sys.exit(0)

flydigi_found = False
for i, device in enumerate(devices):
    vendor_id = device.get('vendor_id', 0)
    product_id = device.get('product_id', 0)
    manufacturer = device.get('manufacturer_string', 'Unknown')
    product = device.get('product_string', 'Unknown')
    path = device.get('path', 'Unknown')
    
    # Check if this is a FlyDigi device
    is_flydigi = vendor_id == 0x37D7
    if is_flydigi:
        flydigi_found = True
    
    # Format output
    marker = "[FLYDIGI]" if is_flydigi else "[other]  "
    print(f"{marker} Device #{i}")
    print(f"    Vendor ID:     0x{vendor_id:04x} ({vendor_id})")
    print(f"    Product ID:    0x{product_id:04x} ({product_id})")
    print(f"    Manufacturer:  {manufacturer}")
    print(f"    Product Name:  {product}")
    print(f"    Path:          {path}")
    
    # Identify FlyDigi devices
    if is_flydigi:
        if product_id == 0x2401:
            print(f"    ✓ CONTROLLER/RECEIVER DETECTED")
        elif product_id == 0x6001:
            print(f"    ✓ DOCK (CHARGING STATION 2 PRO) DETECTED")
        else:
            print(f"    ? Unknown FlyDigi device")
    
    print()

if flydigi_found:
    print("="*70)
    print("✓ FlyDigi device(s) found! Your hardware should be detectable.")
    print("="*70)
else:
    print("="*70)
    print("⚠ No FlyDigi devices found!")
    print("="*70)
    print()
    print("TROUBLESHOOTING:")
    print("1. Ensure the receiver is plugged into a USB port (not a hub)")
    print("2. Ensure the Vader 5 controller is powered on and awake")
    print("3. Press the connect button on both receiver and controller")
    print("4. Try a different USB port")
    print("5. Unplug and re-plug the receiver")
    print("6. Check Device Manager for unknown devices (may need drivers)")
    print()

PYTHON_EOF

echo.
pause
