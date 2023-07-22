from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from client import Client
import datetime
import struct
from binascii import hexlify
from dataclasses import dataclass

from modulelog import ModuleLogging
module_log = ModuleLogging(__name__)
log, pprint = module_log.init()

@dataclass
class Pack4:
    voltage:float
    current:float
    W:float
    @classmethod
    def create(cls, data:bytearray):
        v,a,w = struct.unpack('=III',data)
        return cls(voltage=v/10000,current=a/10000,W=w/10000)

    def __rich_repr__(self):
        yield 'V',self.voltage
        yield 'A',self.current
        yield 'W',self.W

    @staticmethod
    def measurement(): return 'fnirsi-usb-meter'
    @staticmethod
    def tag_keys(): return None
    @staticmethod
    def field_keys(): return ('voltage', 'current', 'W')
    @staticmethod
    def time_key(): return None

@dataclass
class Pack5:
    Ohm:int
    F52:int
    temp:int
#
        #07 a9c90500 01 2401 59
        #07 60c80500 01 2401 20
        #07 afc80500 01 2401 dc
        #07 e7c30500 01 2401 3f
        #07 e7c10500 01 2301 e8
    @classmethod
    def create(cls, data:bytearray):
        ohm,f2,t = struct.unpack('=IBH',data)
        return cls(Ohm=ohm,F52=f2,temp=t/10)

    def __rich_repr__(self):
        yield 'Ohm',self.Ohm
        yield 'F52',self.F52
        yield 'T',self.temp

    @staticmethod
    def measurement(): return 'fnirsi-usb-meter'
    @staticmethod
    def tag_keys(): return None
    @staticmethod
    def field_keys(): return ('Ohm', 'F52', 'T')
    @staticmethod
    def time_key(): return None

@dataclass
class Pack6:
    dp:int
    dn:int
    F63:int
#        ?  D+   D-   ?   ?
        #06 0000 0400 010b 93
        #06 0400 0400 010b 32
        #06 0400 0300 010b 1f
        #06 0400 0100 010b 77
        #06 0100 0000 010b c2
        #06 0000 0000 010b 62
        #06 0000 0100 010b d6
        #06 0100 0000 010b c2
        #06 0100 0100 010b 76
    @classmethod
    def create(cls, data:bytearray):
        dp,dm,f3 = struct.unpack('=HHH',data)
        return cls(dp=dp/1000,dn=dm/1000,F63=f3)

    def __rich_repr__(self):
        yield 'D+',self.dp
        yield 'D-',self.dn
        yield 'F63',self.F63

    @staticmethod
    def measurement(): return 'fnirsi-usb-meter'
    @staticmethod
    def tag_keys(): return None
    @staticmethod
    def field_keys(): return ('dp', 'dn', 'F63')
    @staticmethod
    def time_key(): return None

@dataclass
class Pack7:
    F71:int
    F72:int
#
        #04 c013 8a00 c2
        #04 b813 8300 ec
        #04 bc13 9700 aa
        #04 c213 8400 a5
        #04 c013 8b00 f3
    @classmethod
    def create(cls, data:bytearray):
        f1,f2 = struct.unpack('=HH',data)
        return cls(F71=f1,F72=f2)

    def __rich_repr__(self):
        yield 'F71',self.F71
        yield 'F72',self.F72

    @staticmethod
    def measurement(): return 'fnirsi-usb-meter'
    @staticmethod
    def tag_keys(): return None
    @staticmethod
    def field_keys(): return ('F71', 'F72')
    @staticmethod
    def time_key(): return None

@dataclass
class Pack8:
    Grp:int
    Wh:float
    Ah:float
    Sec:int
#
        #11 06 1ad61f00 a3130500 7a1d0000 00000000 90
        #11 06 1ad61f00 a3130500 7a1d0000 00000000 90
        #11 06 07d61f00 9f130500 791d0000 00000000 10
        #11 06 07d61f00 9f130500 791d0000 00000000 10
        #11 06 f4d51f00 9c130500 781d0000 00000000 73
        #11 06 f4d51f00 9c130500 781d0000 00000000 73
        #11 06 e2d51f00 98130500 771d0000 00000000 d4
        #11 06 e2d51f00 98130500 771d0000 00000000 d4
    @classmethod
    def create(cls, data:bytearray):
        grp,wh,ah,sec = struct.unpack('=BIIQ',data)
        return cls(Grp=grp,Wh=wh/100000,Ah=ah/100000,Sec=sec)

    def __rich_repr__(self):
        yield 'Grp',self.Grp
        yield 'Wh',self.Wh
        yield 'Ah',self.Ah
        yield 'Time',str(datetime.timedelta(seconds=self.Sec))

    @staticmethod
    def measurement(): return 'fnirsi-usb-meter'
    @staticmethod
    def tag_keys(): return ('Grp', )
    @staticmethod
    def field_keys(): return ('Wh', 'Ah', 'Sec')
    @staticmethod
    def time_key(): return None

class Device:
    def __init__(self, device:BLEDevice):
        self.device = device
        self.start= datetime.datetime.now().isoformat()

    def tags(self):
        return {'device':self.device.name, 'start':self.start}


    def get_read_data(self, storage):
        def read_data(_: BleakGATTCharacteristic, data: bytearray):
            pprint(self.device.name)
            packs = {4:Pack4,5:Pack5,6:Pack6,7:Pack7,8:Pack8}
            while data:
                if data[0]!=0xaa:
                    log.debug(f'Unknown data: {hexlify(data)}')
                    return
                pack_type = data[1]
                pack = data[3:3+data[2]]
                data=data[4+data[2]:]
                if pack_type not in packs.keys():
                    log.error(f'Unknown pack: {hexlify(data)}')
                    continue
                info = packs[pack_type].create(pack)
                storage.write(info, self.tags())
        return read_data

class FNIRSI_USB(Client):
    async def run_protocol(self, client, device, storage)->None:
        #self.explore(client)
        dev = Device(device)
        log.debug('notify')
        await client.start_notify('0000ffe4-0000-1000-8000-00805f9b34fb', dev.get_read_data(storage))
        log.debug('write1')
        await client.write_gatt_char('0000ffe9-0000-1000-8000-00805f9b34fb', b'\xaa\x81\x00\xf4')
        log.debug('write2')
        await client.write_gatt_char('0000ffe9-0000-1000-8000-00805f9b34fb', b'\xaa\x82\x00\xa7')
        await self.disconnect_event.wait()
