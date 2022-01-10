from influxdb_tool.datapoint import Datapoint
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from typing import List
import logging


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
