from app.controllers.wunderground_controller import WundergroundController
from fastapi import APIRouter
from app.form_requests.wunderground_request import WundergroundRequest

router = APIRouter()
wunderground_controller = WundergroundController()

@router.post("/wunderground")
async def extract_wunderground_route(req: WundergroundRequest) -> dict:
    return await wunderground_controller.extract_wunderground(req)
