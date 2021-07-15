from influx_database import InfluxDatabase
from datapoint import Datapoint
from datetime import datetime
import configparser


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


config = configparser.ConfigParser()
config.read('config.ini')

influx_db = InfluxDatabase(
    token=config['influxdb']['token'],
    org=config['influxdb']['org'],
    bucket=config['influxdb']['bucket'],
    ipaddress=config['influxdb']['ip_address']
)

# Let say we receive sensor data from our equipment
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


write_data_to_database(server_data_1)
write_data_to_database(server_data_2)
