#export INFLUXDB_TOKEN=xCfUBsIwxIfe1B223eTzkYa-ATrZh5G0ZZ2XqxkhvH5zo9E0I4P9BLpOC76xjv_RG8-brhwSLL4GHHpD1h7BMg==
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime

#token = 'xCfUBsIwxIfe1B223eTzkYa-ATrZh5G0ZZ2XqxkhvH5zo9E0I4P9BLpOC76xjv_RG8-brhwSLL4GHHpD1h7BMg==' #os.environ.get("INFLUXDB_TOKEN")
#org = "test"
#url = "https://eu-central-1-1.aws.cloud2.influxdata.com"
token = '3SMiB5ksX8rCB2zJE19hkz0goeav-pZiWMBJcft1k5PsWGB7DyxPv1r8qK-PwDxcZSfNP16XlT22ldCkd8kurg=='
org = "drovalev"
url = "http://localhost:8086"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

bucket="meters"

# Define the write api
write_api = write_client.write_api(write_options=SYNCHRONOUS)

data = {
  "point1": {
    "location": "Klamath",
    "species": "bees",
    "count": 23,
  },
  "point2": {
    "location": "Portland",
    "species": "ants",
    "count": 30,
  },
  "point3": {
    "location": "Klamath",
    "species": "bees",
    "count": 28,
  },
  "point4": {
    "location": "Portland",
    "species": "ants",
    "count": 32,
  },
  "point5": {
    "location": "Klamath",
    "species": "bees",
    "count": 29,
  },
  "point6": {
    "location": "Portland",
    "species": "ants",
    "count": 40,
  },
}

#for key in data:
#  point = (
#    Point("census")
#    .tag("location", data[key]["location"])
#    .field(data[key]["species"], data[key]["count"])
#  )
#  write_api.write(bucket=bucket, org=org, record=point)
#  time.sleep(1) # separate points by 1 second
#write_api.write(bucket=bucket, org=org, record='fnirsi voltage=0.14658 1678037896316534000')
point = (
    Point("fnirsi").field("voltage", 0.14880).time(datetime.datetime.utcnow())
)
print(point.to_line_protocol())
write_api.write(bucket=bucket, org=org, record=point)
time.sleep(1)

print("Complete. Return to the InfluxDB UI.")
