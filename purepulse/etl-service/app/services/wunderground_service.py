import math
import os
from datetime import datetime, date, timedelta
from io import StringIO
from typing import Dict, List, Optional

import pandas as pd
import requests
from app.enums.wunderground_enums import UnitsEnum, HistoryModeEnum, ForecastModeEnum
from app.helpers.csv_helper import CsvHelper
from requests.exceptions import HTTPError, RequestException
from shared import config

DATETIME_NOW = datetime.now()
DATE_NOW = DATETIME_NOW.date()

REQUEST_HISTORY_URL = 'https://api.weather.com/v2/pws/history/:mode'
REQUEST_FORECAST_HOURLY_URL = 'https://api.weather.com/v3/wx/forecast/hourly/:mode'
URL_DATE_FORMAT = '%Y%m%d'
KEY = config.wunderground['key']

HISTORY_CSV_TIMESTAMP_COL = 'obsTimeUtc'
HISTORY_CSV_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
FORECAST_TIMESTAMP_COL = 'validTimeLocal'
FORECAST_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
FORECAST_HOURLY_HOUR_SPAN = config.wunderground['forecast_hourly_hour_span']

class WundergroundService:

    @staticmethod
    def fetch_wunderground_data(
        locations: List[str],
        history_modes: List[HistoryModeEnum],
        forecast_modes: List[ForecastModeEnum],
        units_list: List[UnitsEnum],
        start: Optional[date] = None,
        end: Optional[date] = None
    ) -> Dict:
        """
        Fetch data from Wunderground API for specified locations, modes, and units.

        Args:
            locations: List of location names to fetch data for.
            history_modes: List of history modes (e.g., hourly, daily).
            forecast_modes: List of forecast modes (e.g., 1day, 5day).
            units_list: List of units (metric, imperial).
            start: Start date for data fetching (optional).
            end: End date for data fetching (optional).

        Returns:
            Dict containing:
                - status: HTTP status code (200 for success, 206 for partial success, 400 for config errors, 500 for server errors).
                - data: List of data sources (e.g., [{"source": "Wunderground"}]).
                - errors: List of error details (station, location, mode, units, error message).

        Raises:
            ValueError: If an invalid location or configuration is provided.
            RuntimeError: If data fetching fails completely.
        """
        errors, processed = [], []
        try:
            start_date_default = datetime.strptime(config.wunderground['start_date'], '%Y-%m-%d').date()
            start_date = start or start_date_default
            end_date = end or DATE_NOW

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

                for station_config in config.devices[location]['stations']:
                    station = Station(
                        location=location,
                        station_id=station_config['id'],
                        geocode=station_config['geocode']
                    )
                    try:
                        # History
                        for mode in history_modes:
                            for unit in units_list:
                                try:
                                    csv = CsvHelper(
                                        station.get_csv_filepath(
                                            arg_type='history',
                                            mode=mode.value,
                                            units=unit.value
                                        )
                                    )
                                    csv.create_file()
                                    last_date = csv.get_last_date(column=HISTORY_CSV_TIMESTAMP_COL, datetime_format=HISTORY_CSV_TIMESTAMP_FORMAT)
                                    start_date = start or last_date or start_date
                                    station.get_history_data(
                                        start_date=start_date,
                                        end_date=end_date,
                                        mode=mode,
                                        units=unit,
                                        csv=csv
                                    )
                                    if last_date and start_date < last_date:
                                        csv.sort(HISTORY_CSV_TIMESTAMP_COL)
                                except Exception as e:
                                    errors.append({
                                        "station": station.id,
                                        "location": location,
                                        "mode": mode.value,
                                        "units": unit.value,
                                        "error": str(e)
                                    })

                        # Forecast
                        for mode in forecast_modes:
                            for unit in units_list:
                                try:
                                    csv = CsvHelper(
                                        station.get_csv_filepath(
                                            arg_type='forecast_hourly',
                                            mode=mode.value,
                                            units=unit.value
                                        )
                                    )
                                    csv.create_file()
                                    last_ref_dt = csv.get_last_datetime(column='referenceDatetimeLocal', datetime_format=FORECAST_TIMESTAMP_FORMAT)
                                    if (last_ref_dt and DATETIME_NOW.replace(tzinfo=last_ref_dt.tzinfo)
                                            <= last_ref_dt + timedelta(hours=FORECAST_HOURLY_HOUR_SPAN)):
                                        continue
                                    station.get_forecast_hourly_data(
                                        mode=mode,
                                        units=unit,
                                        csv=csv
                                    )
                                    csv.sort(FORECAST_TIMESTAMP_COL)
                                except Exception as e:
                                    errors.append({
                                        "station": station.id,
                                        "location": location,
                                        "mode": mode.value,
                                        "units": unit.value,
                                        "error": str(e)
                                    })
                    except Exception as e:
                        errors.append({
                            "station": station.id,
                            "location": location,
                            "error": f"Failed to process station: {str(e)}"
                        })

                    processed.append({"location": location, "station": station.id})

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


class Station:
    def __init__(
        self,
        location: str,
        station_id: str,
        geocode: str
    ) -> None:
        """
        Initialize a Station instance.

        Args:
            location: The location name of the station.
            station_id: The station ID.
            geocode: The geocode for the station.

        Raises:
            ValueError: If location, station_id, or geocode is invalid.
        """
        if not location or not station_id or not geocode:
            raise ValueError("Location, station_id, and geocode must be non-empty strings")
        self.location: str = location
        self.id: str = station_id
        self.geocode: str = geocode
        self.csv_filepath: str = os.path.abspath(
            os.path.join(os.path.dirname(__file__),
            "../../data",
            location,
            config.WEATHER_DIR,
            station_id,
            ":type_:mode_:units.csv")
        )
        os.makedirs(name=os.path.dirname(self.csv_filepath), exist_ok=True)


    def get_csv_filepath(
        self,
        arg_type: str,
        mode: str,
        units: str
    ) -> str:
        """
        Generate the CSV file path for the given type, mode, and units.

        Args:
            arg_type: Type of data (e.g., history, forecast_hourly).
            mode: Mode of data (e.g., hourly, daily).
            units: Units of data (e.g., metric, imperial).

        Returns:
            The file path for the CSV.
        """
        return self.csv_filepath.replace(':type', arg_type).replace(':mode', mode).replace(':units', units)


    def get_history_data(
        self,
        start_date: date,
        end_date: date,
        mode: HistoryModeEnum,
        units: UnitsEnum,
        csv: CsvHelper
    ) -> None:
        """
        Fetch and process history data for the specified date range, mode, and units.

        Args:
            start_date: Start date for data fetching.
            end_date: End date for data fetching.
            mode: History mode (e.g., hourly, daily).
            units: Units of data (metric, imperial).
            csv: CsvHelper instance for handling CSV operations.

        Raises:
            HTTPError: If the API request fails.
            RequestException: For network-related errors.
            RuntimeError: For other processing errors.
        """
        batch = timedelta(days=config.wunderground.get('batch_days', 7))  # Batch processing
        interval = end_date - start_date

        for _ in range(math.ceil(interval.days / batch.days)):
            batch_start = start_date + batch * _
            batch_end = min(batch_start + batch - timedelta(days=1), end_date)

            for day_offset in range((batch_end - batch_start).days + 1):
                date_param = batch_start + timedelta(days=day_offset)
                try:
                    response = requests.get(
                        url=REQUEST_HISTORY_URL.replace(':mode', mode.value),
                        params={
                            'stationId': self.id,
                            'format': 'json',
                            'units': units.value,
                            'date': date_param.strftime(URL_DATE_FORMAT),
                            'apiKey': KEY,
                            'numericPrecision': 'decimal'
                        }
                    )
                    response.raise_for_status()

                    if response.status_code == 204:
                        continue
                    df = pd.json_normalize(response.json(), 'observations')
                    if not df.empty:
                        df.columns = df.columns.str.replace(self.units_text(units), '', regex=False)
                        df = csv.remove_existing_rows_from_df(df=df, column=HISTORY_CSV_TIMESTAMP_COL)
                        df.to_csv(
                            path_or_buf=csv.file_path,
                            mode='a',
                            index=False,
                            header=csv.is_empty()
                        )
                except HTTPError as e:
                    raise HTTPError(f"HTTP error for station {self.id} on {date_param}: {str(e)}")
                except RequestException as e:
                    raise RequestException(f"Network error for station {self.id} on {date_param}: {str(e)}")
                except Exception as e:
                    raise RuntimeError(f"Error fetching history for station {self.id} on {date_param}: {str(e)}")


    def get_forecast_hourly_data(
        self,
        mode: ForecastModeEnum,
        units: UnitsEnum,
        csv: CsvHelper
    ) -> None:
        """
        Fetch and process hourly forecast data for the specified mode and units.

        Args:
            mode: Forecast mode (e.g., 1day, 5day).
            units: Units of data (metric, imperial).
            csv: CsvHelper instance for handling CSV operations.

        Raises:
            HTTPError: If the API request fails.
            RequestException: For network-related errors.
            RuntimeError: For other processing errors.
        """
        try:
            response = requests.get(
                url=REQUEST_FORECAST_HOURLY_URL.replace(':mode', mode.value),
                params={
                    'geocode': self.geocode,
                    'format': 'json',
                    'units': units.value,
                    'language': 'en',
                    'apiKey': KEY
                }
            )
            response.raise_for_status()

            df = pd.read_json(StringIO(response.text))
            col_index = df.columns.get_loc('validTimeLocal')
            df.insert(col_index, 'referenceDatetimeLocal', df['validTimeLocal'][0])
            df = csv.remove_existing_rows_from_df(df=df, column=FORECAST_TIMESTAMP_COL)
            df.to_csv(
                path_or_buf=csv.file_path,
                mode='a',
                index=True,
                header=csv.is_empty()
            )
        except HTTPError as e:
            raise HTTPError(f"HTTP error for station {self.id}: {str(e)}")
        except RequestException as e:
            raise RequestException(f"Network error for station {self.id}: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error fetching forecast for station {self.id}: {str(e)}")


    @staticmethod
    def units_text(units: UnitsEnum) -> str:
        """
        Get the text representation of units.

        Args:
            units: Units enum (metric, imperial).

        Returns:
            String representation of units.
        """
        return 'metric' if units == UnitsEnum.metric else 'imperial'
