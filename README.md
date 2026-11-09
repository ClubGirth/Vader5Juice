# Vader5Juice — shrinking battery bars

## First run
1. Extract the entire ZIP into a permanent folder, such as Documents\Vader5Juice.
2. Install Python 3.12 or 3.13 for Windows from https://www.python.org/downloads/windows/ (include the Python launcher).
3. Plug in the Flydigi 2.4 GHz receiver and wake your Vader 5 Pro in its usual PC/XInput mode. Close Flydigi Space Station, including its background/tray process.
4. Double-click **Setup-and-Run.bat**. It downloads three Python dependencies, then runs the app. Leave its console open during this first test.
5. Find the battery icon in the Windows tray (it may be behind the ^ arrow). Hover for the reported charge; right-click for options.
6. Choose **Indicator → Controller, Dock, or Both**. Default: Controller, 75% brightness, 15-second polling.
7. For subsequent runs, double-click **Run.bat**. Use **Start with Windows** in the tray menu if wanted. Keep this folder in place.

## Shrinking bars and colors
Reported 100%: green; 80%: yellow-green; 60%: yellow; 40%: orange; 20% or 0%: red. Charging: blue. Fully charged: green.

Both the controller and dock now display a shrinking bar: the lit portion follows the reported battery level, and the depleted portion turns off on the controller but glows dim white (RGB 8/8/8) on the dock. The lit portion uses the colors above, including blue while charging. At reported 0%, one red LED stays lit as a low-battery warning. Brightness applies to the colored portion and the dock’s dim white background. Choose **Indicator → Both** to enable both devices.

The controller keeps its existing fill direction. The dock LED order is reversed so LEDs change to dim white from the top down as charge drops, leaving the bottom portion in the battery color.

These are approximate 20% steps, not precise percentages. A fresh reply showing 0% is displayed as 0%; disconnected/time-out states are unknown and never treated as an empty battery. The tray becomes gray when disconnected. Physical lighting can retain its last bar when communication stops; use the tray to confirm connection.

## Dock
Only the USB-addressable **Charging Station 2 Pro**, VID 37D7 / PID 6001, is supported. Other charging docks are not assumed compatible. Connect its USB data cable to your PC, not just a wall charger. The receiver still supplies the controller battery measurement. The dock shows the shrinking battery bar across its 162 addressable LEDs. If dock LED sync is enabled, disable that setting in Flydigi Space Station first, then close Space Station.

## Behavior and limitations
- Uses only the vendor configuration HID collection; does not acquire the controller, remap buttons, switch modes, update firmware, or install drivers.
- Opens one controller/receiver and one compatible dock. Multiple matching devices cause a diagnostic instead of selecting an arbitrary device.
- By default, pauses while process names containing Flydigi or SpaceStation are detected. The status and log now identify the exact matching processes. If you have closed Space Station but a helper keeps triggering this check, uncheck **Pause when Space Station is detected** in the tray menu. This lets you test with the helper running; close the actual configuration app before doing so.
- Reads and validates the controller's LED format before writing. Unsupported formats stay untouched.
- Sends lighting only when battery level/color/brightness changes, or after reconnection. USB reconnect/wake is retried automatically.
- Turning Battery lighting off, switching to Dock only, or choosing Quit attempts to restore the controller LED configuration captured for that connection. A crash, forced shutdown, or disconnect cannot restore it; set your preferred lighting in Space Station if necessary.
- Dock lighting stays at its last bar after exit or switching away; this version cannot back up arbitrary dock animation frames. Restore your dock effect in Space Station.
- Startup is per-user and needs no administrator access. Disable Start with Windows before moving/deleting the folder or replacing the Python version with a built EXE.

## Troubleshooting
Right-click **Open diagnostics folder**. The log and settings live in `%LOCALAPPDATA%\Vader5Juice`. Existing settings in the former `%LOCALAPPDATA%\VaderBattery` folder are copied automatically on first launch after upgrading. The diagnostics action adds the Flydigi HID interface inventory to the log. If battery or lighting fails, share `diagnostics.log` and confirm your dock model. Close Space Station/other RGB controller tools and reconnect the receiver before retrying. Logs may include HID paths/device serials; inspect before sharing publicly.

## Optional single-file EXE
After setup, quit the app and run **Build-EXE.bat** on your Windows PC. It installs PyInstaller and creates `dist\Vader5Juice.exe` with the supplied app logo. Run that EXE without needing the source folder's environment. It is unsigned. No prebuilt Windows EXE is included: this package was prepared on Linux, and PyInstaller Windows builds must run on Windows.

## Validation
Protocol tests verify supplied battery examples, report framing/checksums, configuration versions 2/3, dock pixel payload, shrinking bars at every reported level, and malformed replies. The app has NOT been tested against your physical controller, dock, or Windows HID stack. Treat the first run as a hardware compatibility test; successful writes do not provide visual confirmation. Complete source is included.

## Installing this update
Quit the old tray app before replacing these files. Replace the source files in the same folder, keep `.venv`, and run Run.bat. If you used a built EXE, rebuild with Build-EXE.bat. This update adds shrinking bars to both targets; existing settings remain in place. Choose Indicator → Both if you want both devices active. The process-check bypass remains available.
