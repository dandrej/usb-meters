import asyncio
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from client import Client

from modulelog import ModuleLogging
module_log = ModuleLogging(__name__)
log, pprint = module_log.init()

class Scanner:
    def __init__(self, quit:asyncio.Task, storage):
        self.__quit = quit
        self.__storage = storage
        self.__devices = {}

    async def run(self):
        self.scanner = BleakScanner(self.detect)
        await self.scanner.start()
        await self.__quit
        log.debug('Scanner stops')
        await self.scanner.stop()
        log.debug('wait clients complete')
        await asyncio.gather(*[c.task for c in self.__devices.values()])

    def client_done(self, address):
        del self.__devices[address]

    async def run_client(self,device):
        await self.scanner.stop()
        log.debug('Scanner paused')
        self.__devices[device.address]=Client(device, self.__storage, self.__quit, self.client_done)
        await self.__devices[device.address].connect_event.wait()
        await self.scanner.start()
        log.debug('Scanner resumed')

    def detect(self,device:BLEDevice, advertising_data:AdvertisementData):
        match_data = {
            'names':[
                'DT24TW_BLE',
                'UD24_BLE'
            ],
            'services': [
                '0000ffe0-0000-1000-8000-00805f9b34fb'
            ]
        }
        names = match_data.get('names',())
        if set(match_data.get('services',())) & set(advertising_data.service_uuids):
            if names and advertising_data.local_name and advertising_data.local_name not in names:
                log.debug('Device name %s(%s) service not found',device.name,advertising_data.local_name)
                return
        elif names and advertising_data.local_name not in names:
            log.debug('Device name %s(%s) missmatch',device.name,advertising_data.local_name)
            return
        if device.address in self.__devices: return
        pprint(device)
        pprint(advertising_data)
        asyncio.create_task(self.run_client(device))
        '''print('Local name',advertising_data.local_name)
        print('Manufacturer',advertising_data.manufacturer_data)
        print('Platform',advertising_data.platform_data)
        print('Service',advertising_data.service_data)
        print('uuids',advertising_data.service_uuids)
        print('rssi',advertising_data.rssi,advertising_data.tx_power)
        '''
