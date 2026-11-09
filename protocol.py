"""Flydigi protocol; lighting adapted from ControlLab (MIT, see THIRD_PARTY)."""
VID, CONTROLLER_PID, DOCK_PID, PAGE = 0x37D7, 0x2401, 0x6001, 0xFFA0

def packet(body, size=32):
    if len(body) + 3 > size:
        raise ValueError('Packet too large')
    return bytes([0x5a, 0xa5, *body, sum(body) & 255]).ljust(size, b'\0')

def normalize(data):
    data = bytes(data)
    if data[:3] == b'\x00\x5a\xa5':
        data = data[1:]
    return data

def battery(data):
    d = normalize(data)
    if len(d) < 32 or d[:3] != b'\x5a\xa5\x01' or d[4] != 0:
        return None
    if d[5] != 130:
        raise ValueError('Info reply is not a Vader 5 Pro')
    raw = d[11]
    if raw & 15 > 5 or raw >> 4 > 2:
        raise ValueError('Unknown battery encoding')
    return (raw & 15) * 20, raw >> 4

def color(percent, state):
    if state == 1:
        return (0, 100, 255)
    if state == 2:
        return (0, 255, 0)
    return {100:(0,255,0), 80:(130,255,0), 60:(255,220,0),
            40:(255,90,0), 20:(255,0,0), 0:(255,0,0)}[percent]

def config_chunk(data):
    d = normalize(data)
    if len(d) >= 26 and d[:3] == b'\x5a\xa5\xa7' and 0 < d[3] <= 100 and d[4] < d[3]:
        return d[3], d[4], d[6:26]
    return None

def config_packets(config):
    chunks = [config[i:i+20] for i in range(0, len(config), 20)]
    if not chunks or len(chunks) > 255:
        raise ValueError('Invalid lighting configuration length')
    return [packet([0xa8,6,0,0,len(chunks),20])] + [
        packet([0xa9,len(chunk)+3,i,*chunk]) for i,chunk in enumerate(chunks)]

EMPTY_RGB = (8, 8, 8)  # Dim white for the depleted portion; global brightness still applies.

def bar_pixels(count, rgb, percent, empty_rgb=(0, 0, 0)):
    """Fill in device LED order, with an optional depleted-portion color."""
    if not 0 <= percent <= 100:
        raise ValueError('Battery percentage must be between 0 and 100')
    lit = max(1, (count * percent + 50) // 100)
    return bytes(rgb) * lit + bytes(empty_rgb) * (count - lit)


def controller_packets(current, rgb, brightness=75, percent=100):
    if len(current) < 20 or current[0] != 0 or current[1] not in (2,3) or not 1 <= current[7] <= 16:
        raise ValueError('Unsupported LED configuration; no write performed')
    count = current[7]
    config = bytearray(current[:20])
    config[3:9] = bytes([0,0,0,brightness,count,5])
    if current[1] == 3:
        config.extend(bar_pixels(count, rgb, percent))
    else:
        config.extend(bar_pixels(count * 10, rgb, percent))
        config.extend(b'\0\0\0' * ((16 - count) * 10))
    return config_packets(config)

def dock_packets(rgb, brightness=75, percent=100):
    # Reverse whole RGB pixels so the dock empties from the top down.
    pixels = bar_pixels(162, rgb, percent, EMPTY_RGB)
    pixels = b''.join(pixels[i:i+3] for i in range(len(pixels)-3, -1, -3))
    payload = bytes([1,1,brightness,3,0,0]) + pixels
    chunks = [payload[i:i+50] for i in range(0,len(payload),50)]
    n = len(chunks)
    return [packet([0x61,7,10,0,0,n>>8,n&255],64)] + [
        packet([0x62,len(chunk)+7,n>>8,n&255,i>>8,i&255,len(chunk),*chunk],64)
        for i,chunk in enumerate(chunks)]
