import json
import traceback
from typing import Annotated, Tuple
from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from peewee import DoesNotExist

from ..helpers import get_user_ballots, socketManager, updateBeamerVoteCount

from ..Models import VoteData
from ..dbModels import Ballot, UserVote, Vote, VoteOption, VoterToken, db

from ..security import get_voter_token_from_jwt


templates = Jinja2Templates(directory="votx/templates")

router = APIRouter(
    prefix="/vote",
    tags=["vote"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def voteScreen(request: Request,  voter_token: Annotated[str, Depends(get_voter_token_from_jwt)]):
    try:
        token = VoterToken.get(VoterToken.token == voter_token)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Voter Token"
        )
        
    return templates.TemplateResponse(request=request, name="vote.jinja")

async def vote(vote: VoteData, token: VoterToken) -> Tuple[bool, str]:
    try:
        ballot = Ballot.get_by_id(vote.ballotId)
        registrationToken = token.registrationToken
    except DoesNotExist:
        return (False, "Ballot does not exist!")


    if (not ballot.active):
        return (False, "Ballot is not active!")

    # check if vote is possible
    if (UserVote.select().where(
        (UserVote.voter == registrationToken) &
        (UserVote.ballot == ballot)
        ).exists()):
        return (False, "Already voted for this ballot!")
    
    # Check if VoteOption Ids match with ballot
    if not (set(vote.votes) <=  set(map(lambda voteOption: voteOption.id, ballot.voteOptions))):
        return (False, "Voteoption ids do not match ballot!")

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
                Vote.create(vote_option = VoteOption.get_by_id(voteOption), custom_id = "")
            UserVote.create(voter = registrationToken, ballot = ballot)
    except:
        return (False, "Failure while Voting!")
    
    await updateBeamerVoteCount(ballot)
    return (True, "Vote Successful")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, voter_token: Annotated[str, Depends(get_voter_token_from_jwt)]):        
    try:
        token = VoterToken.get(VoterToken.token == voter_token)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Voter Token"
        )

    await socketManager.connect_voter(websocket, token.token)
    
    try:
        await websocket.send_json({'type': 'AUTHENTICATED'})
        
        while True:
            try:
                message = await websocket.receive_json()

                if (message["type"] == "GETBALLOTS"):
                    await websocket.send_json({
                        'type': 'BALLOTS', 
                        'data': get_user_ballots(voter_token)
                    })

                if (message["type"] == "VOTE"):
                    voteData = VoteData.model_validate(message["data"])
                    voteResult = await vote(voteData, token)
                    await websocket.send_json({'type': 'VOTERESULT', 'data': {'success': voteResult[0]}})
                    await websocket.send_json({
                        'type': 'BALLOTS', 
                        'data': get_user_ballots(voter_token)
                    })
                    
            except (json.JSONDecodeError, KeyError):
                print("Failed to parse Message")
                print(traceback.format_exc())
    except WebSocketDisconnect:
        socketManager.disconnect_voter(websocket)

    
