from typing import Annotated
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..Models import BallotData

from ..helpers import broadcast_user_ballots

from ..dbModels import AccessCode, Ballot, VoteOption

from ..security import get_logged_in_user

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_logged_in_user)],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def get_admin(request: Request, response: Response, user_name: Annotated[str, Depends(get_logged_in_user)], ballot: int | None = None) -> HTMLResponse:
    selected_ballot = Ballot.get_or_none(Ballot.id == ballot)
    return templates.TemplateResponse(
        request=request,
        name="admin.jinja",
        context={
            "user_name": user_name,
            "ballots": Ballot.select(),
            "access_code_count": AccessCode.select().count(),
            "selected_ballot": selected_ballot
            })

@router.post("/ballot/{id}/activate")
async def activateBallot(id: int) -> None:
    ballot = Ballot.get_by_id(id)
    ballot.active = True
    ballot.save()
    await broadcast_user_ballots()

    
    
@router.post("/ballot/{id}/deactivate") 
async def deactivateBallot(id: int) -> None:
    ballot = Ballot.get_by_id(id)
    ballot.active = False
    ballot.save()
    await broadcast_user_ballots()

@router.post("/ballot/")
async def createBallot(ballotData: BallotData) -> int:
    if ballotData.id:
        ballot, _ = Ballot.get_or_create(id=ballotData.id, defaults={"title": ballotData.title})
    else:
        ballot = Ballot()

    ballot.title = ballotData.title
    ballot.maximumVotes = ballotData.maximumVotes
    ballot.minimumVotes = ballotData.minimumVotes
    ballot.voteStacking = ballotData.voteStacking
    ballot.active = ballotData.active
    ballot.save()

    if (ballotData):
        for vo_idx, vote_option in enumerate(ballotData.voteOptions):
            option, _ = VoteOption.get_or_create(ballot=ballot.id, optionIndex=vo_idx, defaults={"title": ballotData.title})
            option.title = vote_option
            option.save()

        VoteOption.delete().where((VoteOption.ballot == ballot.id) & (VoteOption.optionIndex >=  len(ballotData.voteOptions))).execute()

    if (ballotData.active):
        await broadcast_user_ballots()

    return ballot.id