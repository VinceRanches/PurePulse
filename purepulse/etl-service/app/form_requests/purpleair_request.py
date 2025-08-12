from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PurpleAirRequest(BaseModel):
    locations: List[str] = ["patras"]
    start: Optional[datetime] = None
    end: Optional[datetime] = None