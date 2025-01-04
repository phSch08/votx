import datetime
from functools import cmp_to_key
import json
import locale
import os
import secrets
import string
from peewee import Case, JOIN, fn
from typing import Annotated
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from votx.exceptions import BallotProtectedException

from ..helpers.pdfGenerator import generateBallotProtocol, generateRegistrationPDF

from ..Models import BallotData, BaseBallotData, BeamerTextData, RegistrationTokenCreationData, RegistrationTokenResetData, VoteGroupCreationData, VoteGroupDeletionData

from ..helpers.data import broadcast_user_ballots, socketManager

from ..dbModels import BallotProtocol, BallotVoteGroup, RegistrationToken, Ballot, VoteGroup, VoteGroupMembership, VoteOption, VoterToken, db

from ..security import create_access_token, get_logged_in_user

templates = Jinja2Templates(directory="votx/templates")

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_logged_in_user)],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def get_admin(request: Request, response: Response, user_name: Annotated[str, Depends(get_logged_in_user)], ballot: int | None = None, danger: bool | None = None) -> HTMLResponse:
    selected_ballot = Ballot.get_or_none(Ballot.id == ballot)

    response = templates.TemplateResponse(
        request=request,
        name="admin.jinja",
        context={
            "user_name": user_name,
            "ballots": Ballot.select(),
            "access_code_count": RegistrationToken.select().count(),
            "selected_ballot": selected_ballot,
            "vote_groups": VoteGroup.select(VoteGroup, fn.EXISTS(BallotVoteGroup
                                                                 .select()
                                                                 .where((BallotVoteGroup.ballot == selected_ballot) &
                                                                        (BallotVoteGroup.votegroup == VoteGroup.id)))
                                            .alias("is_selected")),
            "danger_mode": danger == True
        })
    expiry_time = int(os.environ.get('ADMIN_TOKEN_EXPIRY')
                      ) if 'ADMIN_TOKEN_EXPIRY' in os.environ else 20
    response.set_cookie(key="session_token",
                        value=create_access_token(
                            {"sub": user_name}, expiry_time),
                        secure=True,
                        httponly=True)

    return response


@router.get("/logout")
async def logout(response: Response):
    response = RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="session_token")
    return response


@router.post("/votegroup")
async def createVoteGroup(creationData: VoteGroupCreationData) -> None:
    voteGroup = VoteGroup(title=creationData.title)
    voteGroup.save()


@router.delete("/votegroup")
async def deleteVoteGroup(deletionData: VoteGroupDeletionData) -> None:
    VoteGroup.delete_by_id(deletionData.id)


@router.post("/beamer/text")
async def beamerText(textData: BeamerTextData) -> None:
    await socketManager.broadcast_beamer(
        json.dumps({
            "type": "SETTEXT",
            "data": textData.text
        })
    )


@router.post("/ballot/{id}/activate")
async def activateBallot(id: int) -> None:
    ballot = Ballot.get_by_id(id)
    ballot.active = True
    ballot.save()
    BallotProtocol.create(ballot=ballot, message="Wahlgang gestartet")
    await broadcast_user_ballots()


@router.post("/ballot/{id}/deactivate")
async def deactivateBallot(id: int) -> None:
    ballot = Ballot.get_by_id(id)
    ballot.active = False
    ballot.save()
    BallotProtocol.create(ballot=ballot, message=f"Wahlgang gestoppt, {
                          len(ballot.votes)} Stimme(n)")
    await broadcast_user_ballots()


@router.post("/ballot/{id}/focus")
async def focusBallot(id: int) -> None:
    ballot = Ballot.get_by_id(id)
    await socketManager.broadcast_beamer(
        json.dumps({
            "type": "SETVOTE",
            "data": {
                "voteTitle": ballot.title,
                "voteCount": len(ballot.votes),
                "voteOptions": [{"title": vo.title} for vo in ballot.voteOptions]
            }
        })
    )


@router.post("/ballot/{id}/result")
async def showResult(id: int) -> None:
    ballot = Ballot.get_by_id(id)
    await socketManager.broadcast_beamer(
        json.dumps({
            "type": "SETRESULT",
            "data": {
                "voteTitle": ballot.title,
                "voteCount": len(ballot.votes),
                "voteOptions": [{"title": vo.title, "votes": len(vo.votes)} for vo in ballot.voteOptions]
            }
        })
    )


@router.get("/ballot/{id}/protocol")
def getBallotProtocol(id: int):
    ballot = Ballot.get_by_id(id)
    voteOptions = ballot.voteOptions
    votes = [vote for vo in voteOptions for vote in vo.votes]

    pdf = generateBallotProtocol(
        ballot.title,
        [(vo.title, len(vo.votes)) for vo in voteOptions],
        [(ev.timestamp, ev.message) for ev in ballot.protocol],
        sorted([(v.vote_option.title, v.custom_id) for v in votes], key=lambda el: el[1].lower()))

    headers = {'Content-Disposition': 'inline; filename="registration_sheets.pdf"'}
    return Response(bytes(pdf.output()), media_type='application/pdf', headers=headers)


@router.get("/registrationTokens/")
def getRegistrationTokens():
    tokens = RegistrationToken.select()

    pdf = generateRegistrationPDF(
        "Wahlschein",
        "DLRG Vollversammlung",
        "15.03.2025",
        "Ihr Wahlcode",
        os.environ.get('URL'),
        [(t.token, [membership.voteGroup.title for membership in t.memberships])
         for t in tokens]
    )

    headers = {'Content-Disposition': 'inline; filename="registration_sheets.pdf"'}
    return Response(bytes(pdf.output()), media_type='application/pdf', headers=headers)


@router.post("/registrationToken/reset")
def resetRegistrationToken(resetData: RegistrationTokenResetData):
    registrationToken = RegistrationToken.get(
        RegistrationToken.token == resetData.token)
    for voterToken in registrationToken.voterToken:
        voterToken.delete_instance()


@ router.post("/registrationTokens/")
def generateRegistrationTokens(
    accessCodeCreationData: RegistrationTokenCreationData
):
    with db.atomic():
        for i in range(accessCodeCreationData.amount):
            secret = ''.join(secrets.choice(string.digits) for i in range(15))
            splitted_secret = ' - '.join([secret[i: i+5] for i in range(3)])
            token = RegistrationToken(
                token=splitted_secret, issueDate=datetime.datetime.now())
            token.save()

            VoteGroupMembership.insert_many(
                [{'voteGroup': vg, 'registrationToken': token} for vg in accessCodeCreationData.voteGroups]).execute()


@ router.post("/ballot/")
async def createBallot(ballotData: BaseBallotData) -> int:
    if ballotData.id:
        ballot, _ = Ballot.get_or_create(id=ballotData.id, defaults={
            "title": ballotData.title})
    else:
        ballot = Ballot()

    # do not allow changes if votes for the ballot exist
    if len(ballot.votes) > 0:
        raise BallotProtectedException(
            "The ballot cannot be changed as there are already existing votes!")

    if ballot.active:
        raise BallotProtectedException(
            "The ballot cannot be changed as it is currently active!")

    ballot.title = ballotData.title
    ballot.maximumVotes = ballotData.maximumVotes
    ballot.minimumVotes = ballotData.minimumVotes
    ballot.voteStacking = ballotData.voteStacking
    ballot.active = ballotData.active
    ballot.save()

    for vo_idx, vote_option in enumerate(ballotData.voteOptions):
        option, new_created = VoteOption.get_or_create(
            ballot=ballot.id, optionIndex=vo_idx, defaults={"title": vote_option})
        if not new_created:
            option.title = vote_option
        option.save()

    VoteOption.delete().where((VoteOption.ballot == ballot.id) & (
        VoteOption.optionIndex >= len(ballotData.voteOptions))).execute()

    print(ballotData.voteGroups)
    BallotVoteGroup.delete().where((BallotVoteGroup.ballot == ballot) &
                                   (BallotVoteGroup.votegroup.not_in(ballotData.voteGroups))).execute()

    for vg in ballotData.voteGroups:
        BallotVoteGroup.get_or_create(
            ballot=ballot, votegroup=VoteGroup.get_by_id(vg))

    if (ballotData.active):
        await broadcast_user_ballots()

    return ballot.id
