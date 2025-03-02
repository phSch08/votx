import json
import os

from fastapi import (
    APIRouter,
    Depends,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from votx.security import get_logged_in_user

from ..helpers.data import socket_manager

templates = Jinja2Templates(directory="votx/templates")
router = APIRouter(
    prefix="/beamer",
    tags=["beamer"],
    dependencies=[Depends(get_logged_in_user)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_class=HTMLResponse)
def get_admin(request: Request) -> HTMLResponse:
    print(os.environ.get("URL"))
    return templates.TemplateResponse(
        request=request,
        name="beamer.jinja",
        context={"displayURL": os.environ.get("URL")},
    )


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await socket_manager.connect_beamer(websocket)
    try:
        while True:
            try:
                message = await websocket.receive_json()
                print("Received Data via Websocket:", message)

            except (json.JSONDecodeError, KeyError):
                print("Failed to parse Message")
    except WebSocketDisconnect:
        socket_manager.disconnect_beamer(websocket)
