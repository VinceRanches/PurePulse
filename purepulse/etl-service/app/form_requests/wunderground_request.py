from datetime import date
from typing import List, Optional

from app.enums.wunderground_enums import UnitsEnum, HistoryModeEnum, ForecastModeEnum
from pydantic import BaseModel


class WundergroundRequest(BaseModel):
    locations: List[str] = ["patras"]
    history: List[HistoryModeEnum]
    forecast_hourly: List[ForecastModeEnum]
    units: List[UnitsEnum] = ["m"]
    start: Optional[date] = date(2023, 3, 22)
    end: Optional[date] = None
