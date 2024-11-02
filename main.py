from typing import Tuple, Annotated
from fastapi import Depends, FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from peewee import DoesNotExist, Case, fn
from .dbModels import Ballot, Vote, VoteOption, db, AccessCode
from .Models import AccessCodeCreationData, BallotData, Token, VoteData

import uvicorn
import jwt
from jwt.exceptions import InvalidTokenError
import json
import secrets
import datetime
import time

from .helpers import broadcast_user_ballots, get_user_ballots, toDictBallotData, toPydanticBallotData, socketManager
from .routers import admin, login

import logging
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init("votix.sqlite")
    db.connect()
    db.create_tables([AccessCode, Ballot, VoteOption, Vote])
    yield
    db.close()

app = FastAPI(lifespan=lifespan, host='0.0.0.0')
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(login.router)
app.include_router(admin.router)

@app.get("/{accessCode}", response_class=HTMLResponse)
def index(request: Request, accessCode: str):
    return templates.TemplateResponse(request=request, name="index.jinja", context={"accessCode": accessCode})



@app.post("/accessCodes/")
def generateAccessCodes(accessCodeCreationData: AccessCodeCreationData) -> list[str]:
    new_codes = []
    while len(set(map(lambda x: x['code'], new_codes))) < accessCodeCreationData.amount:
        new_codes.append({'code': secrets.token_hex(64), 'issueDate': datetime.datetime.now()})

    with db.atomic():
        AccessCode.insert_many(new_codes).execute()

    return map(lambda x: x['code'], new_codes)

@app.get("/ballot/")
def getBallots() -> list[BallotData]:
    return map(toPydanticBallotData, Ballot.select())

def vote(vote: VoteData) -> Tuple[bool, str]:
    print(vote)
    try:
        ballot = Ballot.get_by_id(vote.ballotId)
        accessCode = AccessCode.get(AccessCode.code == vote.accessCode)
    except DoesNotExist:
        return (False, "Voting for this Ballot is not permitted!")


    if (not ballot.active):
        return (False, "Voting for this Ballot is not permitted!")

    # check if vote is possible
    if (Vote.select().where(
        (Vote.voter == accessCode) &
        (Vote.ballot == ballot)
        ).exists()):
        return (False, "Voting for this Ballot is not permitted!")
    
    # Check if VoteOption Ids match with ballot
    if not (set(vote.votes) <=  set(map(lambda voteOption: voteOption.id, ballot.voteOptions))):
        return (False, "Voting for this Ballot is not permitted!")

    # check if vote is correct
    if (len(vote.votes) > ballot.maximumVotes and len(vote.votes) < ballot.minimumVotes):
        return (False, "The number of given votes does not match the expected number of votes!")

    # check for vote stacking
    if len(vote.votes) != len(set(vote.votes)) and ballot.voteStacking == False:
        return (False, "Vote Stacking is not allowed!")

    # perform vote and mark as voted
    try:
        with db.atomic():
            for voteOption in vote.votes:
                query = VoteOption.update(voteCount = VoteOption.voteCount +1).where(VoteOption.id == voteOption)
                query.execute()
            Vote.create(voter = accessCode, ballot = ballot)
    except:
        return (False, "Failure while Voting!")
    return (True, "Vote Successful")


   

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    async def send_ballots(user_id):
        await websocket.send_json({
            'type': 'BALLOTS', 
            'data': list(map(toDictBallotData, get_user_ballots(user_id)))})
        
    await socketManager.connect(websocket)
    try:
        while True:
            try:
                message = await websocket.receive_json()
                print("Received Data via Websocket:", message)
                if (message["type"] == "AUTHENTICATE"):
                    if (AccessCode.select().where(AccessCode.code == message["data"]).exists()):
                        socketManager.register_access_code(websocket, message["data"])
                        await websocket.send_json({'type': 'AUTHENTICATED'})

                if (message["type"] == "GETBALLOTS"):
                    await send_ballots(message["data"])

                if (message["type"] == "VOTE"):
                    time.sleep(3)
                    voteData = VoteData.model_validate(message["data"])
                    voteResult = vote(voteData)
                    #time.sleep(5)
                    await websocket.send_json({'type': 'VOTERESULT', 'data': {'success': voteResult[0]}})
                    await send_ballots(voteData.accessCode)

            except (json.JSONDecodeError, KeyError):
                print("Failed to parse Message")
    except WebSocketDisconnect:
        socketManager.disconnect(websocket)

    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)