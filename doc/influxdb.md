# Install and configure InfluxDB
In general see [official guide](https://docs.influxdata.com/influxdb/v2.6/install/?t=Raspberry+Pi)
I use this guide on my Raspberry Pi 3 despite the official recomendation using "a Raspberry Pi 4+ or 400"

## Install InfluxDB as a service with systemd
From [here](https://docs.influxdata.com/influxdb/v2.6/install/?t=Linux#install-influxdb-as-a-service-with-systemd)
-   Download and install the appropriate `.deb` file using a URL from the [InfluxData downloads page](https://portal.influxdata.com/downloads/) with the following commands:

    ```sh
    # influxdata-archive_compat.key GPG fingerprint:
    #     9D53 9D90 D332 8DC7 D6C8 D3B9 D8FF 8E1F 7DF8 B07E
    wget -q https://repos.influxdata.com/influxdata-archive_compat.key
    echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && cat influxdata-archive_compat.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null
    echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list

    sudo apt-get update && sudo apt-get install influxdb2
    ```

-   Start the InfluxDB service:

    ```sh
    sudo service influxdb start
    ```

    Installing the InfluxDB package creates a service file at `/lib/systemd/system/influxdb.service` to start InfluxDB as a background service on startup.

-   Restart your system and verify that the service is running correctly:

    ```
    $  sudo service influxdb status
    ● influxdb.service - InfluxDB is an open-source, distributed, time series database
      Loaded: loaded (/lib/systemd/system/influxdb.service; enabled; vendor preset: enable>
      Active: active (running)
    ```

## Set up InfluxDB through the UI
From [here](https://docs.influxdata.com/influxdb/v2.6/install/?t=Linux#set-up-influxdb-through-the-ui)
1.  With InfluxDB running, visit http://usbmeters.local:8086 from desktop.
2.  Click **Get Started**

### [Set up your initial user](https://docs.influxdata.com/influxdb/v2.6/install/?t=Linux#set-up-your-initial-user)

1.  Enter a **Username** for your initial user.
2.  Enter a **Password** and **Confirm Password** for your user.
3.  Enter your initial **Organization Name**.
4.  Enter your initial **Bucket Name**.
5.  Click **Continue**.

Your InfluxDB instance is now initialized.

## Additional setup for usb meters

### Get an API token

- Visit http://usbmeters.local:8086 from desktop.
- Navigate to `Load Data -> API Tokens`
- Press `+ GENERATE API TOKEN` button and `All Access API Token`
- Enter token description and click `Save`
- Store token to `ble-config.yml` as described in [Software](software.md)

### Add additional bucket
- Navigate to `Load Data -> Buckets`
- Press `+ CREATE BUCKET` button
- Enter bucket name. (I use `ble-meters` as the bucket name)
- Press `OLDER THAN` button and choose where the old data will be deleted from database. (I choose `72 hours`)
- Store the bucket name to `ble-config.yml` as described in [Software](software.md)
