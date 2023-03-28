# Data collector for USB testers (ATorch, FNIRSI)
I have bought some USB testers with Bluetooth communication recently. These devices are smart enough but do not have any software on Linux. Unfortunately, the existing Android applications have the same interfaces as the devices themself. But it would be great to have a logger of my works with these devices that collect and store data from them, which I will analyze later with some standard tool like Grafana. Ideally, I want to switch on my Raspberry Pi only before a job with a USB logger starts. And store all data that the USB tester interface displays.
So let's go to work.
## Main steps
* [Create an image for RaspberryPi][rpi]
* [Install and configure InfluxDB][influxdb]
* [Install and configure loggers][software]

## Acknowlegements
I would like to thanks the following projects which code and information have been used in this project:
- [tomwang221812/atorch_meter_pyhton](https://github.com/tomwang221812/atorch_meter_pyhton)
- [NiceLabs/atorch-console](https://github.com/NiceLabs/atorch-console)
- [baryluk/fnirsi-usb-power-data-logger](https://github.com/baryluk/fnirsi-usb-power-data-logger)

[software]: doc/software.md
[influxdb]: doc/influxdb.md
[rpi]: doc/rpi.md