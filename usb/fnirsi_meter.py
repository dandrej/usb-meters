#!/usr/bin/python
import datetime
import time
import usb
from proto import FNIRSIMetric
from devices import get_device, get_ep, CMD1, CMD2, CMD3
from storage import InfluxStorage, CSVStorage
import yaml
import sys
from pathlib import Path
from modulelog import setLevel
import logging
import rich
from rich.pretty import pprint

class Cont:
    def __init__(self):
        from signal import SIGINT, SIGTERM, signal
        self.cont = True
        for s in (SIGINT, SIGTERM): signal(s,self.sig_handler)
    def sig_handler(self, signum, frame):
        self.cont = False
    def __bool__(self):
        return self.cont

def main(storage):
    ret = get_device()
    if ret is None: return 1
    dev, cmd, tmo, tags = ret
    #print(dev, tags)
    pprint(tags)
    try:
        ep_out, ep_in = get_ep(dev)
    except usb.core.USBError:
        return 2
    if not ( ep_in and ep_out ): return 3
    ep_out.write(CMD1)
    ep_out.write(CMD2)
    ep_out.write(cmd)
    next_send_time = datetime.datetime.now()+tmo
    time.sleep(0.1)
    cont = Cont()
    while cont:
        try:
            data = ep_in.read(size_or_buffer=64, timeout=1000)
        except Exception as e:
            logging.exception('Read USB error')
            cont.cont=False
            continue
        metrics = FNIRSIMetric.decode(data)
        if metrics:
            storage.write(metrics,tags)
        now = datetime.datetime.now()
        if now>next_send_time:
            ep_out.write(CMD3)
            next_send_time = datetime.datetime.now()+tmo
    storage.close()

config = None
for prefix in (Path.cwd(), Path(__file__).resolve().parent, Path.home()/'.config', Path('/etc')):
    config_file = prefix/'usb-config.yml'
    if config_file.exists():
        try:
            config = yaml.load(config_file.open(), Loader=yaml.SafeLoader)
            print(f'Use {config_file} config file')
        except yaml.YAMLError as e:
            if hasattr(e, 'problem_mark'):
                mark = e.problem_mark
                print(f"Config file {config_file}: error position: ({mark.line+1}:{mark.column+1})")

if config is None:
    print('No valid config file found')
    sys.exit(1)

if 'logging' in config:
    console = rich.get_console()
    for level, modules in config['logging'].items():
        setLevel(modules,level,console)

storage = None
from storage import PrintStorage
if 'storage' in config:
    from storage import CSVStorage, InfluxStorage
    type = config['storage']['type']
    storage_class = {'influxdb':InfluxStorage, 'csv':CSVStorage, 'console':PrintStorage}[type]
    storage_params = config['storage'][type]
    storage = storage_class(**storage_params)
if storage is None: storage = PrintStorage()

main(storage)