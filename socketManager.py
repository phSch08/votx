from fastapi import WebSocket
from typing import Callable

class SocketManager:
    def __init__(self):
        self.active_connections: dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = ""

    def disconnect(self, websocket: WebSocket):
        del self.active_connections[websocket]

    def register_access_code(self, websocket, access_code):
        self.active_connections[websocket] = access_code

    async def broadcast(self, message: str):
        for websocket in self.active_connections:
            await websocket.send_text(message)

    async def broadcast_func(self, func: Callable[[str], list]):
        for websocket, access_code in self.active_connections.items():
            await websocket.send_json(func(access_code))
