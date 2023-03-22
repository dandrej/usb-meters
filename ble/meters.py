import asyncio
import yaml
import sys
from pathlib import Path
from scanner import Scanner
from modulelog import setLevel
import rich

class QuitSignal:
    def __init__(self):
        from signal import SIGINT, SIGTERM
        self.event = asyncio.Event()
        loop = asyncio.get_event_loop()
        for signal in [SIGINT, SIGTERM]:
            loop.add_signal_handler(signal, self.set)
        self.task=asyncio.create_task(self.event.wait(), name='wait_quit')
    def set(self):
        print('Receive signal')
        self.event.set()

async def run_scanner(config):

    if 'logging' in config:
        console = rich.get_console()
        for level, modules in config['logging'].items():
            setLevel(modules,level,console)

    qs = QuitSignal()
    storage = None
    from storage import PrintStorage
    if 'storage' in config:
        from storage import CSVStorage, InfluxDBStorageAsync
        type = config['storage']['type']
        storage_class = {'influxdb':InfluxDBStorageAsync, 'csv':CSVStorage, 'console':PrintStorage}[type]
        storage_params = config['storage'][type]
        storage = storage_class(qs.task,**storage_params)
    if storage is None: storage = PrintStorage(qs.task)
    scanner = Scanner(config.get('devices',{}),qs.task, storage)
    await scanner.run()

config = None
for prefix in (Path.cwd(), Path(__file__).resolve().parent, Path.home()/'.config', Path('/etc')):
    config_file = prefix/'ble-config.yml'
    if config_file.exists():
        try:
            config = yaml.load(config_file.open(), Loader=yaml.SafeLoader)
        except yaml.YAMLError as e:
            if hasattr(e, 'problem_mark'):
                mark = e.problem_mark
                print(f"Config file {config_file}: error position: ({mark.line+1}:{mark.column+1})")

if config is None:
    print('No valid config file found')
    sys.exit(1)

asyncio.run(run_scanner(config))