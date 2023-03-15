from dataclasses import dataclass
import datetime
import struct
import crc

from modulelog import ModuleLogging
module_log = ModuleLogging(__name__)
log, pprint = module_log.init()

crc_calculator = crc.Calculator(
    crc.Configuration(
        width = 8,
        polynomial  = 0x39,
        init_value = 0x42,
        final_xor_value = 0x00,
        reverse_input = False,
        reverse_output = False
    ), optimized = True
)

@dataclass
class FNIRSIMetric:
    time:datetime.datetime
    voltage:float
    current:float
    dp:float
    dn:float
    temp:float
    fld:int
    valid:bool

    @classmethod
    def from_binary(cls,time,data,valid=True):
        v,c,p,n,f,t = struct.unpack('=IIHHBH',data)
        return cls(time=time,voltage=v/100000.,current=c/100000.,dp=p/1000.,dn=n/1000.,temp=t/10.,fld=f,valid=valid)

    @staticmethod
    def decode(data):
        vaild_crc = crc_calculator.verify(data[1:-1].tobytes(),data[-1])
        if data[1]==0x04:
            data=data[2:-1]
            now = datetime.datetime.utcnow()
            metrics = list(
                FNIRSIMetric.from_binary(
                    now+(i-3)*datetime.timedelta(milliseconds=10),
                    data[i*15:(i+1)*15],
                    vaild_crc
                )
                for i in range(4)
            )
            pprint(metrics)
            return metrics
        return None
    @staticmethod
    def measurement(): return 'fnirsi-usb-meter'
    @staticmethod
    def tag_keys(): return ('valid',)
    @staticmethod
    def field_keys(): return ('voltage', 'current', 'dp', 'dn', 'temp')
    @staticmethod
    def time_key(): return 'time'
