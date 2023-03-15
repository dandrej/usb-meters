from flightsql import FlightSQLClient

query = """SELECT *
FROM 'census'
WHERE time >= now() - interval '24 hours'
AND ('bees' IS NOT NULL OR 'ants' IS NOT NULL)"""

# Define the query client
#query_client = FlightSQLClient(
#  host = "eu-central-1-1.aws.cloud2.influxdata.com",
#  token = 'xCfUBsIwxIfe1B223eTzkYa-ATrZh5G0ZZ2XqxkhvH5zo9E0I4P9BLpOC76xjv_RG8-brhwSLL4GHHpD1h7BMg==', #os.environ.get("INFLUXDB_TOKEN"),
#  metadata={"bucket-name": "home-test"})

query_client = FlightSQLClient(
  host = "http://localhost:8086",
  token = '3SMiB5ksX8rCB2zJE19hkz0goeav-pZiWMBJcft1k5PsWGB7DyxPv1r8qK-PwDxcZSfNP16XlT22ldCkd8kurg==', #os.environ.get("INFLUXDB_TOKEN"),
  metadata={"bucket-name": "test"})


# Execute the query
info = query_client.execute(query)
reader = query_client.do_get(info.endpoints[0].ticket)

# Convert to dataframe
data = reader.read_all()
df = data.to_pandas().sort_values(by="time")
print(df)
