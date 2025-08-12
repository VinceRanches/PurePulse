from app.form_requests.purpleair_request import PurpleAirRequest
from app.services.purpleair_service import PurpleAirService


class PurpleAirController:

    def __init__(self):
        self.purpleair_service = PurpleAirService()


    async def extract_purpleair(self, req: PurpleAirRequest) -> dict:
        return await self.purpleair_service.fetch_purpleair_data(
            locations=req.locations,
            start=req.start,
            end=req.end
        )
