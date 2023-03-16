from __future__ import annotations
from dataclasses import dataclass, asdict
import sys
import asyncio

from pathlib import Path
import csv
import gzip

from influxdb_client.client.write.point import Point
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

import logging
from modulelog import ModuleLogging
module_log = ModuleLogging(__name__)
log, pprint = module_log.init()
from rich.pretty import pprint as rich_pprint


class CSVStorage:
    def __init__(self, quit:asyncio.Task, path, is_gzip=False, kwargs:dict=dict()):
        self.path = Path(path)
        if not self.path.is_dir():
            self.path.mkdir(parents=True)
        self.is_gzip = is_gzip
        self.__fd = None
        self.__writer = None
        self.__kwargs = kwargs
        quit.add_done_callback(self.__close)
    def write(self, metrics, tags):
        if not metrics: return
        if self.__writer is None:
            if self.is_gzip:
                self.__fd = gzip.open(self.path/(' '.join(tags.values())+'.csv.gz'),'wt',newline='')
            else:
                self.__fd = open(self.path/(' '.join(tags.values())+'.csv'),'w',newline='')
            self.__writer = csv.DictWriter(self.__fd, (metrics.time_key(),)+metrics.field_keys(),extrasaction='ignore',**self.__kwargs)
            self.__writer.writeheader()
        elif self.__fd is None: return
        self.__writer.writerow(asdict(metrics))
    def __close(self, task):
        if self.__fd:
            self.__fd.close()
            self.__fd = None


class PrintStorage:
    def __init__(self, quit:asyncio.Task, type='pretty'):
        self.type = type
    def write(self, metrics, tags):
        if self.type=='pretty':
            rich_pprint(metrics)
            if tags: rich_pprint(tags)

@dataclass
class InfluxClientArgs:
    url:str
    org:str | None = None
    token:str | None = None
    debug:bool = False
    timeout:int = 10000
    enable_gzip:bool = False
    default_tags:dict | None = None

class InfluxDBStorageAsync:
    def __init__(self, quit:asyncio.Task, bucket:str, url:str, org:str | None = None,
                token:str | None = None, debug:bool = False, timeout:int = 10000,
                enable_gzip = False, default_tags=[], **kwargs):
        self.bucket = bucket
        client_args = InfluxClientArgs(
            url=url,
            org=org,
            token=token,
            debug=debug,
            timeout=timeout,
            enable_gzip=enable_gzip,
            default_tags=default_tags
        )
        self.task = asyncio.create_task(self.__run(client_args, kwargs))
        quit.add_done_callback(self.__close)

    def write(self, metrics, tags):
        if not metrics: return
        self.queue.put_nowait((metrics,tags))

    async def __run(self,client_args:InfluxClientArgs, client_kwargs:dict):
        self.queue = asyncio.Queue()
        cli = InfluxDBClientAsync(**asdict(client_args),**client_kwargs)
        self.__debug(cli)
        write_api = cli.write_api()
        while True:
            metrics, tags = await self.queue.get()
            if metrics is None: break
            point = Point.from_dict(
                asdict(metrics),
                record_measurement_name = metrics.measurement(),
                record_tag_keys = metrics.tag_keys(),
                record_field_keys = metrics.field_keys(),
                record_time_key = metrics.time_key()
            )
            if tags:
                point._tags.update(tags)
            await write_api.write(bucket = self.bucket, record = point)
        await cli.close()

    def __close(self,task):
        self.queue.put_nowait((None,None))

    @staticmethod
    def __debug(cli):
        if module_log.console is None: return
        for _, logger in cli.conf.loggers.items():
            logger.setLevel(logging.DEBUG)
            logger.addHandler(module_log.debug_handler())
