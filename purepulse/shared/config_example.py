import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Get current environment
ENV = os.getenv("ENV", "dev").lower()

##########################################################################
##
##
## Request Configuration
##
##
##########################################################################

# Optional: default timeouts, headers, retries
DEFAULT_REQUEST_TIMEOUT = os.getenv("REQUEST_TIMEOUT", 10)
DEFAULT_HEADERS = {
    "Content-Type": "application/json"
}

##########################################################################
##
##
## purpleAir parameters
##
##
##########################################################################

purpleAir = {
    # The api read keys. Each key will be used for max_requests_per_key (see below) requests
    'key': os.getenv("PURPLEAIR_API_KEY"),

    # Maximum number of requests allowed per key
    'max_requests_per_key': os.getenv("PURPLEAIR_MAX_REQUESTS_PER_KEY", 900),

    # Default date from which we will start getting data for each sensor. In YYYY-MM-DD HH:mm:ss format
    'start_timestamp': os.getenv("PURPLEAIR_START_TIMESTAMP", "2021-01-01 00:00:00"),

    # Batch days for each request. How many days will be included in each request? Values: 1-14. Higher days mean fewer requests.
    'batch_days': 14,

    # Parameters related to get sensor history request.
    # https://api.purpleair.com/#api-sensors-get-sensor-history
    'request': {}
}

##########################################################################
##
##
## wunderground parameters
##
##
##########################################################################

wunderground = {
    # Your API key
    'key': os.getenv("WUNDERGROUND_API_KEY"),

    # Default date from which we will start getting data for each station. In YYYY-mm-dd format
    'start_date': os.getenv("WUNDERGROUND_START_DATE", "2023-03-22"),

    # 'm' for Metric units, 'e' for Imperial (English) units
    'units': os.getenv("WUNDERGROUND_UNITS", "m"),

    # Default history mode (--history parameter). Select from ['hourly', 'daily', 'all'].
    # Leave the array empty for no default history mode.
    # More info about history fields at: https://docs.google.com/document/d/1w8jbqfAk0tfZS5P7hYnar1JiitM0gQZB-clxDfG3aD0/edit
    'history': os.getenv("WUNDERGROUND_HISTORY", []),

    # Default forecast hourly days mode (--forcast-hourly parameter). Select from: ['1day', '2day', '3day', '10day', '15day'].
    # Leave the array empty for no default hourly forecasts
    # More info about forecast fields at: https://docs.google.com/document/d/1_Zte7-SdOjnzBttb1-Y9e0Wgl0_3tah9dSwXUyEA3-c/edit
    'forecast_hourly': os.getenv("WUNDERGROUND_FORECAST_HOURLY", []),

    # Allow new forecast values after N hours of the last request. This helps us avoid unwanted duplicates in our forecast csvs
    'forecast_hourly_hour_span': os.getenv("WUNDERGROUND_FORECAST_HOURLY_HOUR_SPAN", 24)
}

##########################################################################
##
##
## Wunderground Stations and PurpleAir Sensors
##
##
##########################################################################

devices = {}

##########################################################################
##
##
## CSV storage directories
##
##
##########################################################################

# The directories structure are:
# DATA_DIR/:location/WEATHER_DIR
# DATA_DIR/:location/PM_DIR
#
# :location as defined in devices.keys()

# The main storage directory
DATA_DIR = ''

# Directory for each location's weather data. DATA_DIR/:location/WEATHER_DIR. e.g. data/athens/weather
WEATHER_DIR = ''

# Directory for each location's pm data. DATA_DIR/:location/PM_DIR e.g. data/athens/pm
PM_DIR = ''

TIMESCALE_URL=os.getenv("TIMESCALE_URL")

KAFKA_ZOOKEEPER_CLIENT_PORT=os.getenv("KAFKA_ZOOKEEPER_CLIENT_PORT")
KAFKA_ZOOKEEPER_CONNECT=os.getenv("KAFKA_ZOOKEEPER_CONNECT")
KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=os.getenv("KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR")
KAFKA_BOOTSTRAP_SERVERS=os.getenv("KAFKA_BOOTSTRAP_SERVERS")
