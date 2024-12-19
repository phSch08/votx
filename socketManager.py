from fastapi import WebSocket
from typing import Callable

class SocketManager:
    def __init__(self):
        self.active_voters: dict[WebSocket, str] = {}
        self.active_beamers: list[WebSocket] = []

    async def connect_voter(self, websocket: WebSocket, voter_token: str):
        await websocket.accept()
        self.active_voters[websocket] = voter_token
        
    async def connect_beamer(self, websocket: WebSocket):
        await websocket.accept()
        self.active_beamers.append(websocket)
        print(len(self.active_beamers))

    def disconnect_voter(self, websocket: WebSocket):
        del self.active_voters[websocket]
        
    def disconnect_beamer(self, websocket: WebSocket):
        self.active_beamers.remove(websocket)

    def register_access_code(self, websocket, access_code):
        self.active_voters[websocket] = access_code

    async def broadcast(self, message: str):
        for websocket in self.active_voters:
            await websocket.send_text(message)
            
    async def broadcast_beamer(self, message: str):
        print(message)
        for websocket in self.active_beamers:
            await websocket.send_text(message)

    async def broadcast_func(self, func: Callable[[str], list]):
        for websocket, voter_token in self.active_voters.items():
            await websocket.send_json(func(voter_token))
