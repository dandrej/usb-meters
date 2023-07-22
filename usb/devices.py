import usb.core
import usb.util
import datetime

import modulelog
module_log, log, pprint = modulelog.init(__name__)

CMD1 = b"\xaa\x81" + b"\x00" * 61 + b"\x8e"
CMD2 = b"\xaa\x82" + b"\x00" * 61 + b"\x96"
CMD3 = b"\xaa\x83" + b"\x00" * 61 + b"\x9e"

FNB48 = {
    "VID_PID" : {"idVendor":0x0483, "idProduct":0x003A},
    "CMD": CMD3,
    "tmo": datetime.timedelta(milliseconds=3),
}
C1 = {
    "VID_PID" : {"idVendor":0x0483, "idProduct":0x003B},
    "CMD": CMD3,
    "tmo": datetime.timedelta(milliseconds=3),
}
FNB48S = {
    "VID_PID" : {"idVendor":0x2E3C, "idProduct":0x0049},
    "CMD": CMD2,
    "tmo": datetime.timedelta(milliseconds=900),
}
FNB58 = {
    "VID_PID" : {"idVendor":0x2E3C, "idProduct":0x5558},
    "CMD": CMD2,
    "tmo": datetime.timedelta(milliseconds=900),
}

def get_device():
    for descr in (FNB48, C1, FNB48S, FNB58):
        dev = usb.core.find(**descr["VID_PID"])
        if dev:
            tags = {name:getattr(dev,name).replace(' ','_') for name in ('manufacturer','product','serial_number')}
            tags['start']= str(datetime.datetime.now().isoformat())
            return dev, descr["CMD"], descr["tmo"], tags
    return None

def get_ep(dev):
    dev.reset()
    intf_hid = 0
    for cfg in dev:
        for intf in cfg:
            if intf.bInterfaceClass == 0x03:  # HID class
                intf_hid = intf.bInterfaceNumber
            if dev.is_kernel_driver_active(intf.bInterfaceNumber):
                    dev.detach_kernel_driver(intf.bInterfaceNumber)
    usb.util.claim_interface(dev, 0)
    # get an endpoint instance
    cfg = dev.get_active_configuration()
    intf = cfg[(intf_hid, 0)]
    return (
        usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == dir)
        for dir in (usb.util.ENDPOINT_OUT, usb.util.ENDPOINT_IN)
    )
