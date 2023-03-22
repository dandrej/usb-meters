import asyncio
from bleak import BleakClient
from bleak.backends.device import BLEDevice
from protocols import get_read_data, Device

from modulelog import ModuleLogging
module_log = ModuleLogging(__name__)
log, pprint = module_log.init()

class Client:
    def __init__(self, device:BLEDevice, storage, quit:asyncio.Task, on_disconnect):
        self.disconnect_event = asyncio.Event()
        self.connect_event = asyncio.Event()
        quit.add_done_callback(lambda task: self.disconnect_event.set())
        self.task = asyncio.create_task(self.run_client(device, storage), name=device.address)
        self.on_disconnect = on_disconnect

    async def run_client(self, device, storage)->None:
        dev = Device(device)
        try:
            async with BleakClient(device,lambda client: self.disconnect_event.set()) as client:
                log.debug('Client %s connected',device.address)
                self.connect_event.set()
                await client.start_notify('0000ffe1-0000-1000-8000-00805f9b34fb',
                                        get_read_data(dev, storage))
                await self.disconnect_event.wait()
        except Exception as e:
            log.exception('Client failed: %s', str(e))
        log.debug('Client %s disconnected',device.address)
        self.on_disconnect(device.address)
        if not self.connect_event.is_set(): self.connect_event.set()
        

