# Vader5Juice - Complete File Index

This folder contains everything you need to run Vader5Juice on Windows. Here's what each file does:

## 📖 START HERE - Documentation

### 🚀 For First-Time Setup
- **[SETUP-README.md](SETUP-README.md)** ← **START HERE!**
  - Overview of entire setup process
  - Quick start guide for impatient users
  - Links to all relevant guides
  
### ⚡ For Quick Reference
- **[QUICK_START.md](QUICK_START.md)**
  - 3-step TL;DR setup
  - Common Q&A
  - Troubleshooting table
  - Best if you know what you're doing

### 📋 For Detailed Instructions
- **[WINDOWS_SETUP.md](WINDOWS_SETUP.md)**
  - Step-by-step installation guide
  - Detailed troubleshooting for each problem
  - Configuration options explained
  - Settings reference

### 📚 For Complete Information
- **[README.md](README.md)**
  - Original comprehensive documentation
  - Battery color reference
  - Technical details and limitations
  - Advanced configuration

---

## 🔧 Batch Files (Double-Click to Run)

### First-Time Setup (Choose One)
- **[Setup-and-Run.bat](Setup-and-Run.bat)** (Original)
  - Creates Python environment
  - Installs dependencies
  - Launches the app
  - Standard error messages

- **[Setup-and-Run-Enhanced.bat](Setup-and-Run-Enhanced.bat)** (Recommended)
  - Same as above but with better error messages
  - Detailed troubleshooting suggestions
  - Clearer formatting
  - **Use this if you're on a fresh Windows install**

### Running the App
- **[Run.bat](Run.bat)**
  - For all runs after initial setup
  - Launches app without console window
  - Just double-click and go

### System Diagnostics
- **[Check-System.bat](Check-System.bat)**
  - Verifies Python is installed correctly
  - Checks virtual environment
  - Confirms dependencies
  - Lists all source files
  - Run this before troubleshooting

### HID Device Detection
- **[List-HID-Devices.bat](List-HID-Devices.bat)**
  - Shows all USB HID devices
  - Highlights FlyDigi devices
  - Useful for troubleshooting connection issues
  - Requires Python to be set up first

### Build Standalone EXE (Optional)
- **[Build-EXE.bat](Build-EXE.bat)**
  - Creates a standalone `.exe` that doesn't need this folder
  - Run after successful first setup
  - Creates `dist\Vader5Juice.exe` with the supplied app logo

---

## 💻 Python Source Code

- **[app.py](app.py)**
  - Main application
  - Handles UI, tray icon, configuration
  - Monitors battery and controls LEDs

- **[protocol.py](protocol.py)**
  - FlyDigi Vader 5 protocol implementation
  - Packet formatting and battery decoding
  - LED color and animation logic
  - Based on ControlLab (MIT licensed)

- **[test_protocol.py](test_protocol.py)**
  - Unit tests for protocol.py
  - Tests battery parsing, colors, animations
  - Validates packet formatting

- **[requirements.txt](requirements.txt)**
  - List of Python dependencies:
    - `hidapi==0.14.0.post4` - HID device communication
    - `pystray==0.19.5` - System tray integration
    - `Pillow==11.3.0` - Image handling for tray icon

---

## 📄 License & Attribution

- **[README.md](README.md)**
  - Project documentation and features

- **[ControlLab-LICENSE.txt](ControlLab-LICENSE.txt)**
  - MIT License for ControlLab (protocol inspiration)

- **[THIRD_PARTY.txt](THIRD_PARTY.txt)**
  - Credits and licenses for all dependencies

---

## 🗂️ Hidden Folders (After First Run)

After running the app, these folders will be created:

### `.venv/` (Virtual Environment)
- Do NOT delete or move this folder
- Contains isolated Python environment for Vader5Juice
- Keep it in place for future runs

### `%LOCALAPPDATA%\Vader5Juice/` (Settings & Logs)
Location: `C:\Users\YourUsername\AppData\Local\Vader5Juice\`

Contains:
- **`settings.json`** - Your saved preferences (Indicator, Brightness, etc.)
- **`diagnostics.log`** - Detailed activity log (useful for troubleshooting)

Access from app: Right-click tray icon → **Open diagnostics folder**

---

## 🎯 Quick Navigation Guide

**I'm starting from scratch:**
→ Read [SETUP-README.md](SETUP-README.md) → Run [Setup-and-Run-Enhanced.bat](Setup-and-Run-Enhanced.bat)

**I just want to run the app again:**
→ Double-click [Run.bat](Run.bat)

**I need detailed setup help:**
→ Read [WINDOWS_SETUP.md](WINDOWS_SETUP.md)

**I'm having problems:**
→ Run [Check-System.bat](Check-System.bat) → Check [QUICK_START.md](QUICK_START.md) → Review `diagnostics.log`

**I can't find my controller/dock:**
→ Run [List-HID-Devices.bat](List-HID-Devices.bat)

**I want a standalone .exe:**
→ First run [Run.bat](Run.bat) successfully → Then run [Build-EXE.bat](Build-EXE.bat)

**I want technical details:**
→ Read [README.md](README.md)

---

## 📊 Setup Checklist

Before you start, ensure you have:

- ✅ Windows 10/11
- ✅ Python 3.12 or 3.13 from https://www.python.org/downloads/windows/
  - (With "Install launcher for all users" and "Add python.exe to PATH" checked)
- ✅ FlyDigi Vader 5 Pro controller
- ✅ 2.4 GHz USB receiver
- ✅ FlyDigi Space Station closed completely
- ✅ Receiver plugged in and controller powered on

---

## 🚀 Get Started Now!

**New user?** Start here:
```
Read: SETUP-README.md
Then: Double-click Setup-and-Run-Enhanced.bat
```

**Returning user?** Just:
```
Double-click Run.bat
```

---

## 📞 Troubleshooting Flowchart

```
Error during setup?
├─ Python not found? → Install Python 3.12/3.13 with launcher
├─ Can't create venv? → Run as regular user (not admin), try different folder
└─ Dependencies fail? → Check internet connection, run Check-System.bat

App runs but no controller?
├─ App starts but no battery shown? → Run List-HID-Devices.bat
├─ No devices in list? → Plug in receiver, power on controller
├─ Space Station running? → Close Space Station, close helpers
└─ Still stuck? → Check diagnostics.log, look for ERROR

App finds controller but no dock?
├─ Using data cable (not just power)? → Ensure USB data connection
├─ Dock LED Sync disabled? → Disable in Space Station, close app, restart
├─ Right dock model? → Must be "Charging Station 2 Pro"
└─ Still stuck? → Run List-HID-Devices.bat, check for PID_6001
```

---

## ℹ️ File Organization

```
Vader5Juice/
├── README.md                          ← Original documentation
├── SETUP-README.md                    ← Setup overview (START HERE!)
├── QUICK_START.md                     ← Quick reference
├── WINDOWS_SETUP.md                   ← Detailed setup guide
├── Setup-and-Run.bat                  ← Initial setup (original)
├── Setup-and-Run-Enhanced.bat         ← Initial setup (recommended)
├── Run.bat                            ← Run app after setup
├── Check-System.bat                   ← System verification
├── List-HID-Devices.bat               ← HID device enumeration
├── Build-EXE.bat                      ← Create standalone .exe
├── app.py                             ← Main application
├── protocol.py                        ← FlyDigi protocol
├── test_protocol.py                   ← Protocol tests
├── requirements.txt                   ← Python dependencies
├── ControlLab-LICENSE.txt             ← License for protocol
├── THIRD_PARTY.txt                    ← Third-party credits
└── .venv/                             ← Python environment (created after setup)
```

---

**Questions? Check [SETUP-README.md](SETUP-README.md) or [WINDOWS_SETUP.md](WINDOWS_SETUP.md)!**
