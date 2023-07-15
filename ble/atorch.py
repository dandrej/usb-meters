from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from dataclasses import dataclass, field
import datetime
from binascii import hexlify
from client import Client

from modulelog import ModuleLogging
module_log = ModuleLogging(__name__)
log, pprint = module_log.init()

@dataclass
class ATORCH_USB_METER_DATA:
    Voltage:float
    Amp: float
    A_h:float
    W_h:float
    USB_Dn:float
    USB_Dp:float
    Temperature:float
    Time:float
    Backlight:int
    OvrV:float
    LowV:float
    OvrC:float
    Rest:bytearray
    stamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    @classmethod
    def create(cls, data:bytearray):
        #       V       A      Ah    Wh       D+   D-   T     Time Bklt OvrV LowV OvrC
        #01-03-0001fc-000000-000801-000003ff-0000-0000-001c-00020819-3c-0bb8-0000-03dd-00??
        log.debug("Raw:%s",hexlify(data))
        ret = cls(
            Voltage = int.from_bytes(data[2:5], byteorder='big')/100.,
            Amp = int.from_bytes(data[5:8], byteorder='big')/100.,
            A_h = int.from_bytes(data[8:11], byteorder='big')/1000.,
            W_h = int.from_bytes(data[11:15], byteorder='big')/100.,
            USB_Dn = int.from_bytes(data[15:17], byteorder='big'),
            USB_Dp = int.from_bytes(data[17:19], byteorder='big'),
            Temperature = int.from_bytes(data[19:21], byteorder='big'),
            Time = datetime.timedelta(
                hours=int.from_bytes(data[21:23], byteorder='big'),
                minutes=data[23],
                seconds=data[24]
            ).total_seconds(),
            Backlight=data[25],
            OvrV = int.from_bytes(data[26:28], byteorder='big')/100.,
            LowV = int.from_bytes(data[28:30], byteorder='big')/100.,
            OvrC = int.from_bytes(data[30:32], byteorder='big')/100.,
            Rest = data[32:]
        )
        pprint(ret)
        return ret
    def __rich_repr__(self):
        yield 'V',self.Voltage
        yield 'A',self.Amp
        yield 'Ah',self.A_h
        yield 'Wh',self.W_h
        yield 'D+',self.USB_Dp
        yield 'D-',self.USB_Dn
        yield 'Temp',self.Temperature
        yield 'Time',self.Time
        yield 'Backlight',self.Backlight
        yield 'OvrV',self.OvrV
        yield 'LowV',self.LowV
        yield 'OvrC',self.OvrC
        yield 'Rest',hexlify(self.Rest)

    @staticmethod
    def measurement(): return 'at24-usb-meter'
    @staticmethod
    def tag_keys(): return None
    @staticmethod
    def field_keys(): return ('Voltage', 'Amp', 'A_h', 'W_h', 'USB_Dp','USB_Dn','Temperature','Time','OvrV','LowV','OvrC','Backlight')
    @staticmethod
    def time_key(): return 'stamp'

@dataclass
class ATORCH_DC_METER_DATA:
    Voltage:float
    Amp: float
    Cap:float
    Pwr:float
    Fld1:bytearray
    Temperature:float
    RunTime:float
    Backlight:int
    Fld2:bytearray
    @classmethod
    def create(cls, data:bytearray):
        #        V       A    Cap     Pwr                  T    --Time-- Bklt
        #01-02-000082-000000-003a98-00000000-000000000000-0014-0025-1a-28-3c-00000000
        #01-02-000080-000000-003a98-00000026-000000000000-0016-0123-10-37-3c-0000000023
        #Voltage=12.8, Amp=0.0, Cap=150.0, Pwr=0.38, Temp=22, RunTime='12 days, 3:16:55', Backlight=60, Fld1=b'000000000000', Fld2=b'0000000023'
        log.debug("Raw:%s",hexlify(data))
        ret = cls(
            Voltage = int.from_bytes(data[2:5], byteorder='big')/10.,
            Amp = int.from_bytes(data[5:8], byteorder='big')/1000.,
            Cap = int.from_bytes(data[8:11], byteorder='big')/100.,
            Pwr = int.from_bytes(data[11:15], byteorder='big')/100.,
            Fld1 = data[15:21],
            Temperature = int.from_bytes(data[21:23], byteorder='big'),
            RunTime = datetime.timedelta(
                hours=int.from_bytes(data[23:25], byteorder='big'),
                minutes=data[25],
                seconds=data[26]
            ).total_seconds(),
            Backlight=data[27],
            Fld2 = data[28:]
        )
        pprint(ret)
        return ret
    def __rich_repr__(self):
        yield 'Voltage',self.Voltage
        yield 'Amp',self.Amp
        yield 'Cap',self.Cap
        yield 'Pwr',self.Pwr
        yield 'Temp',self.Temperature
        yield 'RunTime',str(datetime.timedelta(seconds=self.RunTime))
        yield 'Backlight',self.Backlight
        yield 'Fld1',hexlify(self.Fld1)
        yield 'Fld2',hexlify(self.Fld2)

    @staticmethod
    def measurement(): return 'dt24tw-usb-meter'
    @staticmethod
    def tag_keys(): return None
    @staticmethod
    def field_keys(): return ('Voltage', 'Amp', 'Cap', 'Pwr', 'Temperature','RunTime','Backlight')
    @staticmethod
    def time_key(): return None


class Device:
    def __init__(self, device:BLEDevice):
        self.device = device
        self.atorch_dc_part = bytearray(b'')
        self.start= datetime.datetime.now().isoformat()
    def tags(self):
        return {'device':self.device.name, 'start':self.start}

    def atorch_decode(self, data: bytearray):
        if self.atorch_dc_part!=bytearray(b''):
            packet = ATORCH_DC_METER_DATA.create(self.atorch_dc_part+data)
            self.atorch_dc_part = bytearray(b'')
            return packet
        if data[0:2]!=b'\xFF\x55':
            log.debug('Wrong ATorch packet header: %s',data)
            return None
        if data[2]!=1:
            log.debug('Wrong ATorch packet type: %s',data[2])
            return None
        payload = data[2:-1]
        if payload[1]==3:
            packet = ATORCH_USB_METER_DATA.create(payload)
            return packet
        if payload[1]==2:
            self.atorch_dc_part = payload
            return None
        log.debug('Unknown ATORCH payload: %s', hexlify(payload))
        return None

    def decode(self, data: bytearray):
        packet = self.atorch_decode(data)
        return packet

    def get_read_data(self, storage):
        def read_data(_: BleakGATTCharacteristic, data: bytearray):
            pprint(self.device.name)
            #pprint(device.metadata)
            decoded_data = self.decode(data)
            if decoded_data is not None:
                storage.write(decoded_data, self.tags())
        return read_data

class ATORCHClient(Client):
    async def run_protocol(self, client, device, storage)->None:
        dev = Device(device)
        await client.start_notify('0000ffe1-0000-1000-8000-00805f9b34fb',
                                dev.get_read_data(storage))
        await self.disconnect_event.wait()