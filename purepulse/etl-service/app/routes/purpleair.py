from app.controllers.purpleair_controller import PurpleAirController
from fastapi import APIRouter
from app.form_requests.purpleair_request import PurpleAirRequest

router = APIRouter()
purpleair_controller = PurpleAirController()

@router.post("/purpleair")
async def extract_purpleair_route(req: PurpleAirRequest) -> dict:
    return await purpleair_controller.extract_purpleair(req)
