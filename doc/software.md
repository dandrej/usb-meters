# Software (Bluetooth)
## Install
```bash
git clone https://github.com/dandrej/usb-meters.git
cd usb-meters
pip install -r ble/requirements.txt
```
## Configure
Bluetooth devices tested:
- Atorch UD24 https://www.aliexpress.com/item/1005001483503811.html
- Atorch DT24TW https://www.aliexpress.com/item/1005003948599629.html
- Atorch AT24CB https://www.aliexpress.com/item/1005002474832237.html
- Atorch DL24M-H https://www.aliexpress.com/item/1005003474912240.html
- XiaoXiang BMS

Configuration file `ble-config.yml`.

The file has to be placed in:
- `/etc`
- `~/.config`
- `meters.py` script directory
- current directory

### Choose a right device
The `device` key of the configuration file contains information about the devices the script working with.
Subkeys are the device types. There are three types supported at the moment:
- `atorch`
- `rnirsi`
- `xiaoxiang`
The types subkeys are the names of the handled devices.

### Choose the data output
The `storage` key of the configuration file contains information about output configurations and current output.

The `type` subkey contains the current output type. It may be `influxdb`, `csv`, or `console` output.

The `console` subkey contains the configuration of the console output. The only subkey `type` is available in this configuration. This subkey has the only value `pretty`

The `csv` subkey contains the configuration of output to CSV formatted file.
| Key | Description |
|---- | ----------- |
|`path`| Set the directory name where CSV files will be stored to. |
|`is_zip`| The boolean value whether or not the output file will be gzipped.|
|`kwarg`| Any additional argument of the [csv.DictWriter class constructor](https://docs.python.org/3.11/library/csv.html?highlight=csv%20dictwriter#csv.DictWriter) which is used to create CSV. One of the useful arguments is `dialect` argument which specifies the dialect of CSV file.|

The `influxdb` subkey contains the configuration of output to the InfluxDB database.
| Required Keys | Description |
|---- | ----------- |
|`url`| The url of the database connection. If the database is installed on the same computer that this script is running it may be `http://localhost:8086`|
|`org`| Organization name that has been configured during [IndluxDB installation](influxdb.md)  |
|`token`| Access token value that has been configured during [IndluxDB installation](influxdb.md)|
|`bucket`|Bucket name that has been configured during [IndluxDB installation](influxdb.md)|

### Logging
The logging key of the configuration file contains the logging configuration parameters. The subkeys of this key are logging levels: `critical`, `error`, `warning`, `info`, and `debug`. The subkeys of the logging levels may be script modules names `storage`, `scanner`, `client`, `atorch`, and `xiaoxiang`

## Run
```bash
python ble/meters.py
```

# Software (USB)
Unfortunately, I do not find how to connect to FNIRSI USB meter through Bluetooth. But I found a way of such a connection through USB. This set of scripts works automatically when the meter is connected to PC by its PC micro usb port.
## Edit config file
Open `usb-config.yml` and edit its `storage` section as described above in the section 'Choose the right data output'
## Install required files
``` bash
./usb-install.bash
```
## Connect the device
Connect the micro usb cable to the device PC port and another side of this cable to the desktop USB port. The installed udev rule launches the `fnirsi` systemd service and the data recording starts. Check the service availability by typing
``` bash
systemctl status fnirsi
```
_Notes:_ This script does not work on my Raspberry Pi 3, due to some timeouts in USB transfers. May be due to pure power or a bad USB cable. I will check it later. But the script works perfectly in my notebook.