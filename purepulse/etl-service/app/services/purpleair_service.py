import math
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
from app.helpers.csv_helper import CsvHelper
from app.helpers.request_helper import get_request

from shared import config

MAX_REQUESTS: int = config.purpleAir['max_requests_per_key']
KEY = config.purpleAir['key']
REQUEST_PARAMS = {
    "headers": {"X-API-Key": KEY},
    "url": "https://api.purpleair.com/v1/sensors/:sensor/history",
    "datetime_format": '%Y-%m-%dT%H:%M:%SZ'
}
AVERAGE_MINS: int = config.purpleAir['request']['average']
PM_DIR: str = config.PM_DIR
CSV_TIMESTAMP_COL: str = 'time_stamp'
START_TIMESTAMP: str = config.purpleAir['start_timestamp']
BATCH_DAYS: int = config.purpleAir['batch_days']


class PurpleAirService:

    @staticmethod
    async def fetch_purpleair_data(
        locations: List[str],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> Dict:
        """
        Fetch data from PurpleAir sensors for specified locations and time range.

        Args:
            locations: List of location names to fetch data for
            start: Start datetime for data fetching (optional)
            end: End datetime for data fetching (optional)

        Returns:
            Dictionary containing:
                - status: HTTP status code (200 for success, 206 for partial success, 400 for config errors)
                - data: List of data sources (empty on failure)
                - errors: List of error details (sensor, location, error message)

        Raises:
            ValueError: If invalid location or configuration is provided
            RuntimeError: If data fetching fails completely
        """
        errors, processed = [], []
        try:
            now = datetime.now().replace(
                minute=0,
                second=0,
                microsecond=0
            )
            start_timestamp = start or datetime.strptime(START_TIMESTAMP, '%Y-%m-%d %H:%M:%S')
            end_timestamp = end or now

            if not locations:
                errors.append({"error": "Locations list cannot be empty"})
                return {
                    "status": 400,
                    "data": processed,
                    "errors": errors
                }

            for location in locations:
                if location not in config.devices:
                    errors.append({"error": f"Invalid location: {location}"})
                    return {
                        "status": 400,
                        "data": processed,
                        "errors": errors
                    }

                for sensor_index in config.devices[location]['sensors']:
                    try:
                        sensor = Sensor(location=location, index=sensor_index)
                        csv = CsvHelper(sensor.csv_filepath)
                        csv.create_file()

                        last_timestamp = csv.get_last_datetime(
                            column=CSV_TIMESTAMP_COL,
                            datetime_format=REQUEST_PARAMS['datetime_format']
                        )
                        if last_timestamp:
                            start_timestamp = start or last_timestamp + timedelta(minutes=AVERAGE_MINS)

                        await sensor.get_data(
                            start_timestamp=start_timestamp,
                            end_timestamp=end_timestamp,
                            csv=csv
                        )

                        processed.append({"location": location, "sensor": sensor_index})

                    except Exception as e:
                        print(f"Error processing sensor {sensor_index} at {location}: {str(e)}")
                        errors.append({
                            "sensor": sensor_index,
                            "location": location,
                            "error": str(e)
                        })
                        continue

            return {
                "status": 200 if not errors else 206,
                "data": processed,
                "errors": errors
            }

        except ValueError as ve:
            errors.append({"error": f"Configuration error: {str(ve)}"})
            return {
                "status": 400,
                "data": processed,
                "errors": errors
            }
        except Exception as e:
            errors.append({"error": f"Failed to fetch data: {str(e)}"})
            return {
                "status": 500,
                "data": processed,
                "errors": errors
            }


class Counter:
    total_requests: int = 0
    key_requests: int = 0


class Sensor:
    def __init__(
        self,
        location: str,
        index: int
    ) -> None:
        """
        Initialize a Sensor instance.

        Args:
            location: The location name of the sensor
            index: The sensor index number

        Raises:
            ValueError: If location or index is invalid
        """
        if not location or not isinstance(index, int):
            raise ValueError("Location must be a non-empty string and index must be an integer")

        self.location: str = location
        self.index: int = index
        self.url: str = REQUEST_PARAMS["url"].replace(':sensor', str(index))
        self.csv_filepath: str = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../data",
                location,
                PM_DIR,
                f"{index}.csv",
            )
        )
        os.makedirs(name=os.path.dirname(self.csv_filepath), exist_ok=True)


    async def get_data(
        self,
        start_timestamp: datetime,
        end_timestamp: datetime,
        csv: CsvHelper
    ) -> None:
        """
        Fetch and process sensor data for the specified time range.

        Args:
            start_timestamp: Start datetime for data fetching
            end_timestamp: End datetime for data fetching
            csv: CsvHelper instance for handling CSV operations

        Raises:
            HTTPError: If the API request fails
            RequestException: For network-related errors
            ValueError: For invalid data or configuration
        """
        try:
            batch = timedelta(days=BATCH_DAYS)
            interval = end_timestamp - start_timestamp

            for _ in range(math.ceil(interval / batch)):
                start_date_param = start_timestamp + batch * _
                end_date_tmp = start_date_param + batch
                end_date_param = end_date_tmp if end_date_tmp < end_timestamp else end_timestamp

                try:
                    response = await get_request(
                        endpoint=self.url,
                        params={
                            'start_timestamp': start_date_param.strftime(REQUEST_PARAMS["datetime_format"]),
                            'end_timestamp': end_date_param.strftime(REQUEST_PARAMS["datetime_format"]),
                            'average': AVERAGE_MINS,
                            'fields': ','.join(config.purpleAir['request']['fields'])
                        },
                        headers=REQUEST_PARAMS["headers"]
                    )

                    if response['status'] != 200:
                        print(f"Request failed for sensor {self.index}: {response.get('error', 'Unknown error')}")
                        continue

                    Counter.total_requests += 1
                    Counter.key_requests += 1

                    response_df = pd.DataFrame(response['data']['data'], columns=response['data']['fields'])
                    response_df = csv.remove_existing_rows_from_df(df=response_df, column=CSV_TIMESTAMP_COL)
                    response_df.sort_values(by=[CSV_TIMESTAMP_COL], inplace=True)
                    response_df.to_csv(
                        path_or_buf=csv.file_path,
                        mode='a',
                        index=False,
                        header=csv.is_empty()
                    )

                    if Counter.key_requests >= MAX_REQUESTS:
                        try:
                            time.sleep(3)
                            Counter.key_requests = 0
                        except StopIteration:
                            raise ValueError("No more API keys available")

                except Exception as e:
                    print(f"Error processing request for sensor {self.index}: {str(e)}")
                    continue

        except Exception as e:
            raise RuntimeError(f"Failed to process sensor data for sensor {self.index}: {str(e)}")
