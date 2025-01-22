import json
import traceback
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from peewee import DoesNotExist

from ..db_models import Ballot, UserVote, Vote, VoteOption, VoterToken, db
from ..helpers.data import get_user_ballots, socket_manager, update_beamer_vote_count
from ..models import VoteData
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
def vote_screen(
    request: Request, voter_token: Annotated[str, Depends(get_voter_token_from_jwt)]
):
    try:
        VoterToken.get(VoterToken.token == voter_token)
    except DoesNotExist:
        response = RedirectResponse(url="/")
        response.delete_cookie("voter_token")
        return response

    return templates.TemplateResponse(request=request, name="vote.jinja")


@router.get("/logout")
async def logout(response: Response):
    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="voter_token")
    return response


async def vote(vote: VoteData, token: VoterToken) -> tuple[bool, str]:
    try:
        ballot = Ballot.get_by_id(vote.ballot_id)
        registration_token = token.registration_token
    except DoesNotExist:
        return (False, "Ballot does not exist!")

    if not ballot.active:
        return (False, "Ballot is not active!")

    # check if vote is possible
    if (
        UserVote.select()
        .where((UserVote.voter == registration_token) & (UserVote.ballot == ballot))
        .exists()
    ):
        return (False, "Already voted for this ballot!")

    # Check if VoteOption Ids match with ballot
    if not (
        set(vote.votes)
        <= set(map(lambda vote_option: vote_option.id, ballot.voteOptions))
    ):
        return (False, "Voteoption ids do not match ballot!")

    # check if vote is correct
    if len(vote.votes) > ballot.maximum_votes or len(vote.votes) < ballot.minimum_votes:
        return (
            False,
            "The number of given votes does not match the expected number of votes!",
        )

    # check for vote stacking
    if len(vote.votes) != len(set(vote.votes)) and not ballot.vote_stacking:
        return (False, "Vote Stacking is not allowed!")

    if len(vote.custom_id) != 12:
        return (False, "The custom ID must consist of exactly 12 characters")

    # perform vote and mark as voted
    try:
        with db.atomic():
            for vote_option in vote.votes:
                Vote.create(
                    vote_option=VoteOption.get_by_id(vote_option),
                    custom_id=vote.custom_id,
                )
            UserVote.create(voter=registration_token, ballot=ballot)
    except Exception:
        return (False, "Failure while Voting!")

    await update_beamer_vote_count(ballot)
    return (True, "Vote Successful")


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, voter_token: Annotated[str, Depends(get_voter_token_from_jwt)]
):
    try:
        token = VoterToken.get(VoterToken.token == voter_token)
    except DoesNotExist as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Voter Token"
        ) from e

    await socket_manager.connect_voter(websocket, token.token)

    try:
        await websocket.send_json({"type": "AUTHENTICATED"})

        while True:
            try:
                message = await websocket.receive_json()

                if message["type"] == "GETBALLOTS":
                    await websocket.send_json(
                        {"type": "BALLOTS", "data": get_user_ballots(voter_token)}
                    )

                if message["type"] == "VOTE":
                    vote_data = VoteData.model_validate(message["data"])
                    vote_result = await vote(vote_data, token)
                    await websocket.send_json(
                        {"type": "VOTERESULT", "data": {"success": vote_result[0]}}
                    )
                    await websocket.send_json(
                        {"type": "BALLOTS", "data": get_user_ballots(voter_token)}
                    )

            except (json.JSONDecodeError, KeyError):
                print("Failed to parse Message")
                print(traceback.format_exc())
    except WebSocketDisconnect:
        socket_manager.disconnect_voter(websocket)
