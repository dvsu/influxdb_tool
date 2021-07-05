from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from typing import Dict, List, Any
from datetime import datetime
import logging
import sys


class Datapoint:

    def __init__(self, measurement: str, time: str, fields: Dict[str, Any], tags: Dict[str, str] = None):
        """
        ```
        (required) measurement: str
        ```
            Name of measurement, equivalent to table in SQL

        ```
        (required) time: str
        ```
            UTC time in ISO 8601 format `YYYY-mm-ddTHH:MM:SSZ`, e.g. `"2021-12-23T01:23:45Z"`\n
        ```
            datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            datetime.utcfromtimestamp(int(epoch_time)).strftime("%Y-%m-%dT%H:%M:%SZ")
        ```
        ```
        (required) fields: dict
        ```
            Key-value pairs which consist of metric names and values. Typically, values type should be `float`

            Example:
        ```
            {
                "temperature": 23.456,
                "humidity": 50.12,
                "system_load": 12.34
            }
        ```
        ```
        (optional) tags: dict
        ```
            Optional, but very useful when performing data queries

            Example:
        ```
            {
                "device_serial_number": "A1B2C3D4E5F6",
                "device_type": "sensor"
            }
        ```
        """

        try:
            if type(measurement) != str:
                raise TypeError("'measurement' must be in 'str'")

            if type(time) != str:
                raise TypeError("'time' must be in 'str'")

            if not self.__time_check(time):
                raise ValueError(
                    "'time' must be in `YYYY-mm-ddTHH:MM:SSZ` format")

            if type(fields) != dict:
                raise TypeError("'fields' must be in 'dict'")

            if not fields:
                raise ValueError("'fields' must not be empty")

            for elem_type in list(map(lambda x: type(x), fields.keys())):
                if elem_type != str:
                    raise KeyError("'key' of fields must be in 'str'")

            if type(tags) != dict or tags != None:
                pass

        except (TypeError, ValueError, KeyError) as e:
            print(f"{type(e).__name__}: {e}")
            sys.exit(1)

        self.measurement = measurement
        self.tags = tags
        self.time = time
        self.fields = fields

    def __time_check(self, time: str) -> None:

        try:
            datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
            return True

        except ValueError as e:
            print(
                f"{type(e).__name__}: {e}")
            return False


class InfluxDatabase:

    def __init__(self, token: str, org: str, bucket: str, ipaddress: str, logger: str = None):
        self.logger = None
        if logger:
            self.logger = logging.getLogger(logger)
        self.__token = token
        self.__org = org
        self.__bucket = bucket
        self.__ipaddress = ipaddress
        self.__client = InfluxDBClient(
            url=f"http://{self.__ipaddress}:8086", token=self.__token)
        self.__write_api = self.__client.write_api(write_options=SYNCHRONOUS)

        if self.logger:
            self.logger.info("InfluxDatabase class initialized")
        else:
            print("InfluxDatabase class initialized")

    def _generate_list_of_datapoints(self, data: List[Datapoint]) -> list:

        return [{
                "measurement": item.measurement,
                "tags": item.tags,
                "time": item.time,
                "fields": item.fields
                } for item in data]

    def write_single_datapoint(self, datapoint: Datapoint) -> None:
        try:
            self.__write_api.write(
                self.__bucket,
                self.__org,
                self._generate_list_of_datapoints(datapoint)
            )

        except Exception as e:
            if self.logger:
                self.logger.warning(
                    f"{type(e).__name__}: Unable to write datapoints\n{e}")
            else:
                print(f"{type(e).__name__}: Unable to write datapoints\n{e}")

    def write_bulk_datapoints(self, datapoints: List[Datapoint]) -> None:
        try:
            self.__write_api.write(
                self.__bucket,
                self.__org,
                self._generate_list_of_datapoints(datapoints))

        except Exception as e:
            if self.logger:
                self.logger.warning(
                    f"{type(e).__name__}: Unable to write datapoints\n{e}")
            else:
                print(f"{type(e).__name__}: Unable to write datapoints\n{e}")
