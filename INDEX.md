# Vader5Juice

## Run the app

**Want the easiest option?** Download [Vader5Juice.exe](Vader5Juice.exe), save it in a permanent folder on Windows, and double-click it. No Python installation is needed. The EXE is unsigned; only run it if you trust the source.

For running from source, see [README.md](README.md). It covers Python setup, controller/dock compatibility, troubleshooting, and building the EXE yourself.

## Files

- `Vader5Juice.exe` — standalone Windows application.
- `README.md` — setup, usage, compatibility, troubleshooting, and build instructions.
- `app.py` — tray application and HID device handling.
- `protocol.py` — device protocol and battery/LED formatting.
- `test_protocol.py` — protocol tests.
- `requirements.txt` — Python dependencies for running from source.
- `Setup-and-Run.bat` / `Setup-and-Run-Enhanced.bat` — create a Python environment, install dependencies, and launch the source app.
- `Run.bat` — launch the source app after setup.
- `Build-EXE.bat` — build the standalone EXE on Windows.
- `Check-System.bat` — check the Python environment.
- `List-HID-Devices.bat` — enumerate HID devices for troubleshooting.
- `Vader5Juice.spec` — PyInstaller configuration.
- `ControlLab-LICENSE.txt` — MIT license for the attributed ControlLab material.

The application targets Windows 10/11 and requires a Flydigi Vader 5 Pro with its receiver. The optional dock feature supports the USB-addressable Charging Station 2 Pro only. See the README for limitations and details.
