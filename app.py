import csv
import io
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time
import hid
import pystray
from PIL import Image, ImageDraw
from protocol import *

APP_NAME = 'Vader5Juice'
LEGACY_APP_NAME = 'VaderBattery'
DATA_ROOT = Path(os.environ.get('LOCALAPPDATA', str(Path.home())))
ROOT = DATA_ROOT / APP_NAME
LEGACY_ROOT = DATA_ROOT / LEGACY_APP_NAME
ROOT.mkdir(parents=True, exist_ok=True)
for filename in ('settings.json', 'diagnostics.log'):
    legacy_file = LEGACY_ROOT / filename
    app_file = ROOT / filename
    if legacy_file.is_file() and not app_file.exists():
        shutil.copy2(legacy_file, app_file)
handler = RotatingFileHandler(ROOT/'diagnostics.log', maxBytes=500000, backupCount=2)
logging.basicConfig(handlers=[handler], level=logging.INFO, format='%(asctime)s %(message)s')
DEFAULT = dict(target='Controller', brightness=75, interval=15, enabled=True, check_conflicts=True)
try:
    settings = DEFAULT | json.loads((ROOT/'settings.json').read_text())
except (OSError, ValueError):
    settings = DEFAULT.copy()
if settings['target'] not in ('Controller','Dock','Both'):
    settings['target'] = 'Controller'
if settings['brightness'] not in (25,50,75,100):
    settings['brightness'] = 75
if settings['interval'] not in (10,15,30,60):
    settings['interval'] = 15
stop, wake = threading.Event(), threading.Event()
status = 'Waiting for controller'
ctrl = dock = None
original = None
last_ctrl = last_dock = None
worker_thread = None


def save():
    (ROOT/'settings.json').write_text(json.dumps(settings, indent=2))
    wake.set()


def processes_conflict():
    result = subprocess.run(['tasklist','/FO','CSV','/NH'], capture_output=True,
                            text=True, timeout=5, creationflags=0x08000000)
    if result.returncode:
        raise RuntimeError('Unable to check configuration-app conflicts')
    matches = []
    for row in csv.reader(io.StringIO(result.stdout)):
        if row and any(s in row[0].lower() for s in ('flydigi','spacestation','space station')):
            matches.append(row[0])
    return sorted(set(matches))


def discover(pid):
    devices = [d for d in hid.enumerate(VID,pid) if d.get('usage_page') == PAGE and d.get('usage') == 1]
    paths = {d['path'] for d in devices}
    if len(paths) > 1:
        raise RuntimeError('Multiple matching devices; connect only one controller/receiver and one dock')
    if not paths:
        return None
    device = hid.device()
    device.open_path(next(iter(paths)))
    return device


def send(device, report):
    # HIDAPI on Windows requires a leading zero for an unnumbered output report.
    output = b'\0' + report
    written = device.write(output)
    if written != len(output):
        raise OSError(f'Short HID write: {written}/{len(output)}')


def drain(device):
    device.set_nonblocking(True)
    try:
        for _ in range(200):
            if not device.read(65):
                break
    finally:
        device.set_nonblocking(False)


def read_battery(device):
    drain(device)
    send(device, packet([1,2]))
    deadline = time.monotonic()+2
    while time.monotonic() < deadline and not stop.is_set():
        reply = device.read(65,100)
        if reply:
            parsed = battery(reply)
            if parsed is not None:
                logging.info('Battery %s; info %s', parsed, bytes(reply).hex())
                return parsed
    raise TimeoutError('No fresh battery response; wake controller and close Space Station')


def read_config(device):
    drain(device)
    send(device, packet([0xa7,4,0,20]))
    chunks = {}
    total = None
    deadline = time.monotonic()+4
    while time.monotonic() < deadline and not stop.is_set():
        c = config_chunk(device.read(65,100))
        if c:
            n,i,data = c
            if total is not None and total != n:
                raise ValueError('Inconsistent lighting reply')
            total = n
            chunks[i] = data
            if len(chunks) == n:
                config = b''.join(chunks[i] for i in range(n))
                # Validate before retaining a configuration for later writes.
                controller_packets(config, (0,255,0))
                logging.info('Read controller lighting version=%s LEDs=%s',config[1],config[7])
                return config
    raise TimeoutError('Battery readable, but controller LED configuration did not respond')


def write_sequence(device, packets, delay):
    for p in packets:
        send(device,p)
        time.sleep(delay)


def close_devices(restore=False):
    global ctrl,dock,original,last_ctrl,last_dock
    if ctrl and restore and original:
        try:
            write_sequence(ctrl, config_packets(original), .025)
        except Exception:
            logging.exception('Controller lighting restore failed')
    for device in (ctrl,dock):
        if device:
            try:
                device.close()
            except Exception:
                pass
    ctrl = dock = original = last_ctrl = last_dock = None


def badge(rgb=(120,120,120), percent=None):
    im = Image.new('RGB',(64,64),(20,24,30))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((5,15,55,49),radius=5,outline=rgb,width=4)
    d.rectangle((55,25,60,39),fill=rgb)
    if percent is not None:
        d.rectangle((10,20,10+max(1,int(40*percent/100)),44),fill=rgb)
    return im


def update(text, rgb=(120,120,120), percent=None):
    global status
    status = text
    icon.title = (APP_NAME+': '+text)[:127]
    icon.icon = badge(rgb,percent)
    icon.update_menu()


def worker():
    global ctrl,dock,original,last_ctrl,last_dock
    try:
        while not stop.is_set():
            delay = settings['interval']
            try:
                conflicts = processes_conflict() if settings['enabled'] and settings['check_conflicts'] else []
                if not settings['enabled']:
                    close_devices(restore=True)
                    update('Paused')
                elif conflicts:
                    # Do not send restore commands while another configuration app is active.
                    close_devices()
                    logging.info('Conflict check detected: %s', ', '.join(conflicts))
                    update('Paused — detected: ' + ', '.join(conflicts))
                else:
                    if ctrl is None:
                        ctrl = discover(CONTROLLER_PID)
                    if ctrl is None:
                        close_devices()
                        update('Disconnected — wake controller')
                    else:
                        percent,state = read_battery(ctrl)
                        rgb = color(percent,state)
                        label = ('charging' if state == 1 else 'full' if state == 2 else 'on battery')
                        errors = []
                        key = (rgb,settings['brightness'],percent)
                        if settings['target'] in ('Controller','Both'):
                            try:
                                if original is None:
                                    original = read_config(ctrl)
                                if key != last_ctrl:
                                    write_sequence(ctrl,controller_packets(original,*key),.025)
                                    last_ctrl = key
                            except Exception as e:
                                errors.append('Controller LED: '+str(e))
                                logging.exception('Controller LED update')
                        elif last_ctrl is not None and original:
                            write_sequence(ctrl,config_packets(original),.025)
                            last_ctrl = None
                        if settings['target'] in ('Dock','Both'):
                            try:
                                if dock is None:
                                    dock = discover(DOCK_PID)
                                if dock is None:
                                    errors.append('Dock 2 Pro not detected')
                                elif key != last_dock:
                                    write_sequence(dock,dock_packets(*key),.005)
                                    last_dock = key
                            except Exception as e:
                                if dock:
                                    dock.close()
                                dock = None
                                last_dock = None
                                errors.append('Dock LED: '+str(e))
                                logging.exception('Dock LED update')
                        update(f'~{percent}% • {label}' + (' • '+ '; '.join(errors) if errors else ''),rgb,percent)
            except Exception as e:
                logging.exception('Monitor')
                close_devices()
                update(str(e))
                delay = min(delay,5)
            wake.wait(delay)
            wake.clear()
    finally:
        close_devices(restore=True)


def choose(field,value):
    def callback(icon,item):
        settings[field] = value
        save()
    return callback


def submenu(field,values):
    return pystray.Menu(*(pystray.MenuItem(str(v),choose(field,v),
           checked=lambda item,v=v: settings[field] == v,radio=True) for v in values))


def pause(icon,item):
    settings['enabled'] = not settings['enabled']
    save()


def toggle_conflicts(icon,item):
    settings['check_conflicts'] = not settings['check_conflicts']
    save()


def startup_command():
    if getattr(sys,'frozen',False):
        return subprocess.list2cmdline([sys.executable])
    pythonw = str(Path(sys.executable).with_name('pythonw.exe'))
    return subprocess.list2cmdline([pythonw,str(Path(__file__).resolve())])


def startup_enabled(item=None):
    import winreg
    try:
        with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Run',
                0,
                winreg.KEY_READ | winreg.KEY_WRITE) as key:
            command = startup_command()
            try:
                current = winreg.QueryValueEx(key, APP_NAME)[0]
            except FileNotFoundError:
                current = None
            try:
                legacy = winreg.QueryValueEx(key, LEGACY_APP_NAME)[0]
            except FileNotFoundError:
                legacy = None
            if current is None and legacy == command:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, legacy)
                current = legacy
            if legacy == command:
                winreg.DeleteValue(key, LEGACY_APP_NAME)
            return current == command
    except OSError:
        return False


def startup(icon,item):
    import winreg
    enabled = startup_enabled()
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Run') as key:
        if enabled:
            winreg.DeleteValue(key, APP_NAME)
        else:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, startup_command())


def diagnostics(icon,item):
    try:
        logging.info('HID inventory: %s',hid.enumerate(VID,0))
        os.startfile(ROOT)
    except Exception:
        logging.exception('Diagnostics')


def quit_app(icon,item):
    stop.set()
    wake.set()
    if worker_thread and worker_thread.is_alive():
        worker_thread.join(timeout=3)
    icon.stop()


if __name__ == '__main__':
    if sys.platform != 'win32':
        raise SystemExit('This app targets Windows 10/11.')
    # Prevent duplicate programs competing over the same HID interface.
    import ctypes
    ctypes.windll.kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p]
    ctypes.windll.kernel32.CreateMutexW.restype = ctypes.c_void_p
    ctypes.windll.kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    mutex = ctypes.windll.kernel32.CreateMutexW(None,False,'Local\\Vader5JuiceSingleton')
    if not mutex:
        raise ctypes.WinError()
    if ctypes.windll.kernel32.GetLastError() == 183:
        raise SystemExit(f'{APP_NAME} is already running in the tray.')
    menu = pystray.Menu(
        pystray.MenuItem(lambda item: status,None,enabled=False),
        pystray.MenuItem('Battery lighting',pause,checked=lambda item: settings['enabled']),
        pystray.MenuItem('Indicator',submenu('target',('Controller','Dock','Both'))),
        pystray.MenuItem('Brightness %',submenu('brightness',(25,50,75,100))),
        pystray.MenuItem('Update seconds',submenu('interval',(10,15,30,60))),
        pystray.MenuItem('Pause when Space Station is detected',toggle_conflicts,
                         checked=lambda item: settings['check_conflicts']),
        pystray.MenuItem('Start with Windows',startup,checked=startup_enabled),
        pystray.MenuItem('Refresh now',lambda icon,item:wake.set()),
        pystray.MenuItem('Open diagnostics folder',diagnostics),
        pystray.MenuItem('Quit (restore controller LEDs)',quit_app))
    icon = pystray.Icon(APP_NAME,badge(),APP_NAME+' — starting',menu)
    worker_thread = threading.Thread(target=worker)
    def start(icon):
        icon.visible = True
        worker_thread.start()
    try:
        icon.run(setup=start)
    finally:
        stop.set()
        wake.set()
        if worker_thread.is_alive():
            worker_thread.join(timeout=8)
        ctypes.windll.kernel32.CloseHandle(mutex)
