import asyncio
import pathlib
from typing import Sequence

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice


async def find_all_devices_services():
    scanner = BleakScanner()
    devices: Sequence[BLEDevice] = await scanner.discover(timeout=5.0)
    for d in devices:
        print('Device:',str(d))
        try:
            async with BleakClient(d) as client:
                for sidx, service in enumerate(client.services):
                    print(f"Service#{sidx}:",service.description)
                    for cidx, char in enumerate(service.characteristics):
                        print(f"Characteristic#{cidx}:",char.description)
                        print(char.properties)
                    print('---------------')
        except Exception as e:
            print('Error:',str(e))

devices = []

async def client_log(d=None):
    #await asyncio.sleep(5)
    if d is None: d = my_device
    if d is None:
        print('No device specified')
        return
    async with BleakClient(d) as client:
        if d.address in devices: devices.remove(d.address)
        for sidx, service in enumerate(client.services):
            print(f"Service#{sidx}:",service.description)
            for cidx, char in enumerate(service.characteristics):
                print(f"Characteristic#{cidx}:",char.description)
                print(char.properties)
            print('---------------')


import asyncio
from bleak import BleakScanner

my_device = None
from functools import reduce

async def scanner(event):

    def callback(device, advertising_data):
        global my_device
        # TODO: do something with incoming data
        if device.address in devices: return
        if advertising_data.local_name != 'UD24_BLE': return
        if advertising_data.platform_data[1]['Connected']: return
        my_device = device
        print('Device:', device.address, device.details, device.name)
        devices.append(device.address)
        asyncio.get_event_loop().create_task(client_log(device))
        #print('Local name',advertising_data.local_name)
        #print('Manufacturer',advertising_data.manufacturer_data)
        #print('Platform',advertising_data.platform_data)
        #print('Service',advertising_data.service_data)
        #print('uuids',advertising_data.service_uuids)
        #print('rssi',advertising_data.rssi,advertising_data.tx_power)

    async with BleakScanner(callback):
        await event.wait()

async def timer(event):
    await asyncio.sleep(20)
    event.set()

async def scanner_main():
    event = asyncio.Event()
    await asyncio.gather(
        asyncio.create_task(scanner(event)),
        asyncio.create_task(timer(event))
    )

def checksum():
    import binascii

    packet = bytes.fromhex('FF551103310000000001')
    payload = packet[2:-1]  # b'\x11\x03\x31\x00\x00\x00'
    print(payload)

    checksum = (sum(payload) & 0xff) ^ 0x44  # 0x01
    print(packet[-1], checksum)

def chk():
    #p = b'\x01\x03\x00\x01\xfc\x00\x00\x00\x00\x08\x01\x00\x00\x03\xff\x00\x00\x00\x00\x00\x1c\x00\x02\x08\x19<\x0b\xb8\x00\x00\x03\xdd\x00'
    p = b'\x01\x03\x00\x01\xfc\x00\x00\x00\x00\x08\x01\x00\x00\x03\xff\x00\x00\x00\x00\x00\x1c\x00\x02\x08\x19<\x0b\xb8\x00\x00\x03\xdd\x00'
    #p=b'\x11\x03\x31\x00\x00\x00\x00'
    chksum = 253
    res = reduce(lambda x,y: (int(x)+int(y)) & 0xff, p, 0) ^ 0x44
    #s = 0
    #s1 = 0
    #for c in p:
    #    s += int(c)
    #    s1 = s
    #    s &= 0xff
    #s1 &= 0xff
    s = sum(p) & 0xff
    #print(s, s1, s2, s ^ 0x44)
    #xorbyte = 0x44
    xorbyte = 0xd7
    chk = s ^ xorbyte
    print(s, s ^ xorbyte, chksum)
    print(bin(s), bin(s ^ xorbyte), bin(chksum))
    print(bin(chk ^ s),hex(chk ^ s))
    #print(bin(chksum ^ s),hex(chksum ^ s))

def path():
    print(pathlib.Path(__file__).resolve().parent)

#asyncio.run(find_all_devices_services())
#asyncio.run(client_log('0D:9A:BF:9A:0D:BD'))
#asyncio.run(scanner_main())
#chk()
path()