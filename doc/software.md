# Software
## Install
```bash
git clone https://github.com/dandrej/usb-meters.git
cd usb-meters
pip install -r ble/requirements.txt
```
## Configure
Bluetooth usb meters tested:
- Atorch AT24
- Atorch DT24TW

Configuration file `ble-config.yml`.

The file has to be placed in:
- `/etc`
- `~/.config`
- `meters.py` script directory
- current directory

### Choose a right device
The `device` key of the configuration file contains information about the devices the script working with.

The subkey `names` contains the list of device names.

The subkey `services` limits the device discovery to a list of services. Now only '0000ffe0-0000-1000-8000-00805f9b34fb' service for ATorch devices is supported.

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
The logging key of the configuration file contains the logging configuration parameters. The subkeys of this key are logging levels: `critical`, `error`, `warning`, `info`, and `debug`. The subkeys of the logging levels may be script modules names `storage`, `scanner`, `client`, and `protocols`

## Run
```bash
python ble/meters.py
```