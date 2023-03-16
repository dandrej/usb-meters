# Create an image for RaspberryPi
In general see [Official guide](https://www.raspberrypi.com/software/)
I have documented my steps to create an image for my RPI 3 below.
## Install rpi-imager
For Ubuntu
``` bash
sudo apt install rpi-imager
```
For Fedora
``` bash
sudo dnf install rpi-imager
```
## Flash SD card
1. Run `rpi-imager`
2. Click "Choose OS" button
3. Choose Raspberry Pi OS (other) -> Raspberry Pi OS Lite (64-bit)
4. Insert an SD card to write the image to.
5. Click "Choose Storage" button
6. Select the SD card inserted in step 4
7. Click "Write" button
8. The image will be written on an SD card
9. Insert keyboard, monitor, and SD card into Raspberry Pi
10. Power on the RPI
11. Finish the setup by following the prompts

## Post setup steps

### Check your BLE device
Check device name (`hci0` for RaspberryPi 3)
```bash
hcitool dev
```
Scan BLE devices available
```bash
sudo hcitool -i hci0 lescan
```
### Change host name
```bash
sudo hostnamectl set-hostname usbmeters
systemctl reboot
```
After that it will be possible to ssh in this device as `ssh usbmeters.local` and access the local InfluxDB instance (after installation) through `http://usbmeters.local:8086`

### Install pip package
```bash
sudo apt-get install python3-pip
```
