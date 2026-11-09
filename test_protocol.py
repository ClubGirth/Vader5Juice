import unittest
from protocol import *

class ProtocolTests(unittest.TestCase):
    INFO = bytes.fromhex('5a a5 01 01 00 82 01 00 00 00 00 05 45 01 00 72 21 04 83 36 05 00 00 00 00 00 00 10 43 27 00 9f')

    def test_documented_battery(self):
        self.assertEqual(battery(self.INFO),(100,0))
        self.assertEqual(battery(b'\0'+self.INFO),(100,0))
        for level in range(6):
            for state in range(3):
                reply = bytearray(self.INFO)
                reply[11] = state*16+level
                self.assertEqual(battery(reply),(level*20,state))

    def test_invalid_and_unrelated(self):
        self.assertIsNone(battery(self.INFO[:12]))
        unrelated = bytearray(self.INFO)
        unrelated[2] = 0xef
        self.assertIsNone(battery(unrelated))
        for raw in (6,0xff,0x35):
            malformed = bytearray(self.INFO)
            malformed[11] = raw
            with self.assertRaises(ValueError): battery(malformed)
        wrong = bytearray(self.INFO)
        wrong[5] = 128
        with self.assertRaises(ValueError): battery(wrong)

    def test_controller_roundtrip(self):
        for version,count in ((2,16),(3,8)):
            current = bytearray(20)
            current[1] = version
            current[7] = count
            reports = controller_packets(current,(1,2,3),75)
            chunks = [r[5:5+r[3]-3] for r in reports[1:]]
            config = b''.join(chunks)
            self.assertEqual(config[3:9],bytes([0,0,0,75,count,5]))
            self.assertEqual(config[20:],bytes([1,2,3])*(160 if version == 2 else count))
            self.assertEqual(reports[0][2:8],bytes([0xa8,6,0,0,len(chunks),20]))
            for report in reports:
                self.assertEqual(len(report),32)
                # Controller len counts command plus len plus payload.
                checksum_at = 2+report[3]
                self.assertEqual(report[checksum_at],sum(report[2:checksum_at])&255)
        with self.assertRaises(ValueError): controller_packets(bytes(20),(0,0,0))

    def test_dock_golden_and_pixels(self):
        reports = dock_packets((1,2,3),75)
        self.assertEqual(reports[0][:10],bytes.fromhex('5a a5 61 07 0a 00 00 00 0a 7c'))
        payload = b''.join(r[9:9+r[8]] for r in reports[1:])
        self.assertEqual(payload,bytes([1,1,75,3,0,0])+bytes([1,2,3])*162)
        for i,r in enumerate(reports[1:]):
            self.assertEqual(len(r),64)
            self.assertEqual(r[7],i)
            self.assertEqual(r[5],10)
            checksum_at = 9+r[8]
            self.assertEqual(r[checksum_at],sum(r[2:checksum_at])&255)

    def test_chunk_and_colors(self):
        r = bytes([0x5a,0xa5,0xa7,2,1,20])+bytes(range(20))+bytes(6)
        self.assertEqual(config_chunk(r),(2,1,bytes(range(20))))
        self.assertIsNone(config_chunk(r[:20]))
        self.assertEqual(color(20,0),(255,0,0))
        self.assertEqual(color(40,1),(0,100,255))
        self.assertEqual(color(100,2),(0,255,0))

    def test_shrinking_bars(self):
        for percent in (0,20,40,60,80,100):
            rgb = color(percent,0)
            for version,count in ((2,8),(2,16),(3,8),(3,16)):
                current = bytearray(20)
                current[1],current[7] = version,count
                reports = controller_packets(current,rgb,50,percent)
                config = b''.join(r[5:5+r[3]-3] for r in reports[1:])
                pixels = count * 10 if version == 2 else count
                lit = max(1,(pixels * percent + 50)//100)
                expected = bytes(rgb)*lit + bytes(3*(pixels-lit))
                if version == 2:
                    expected += bytes(3*(160-pixels))
                self.assertEqual(config[20:],expected)
                self.assertEqual(config[6],50)
            reports = dock_packets(rgb,50,percent)
            payload = b''.join(r[9:9+r[8]] for r in reports[1:])
            lit = max(1,(162*percent+50)//100)
            self.assertEqual(payload,bytes([1,1,50,3,0,0])+bytes(EMPTY_RGB)*(162-lit)+bytes(rgb)*lit)
        self.assertEqual(bar_pixels(8,color(40,1),40),bytes([0,100,255])*3+bytes(15))
        for percent in (-1,101):
            with self.assertRaises(ValueError):
                dock_packets((255,0,0),percent=percent)

if __name__ == '__main__': unittest.main()
