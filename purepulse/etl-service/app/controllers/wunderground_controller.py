from app.form_requests.wunderground_request import WundergroundRequest
from app.services.wunderground_service import WundergroundService

class WundergroundController:

    def __init__(self):
        self.wunderground_service = WundergroundService()


    async def extract_wunderground(self, req: WundergroundRequest) -> dict:
        return self.wunderground_service.fetch_wunderground_data(
            locations=req.locations,
            history_modes=req.history,
            forecast_modes=req.forecast_hourly,
            units_list=req.units,
            start=req.start,
            end=req.end
        )
