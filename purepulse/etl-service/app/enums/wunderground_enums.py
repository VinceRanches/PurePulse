from enum import Enum

class UnitsEnum(str, Enum):
    metric = "m"
    imperial = "e"

class HistoryModeEnum(str, Enum):
    hourly = "hourly"
    daily = "daily"
    all = "all"

class ForecastModeEnum(str, Enum):
    day1 = "1day"
    day2 = "2day"
    day3 = "3day"
    day5 = "5day"
    day10 = "10day"
    day15 = "15day"
