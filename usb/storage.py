from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import csv
import gzip

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.write.point import Point
from urllib3.util.retry import Retry

import logging
from modulelog import ModuleLogging
module_log = ModuleLogging(__name__)
log, pprint = module_log.init()
from rich.pretty import pprint as rich_pprint

class InfluxStorage:
    def __init__(self, bucket:str, url:str, org:str | None = None,
                token:str | None = None, debug:bool = False, timeout:int = 10000,
                enable_gzip = False, default_tags=[], **kwargs):
        self.cli = influxdb_client.InfluxDBClient(
            url=url,org=org,token=token,debug=debug,timeout=timeout,enable_gzip=enable_gzip,
            default_tags=default_tags,retries=Retry(),**kwargs)
        if log.isEnabledFor(logging.DEBUG):
            self.__debug()
        self.write_api = self.cli.write_api(write_options=SYNCHRONOUS)
        self.bucket = bucket

    def write(self, metrics, tags):
        if not metrics: return
        points = list(Point.from_dict(
            asdict(m),
            record_measurement_name = m.measurement(),
            record_tag_keys = m.tag_keys(),
            record_field_keys = m.field_keys(),
            record_time_key = m.time_key()
        ) for m in metrics)
        if tags:
            for p in points: p._tags.update(tags)
        pprint(list(p.to_line_protocol() for p in points))
        self.write_api.write(bucket = self.bucket, record = points)
    def close(self):
        self.write_api.close()
        self.cli.close()
    def __debug(self):
        if module_log.console is None: return
        for _, logger in self.cli.conf.loggers.items():
            logger.setLevel(logging.DEBUG)
            logger.addHandler(module_log.log_handler())


class CSVStorage:
    def __init__(self, path, is_gzip=False, kwargs:dict=dict()):
        path = Path(path)
        if not path.is_dir():
            path.mkdir(parents=True)
        self.__path = path
        self.__is_gzip = is_gzip
        self.__fd = None
        self.__writer = None
        self.__kwargs = kwargs
    def write(self, metrics,tags):
        if not metrics: return
        if self.__writer is None:
            if self.__is_gzip:
                self.__fd = gzip.open(self.__path/(' '.join(tags.values())+'.csv.gz'),'wt',newline='')
            else:
                self.__fd = open(self.__path/(' '.join(tags.values())+'.csv'),'w',newline='')
            self.__writer = csv.DictWriter(self.__fd, (metrics[0].time_key(),)+metrics[0].field_keys(),extrasaction='ignore',**self.__kwargs)
            self.__writer.writeheader()
        elif self.__fd is None: return
        self.__writer.writerows((asdict(m) for m in metrics))
    def close(self):
        if self.__fd is not None: 
            self.__fd.close()
            self.__fd = None

class PrintStorage:
    def __init__(self, type='pretty'):
        self.type = type
    def write(self, metrics, tags):
        if self.type=='pretty':
            rich_pprint(metrics)
            if tags: rich_pprint(tags)
    def close(self):
        ...
