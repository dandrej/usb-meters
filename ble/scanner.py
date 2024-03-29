import asyncio
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from bleak.backends.bluezdbus.scanner import BlueZScannerArgs

import modulelog
module_log, log, pprint = modulelog.init(__name__)

class Scanner:
    def __init__(self, devs, quit:asyncio.Task, storage):
        self.__quit = quit
        self.__storage = storage
        self.__devices = {}
        self.names = {}
        dev_handlers = {}
        for type in devs:
            dev_handlers[type]=__import__(type,globals(),locals(),['Cli'],0).Cli
        for type, names in devs.items():
            self.names.update({name:dev_handlers[type] for name in names})


    async def run(self):
        self.scanner = BleakScanner(self.detect)#,service_uuids=['0000ffe0-0000-1000-8000-00805f9b34fb','0000ff00-0000-1000-8000-00805f9b34fb','0000ffb0-0000-1000-8000-00805f9b34fb'])
        await self.scanner.start()
        await self.__quit
        log.debug('Scanner stops')
        await self.scanner.stop()
        log.debug('wait clients complete')
        await asyncio.gather(*[c.task for c in self.__devices.values()])

    def client_done(self, address):
        del self.__devices[address]

    async def run_client(self,device, client):
        await self.scanner.stop()
        try:
            log.debug('Scanner paused')
            client = client(device, self.__storage)
            self.__devices[device.address] = client
            self.__quit.add_done_callback(lambda task: client.disconnect_event.set())
            client.task.add_done_callback(lambda task: self.client_done(device.address))
            await self.__devices[device.address].connect_event.wait()
        except Exception as e:
            log.exception('Scanner failed: %s',str(e))
        finally:
            log.debug('Scanner resume...')
            await self.scanner.start()
            log.debug('Scanner resumed')

    def detect(self,device:BLEDevice, advertising_data:AdvertisementData):
        if not advertising_data.local_name: return
        if not advertising_data.local_name.strip() in self.names:
            log.debug('Device name %s skip',advertising_data.local_name)
            return
        if device.address in self.__devices: return
        pprint(device)
        pprint(advertising_data)
        client = self.names[advertising_data.local_name.strip()]
        asyncio.create_task(self.run_client(device, client))
        '''print('Local name',advertising_data.local_name)
        print('Manufacturer',advertising_data.manufacturer_data)
        print('Platform',advertising_data.platform_data)
        print('Service',advertising_data.service_data)
        print('uuids',advertising_data.service_uuids)
        print('rssi',advertising_data.rssi,advertising_data.tx_power)
        '''
