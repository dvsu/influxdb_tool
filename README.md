# influxdb-tool

A class wrapper that simplifies interaction with InfluxDB 2.0+

## Introduction

The `influx_database.py` consists of 2 main classes, `Datapoint` and `InfluxDatabase`.  
`Datapoint` is the main data class that is used to construct our data before writing data into InfluxDB using a method in `InfluxDatabase` class.

## Dependencies

```shell
pip3 install influxdb-client
```

## How to Use

Assuming that we have the following project structure

```none
.
├── ...
│   ├── ...
│   ├── ...
│   └── ...
├── influxdb_tool
│   └── influx_database.py
├── config.py
└── main.py
```

and InfluxDB details are stored in `config.py`

> ***Note:***  
> All InfluxDB details can be obtained/ set up via InfluxDB UI.  
> If InfluxDB is installed correctly and the service is running, the UI can be accessed at `{IP_ADDRESS}:8086`

```python
TOKEN="example_token"
ORG="my_org"
BUCKET="my_bucket"
IP_ADDRESS="123.234.45.67"
```

Hence, we can initialize our `InfluxDatabase` class as shown below.

```python
from influxdb_tool.influx_database import InfluxDatabase, Datapoint

influx_db = InfluxDatabase(
    token=config.TOKEN,
    org=config.ORG,
    bucket=config.BUCKET,
    ipaddress=config.IP_ADDRESS)
```

To construct a `Datapoint`

```python
Datapoint(
    measurement="measurement_name",
    time="time_in_ISO_8601_format",
    fields={
        value1: 12.34,
        value2: 23.45,
        value3: 34.56    
    },
    tags={
        "tag1": "tag1_value",
        "tag2": "tag2_value"
    }
)
```

There are two main methods that can be used to write data to database

```python
write_single_datapoint(datapoint: Datapoint)
write_bulk_datapoints(datapoints: List[Datapoint])
```

## Example

We would like to analyze the environmental condition in our server room. Our IT members install 2 sensor nodes at different location inside the server room. Let say the names of the data received from our equipment are `server_data_1` and `server_data_2` respectively. Each equipment (sensor node) is identical and consists of three sensors.

```python
server_data_1 = {
    "equipment_name": "office_server_01",
    "equipment_serial_number": "A1B2C3D4E5",
    "sensors": [
        {
            "sensor_name": "TS11",
            "sensor_serial_number": "A12345",
            "type": "temperature_sensor",
            "value": 23.45,
            "measurement_unit": "celsius"
        },
        {
            "sensor_name": "HS12",
            "sensor_serial_number": "A67890",
            "type": "humidity_sensor",
            "value": 51.23,
            "measurement_unit": "percent"
        },
        {
            "sensor_name": "FS13",
            "sensor_serial_number": "A35791",
            "type": "air_flow_sensor",
            "value": 0.679,
            "measurement_unit": "m/s"
        },
    ],
    "timestamp": 1625484644
}

server_data_2 = {
    "equipment_name": "office_server_02",
    "equipment_serial_number": "P6Q7R8S9T0",
    "sensors": [
        {
            "sensor_name": "TS11",
            "sensor_serial_number": "A56790",
            "type": "temperature_sensor",
            "value": 24.12,
            "measurement_unit": "celsius"
        },
        {
            "sensor_name": "HS12",
            "sensor_serial_number": "A21334",
            "type": "humidity_sensor",
            "value": 49.76,
            "measurement_unit": "percent"
        },
        {
            "sensor_name": "FS13",
            "sensor_serial_number": "A43572",
            "type": "air_flow_sensor",
            "value": 0.572,
            "measurement_unit": "m/s"
        },
    ],
    "timestamp": 1625484925
}
```

There are a few scenarios to structure our data. The most common is either:

1. Each `equipment` is stored in a separate `measurement`. Inside each `measurement`, there are `fields` which contain sensor values and `tags` which store equipment and sensor unique IDs, ***or***
2. Each `sensor` is stored in a separate `measurement`. Inside each `measurement`, there are `fields` which contain values of identical sensor from various `equipment`.

Back to our main problem why we install these sensor nodes in our server room. We probably want to answer questions, such as

1. What is the current temperature inside our server room?  
2. Our server becomes quite warm. Do we have good air flow inside the room?
3. The lifetime of our server is somewhat shorter than expected. What is the root cause of the problem?

In this case, point 2 is a more viable solution, because it reduces the complexity of our data structure and is much easier to profile the environmental condition by grouping it into a single measurement per sensor type.  

The full example is as below.

```python
from influxdb_tool.influx_database import InfluxDatabase, Datapoint
from datetime import datetime
import config


def write_data_to_database(raw_data: dict):

    datapoints = []

    for sensor in raw_data["sensors"]:
        datapoints.append(Datapoint(
            measurement=sensor["type"],
            time=datetime.utcfromtimestamp(
                int(raw_data["timestamp"])).strftime("%Y-%m-%dT%H:%M:%SZ"),
            fields={
                "value": sensor["value"]
            },
            tags={
                "equipment_name": raw_data["equipment_name"],
                "equipment_serial_number": raw_data["equipment_serial_number"],
                "sensor_name": sensor["sensor_name"],
                "sensor_serial_number": sensor["sensor_serial_number"],
                "measurement_unit": sensor["measurement_unit"],
            }
        ))

    influx_db.write_bulk_datapoints(datapoints)


influx_db = InfluxDatabase(
    token=config.TOKEN,
    org=config.ORG,
    bucket=config.BUCKET,
    ipaddress=config.IP_ADDRESS
)

# ...
# assuming the received sensor data is handled continuously in the background 
# ...

write_data_to_database(server_data_1)
write_data_to_database(server_data_2)
```
