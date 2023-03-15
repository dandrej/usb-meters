# Data collector from USB testers (ATorch, FNIRSI)
I have bought some USB testers with Bluetooth communication recently. These devices are smart enough but do not have any software on Linux. Unfortunately, the existing Android applications have the same interfaces as the devices themself. But it would be great to have a logger of my works with these devices that collect and store data from them, which I will analyze later with some standard tool like Grafana. Ideally, I want to switch on my Raspberry Pi only before a job with a USB logger starts. And store all data that the USB tester interface displays.
So let's go to work.
## Main steps
* [Create an image for RaspberryPi](doc/rpi.md)
* [Install and configure InfluxDB](doc/influxdb.md)
* Install and configure loggers