from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from dataclasses import dataclass, field, asdict
import datetime
import asyncio
from binascii import hexlify
from client import Client

from modulelog import ModuleLogging
module_log = ModuleLogging(__name__)
log, pprint = module_log.init()

@dataclass
class XIAOXIANG_BMS_DATA:
    Voltage:float
    Current: float
    RemainCap:float
    NominalCap:float
    Cycles:int
    ProdDate:datetime.date
    Equilibrium:int
    Protection:int
    Ver:float
    RSOC:float # percentage of remain capacity
    FET:int
    BattStr:int
    Temp:dict[int,float] = field(default_factory=dict)

    @classmethod
    def prod_date_decode(cls, data:int)->datetime.date:
        return datetime.date(year=(data>>9) + 2000, month=(data>>5) & 0x0f, day=data & 0x1f)
    
    @classmethod
    def temp_decode(cls, data:bytearray)->dict[int,float]:
        return {(i//2+1):(int.from_bytes(data[i:i+2], byteorder='big')-2731)/10 for i in range(0, len(data), 2)}

    @classmethod
    def create(cls, data:bytearray):
        log.debug("Raw:%s",hexlify(data))
        ret = cls(
            Voltage = int.from_bytes(data[4:6], byteorder='big')/100.,
            Current = int.from_bytes(data[6:8], byteorder='big')/100.,
            RemainCap = int.from_bytes(data[8:10], byteorder='big')/100.,
            NominalCap = int.from_bytes(data[10:12], byteorder='big')/100.,
            Cycles = int.from_bytes(data[12:14], byteorder='big'),
            ProdDate = cls.prod_date_decode(int.from_bytes(data[14:16], byteorder='big')),
            Equilibrium = int.from_bytes(data[16:20], byteorder='big'),
            Protection = int.from_bytes(data[20:22], byteorder='big'),
            Ver = data[22]/10.,
            RSOC = data[23],
            FET = data[24],
            BattStr = data[25],
            Temp = cls.temp_decode(data[27:27+data[26]*2])
        )
        pprint(ret)
        return ret

    def asdict(self):
        res = asdict(self)
        del res['Temp']
        res.update({f'Temp{k}':v for k,v in self.Temp.items()})
        return res

    def __rich_repr__(self):
        yield 'Voltage',self.Voltage
        yield 'Current',self.Current
        yield 'RemainCap',self.RemainCap
        yield 'NominalCap',self.NominalCap
        yield 'Cycles',self.Cycles
        yield 'ProdDate',self.ProdDate
        yield 'Equilibrium',bin(self.Equilibrium)
        yield 'Protection',bin(self.Protection)
        yield 'Ver',self.Ver
        yield 'RSOC',f'{self.RSOC}%'
        yield 'BattStr',self.BattStr
        yield 'FET',bin(self.FET)
        for k,v in self.Temp.items():
            yield f'Temp{k}',v

    @staticmethod
    def measurement(): return 'xiaoxiang-bms'
    @staticmethod
    def tag_keys(): return None
    def field_keys(self):
        return self.asdict().keys()
    @staticmethod
    def time_key(): return None


class Device:
    def __init__(self, device:BLEDevice):
        self.device = device
        self.first_part = b''
        self.start= datetime.datetime.now().isoformat()

    def tags(self):
        return {'device':self.device.name, 'start':self.start}

    def decode(self, data):
        return XIAOXIANG_BMS_DATA.create(data)

    def get_read_data(self, storage):
        def read_data(_: BleakGATTCharacteristic, data: bytearray):
            #pprint(self.device.name)
            #pprint(data)
            if data[0] == 0xdd: self.first_part = data
            else:
                decoded_data = self.decode(self.first_part+data)
                if decoded_data is not None:
                    storage.write(decoded_data, self.tags())
        return read_data

class XiaoXiangBMS(Client):
    async def run_protocol(self, client, device, storage)->None:
        dev = Device(device)
        await client.start_notify('0000ff01-0000-1000-8000-00805f9b34fb',
                                dev.get_read_data(storage))
        await asyncio.wait([self.disconnect_event.wait(),self.write(client)],return_when=asyncio.FIRST_COMPLETED)

    async def write(self, client):
        while True:
            log.debug('Write')
            await client.write_gatt_char('0000ff02-0000-1000-8000-00805f9b34fb', b'\xdd\xa5\x03\x00\xff\xfd\x77')
            await asyncio.sleep(2)
