import asyncio
from bleak import BleakClient
from bleak.backends.device import BLEDevice
from abc import abstractmethod

from modulelog import ModuleLogging
module_log = ModuleLogging(__name__)
log, pprint = module_log.init()

class Client:
    def __init__(self, device:BLEDevice, storage):
        self.disconnect_event = asyncio.Event()
        self.connect_event = asyncio.Event()
        self.task = asyncio.create_task(self.run_client(device, storage), name=device.address)

    async def run_client(self, device, storage)->None:
        try:
            async with BleakClient(device,lambda client: self.disconnect_event.set()) as client:
                log.debug('Client %s connected',device.address)
                self.connect_event.set()
                await self.run_protocol(client, device, storage)
        except Exception as e:
            log.exception('Client failed: %s', str(e))
        log.debug('Client %s disconnected',device.address)
        if not self.connect_event.is_set(): self.connect_event.set()

    def explore(self, client):
        for service in client.services:
            log.debug(f'Service: {service}')
            for char in service.characteristics:
                log.debug(f'  Characteristic: {char} - {char.properties}')
            #log.debug(f'Service: {service.uuid} - "{service.description}"')
            #log.debug(f'Characteristics: {service.characteristics}')

    @abstractmethod
    async def run_protocol(self, client, device, storage)->None:
        ...


