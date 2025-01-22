import datetime
import json
import os
import secrets
import string
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from peewee import fn

from votx.exceptions import ballot_protexted_exception, invalid_ballot_configuration

from ..db_models import (
    Ballot,
    BallotProtocol,
    BallotVoteGroup,
    RegistrationToken,
    VoteGroup,
    VoteGroupMembership,
    VoteOption,
    db,
)
from ..helpers.data import broadcast_user_ballots, socket_manager
from ..helpers.pdf_generator import generate_ballot_protocol, generate_registration_pdf
from ..models import (
    BaseBallotData,
    BeamerTextData,
    RegistrationTokenCreationData,
    RegistrationTokenResetData,
    VoteGroupCreationData,
    VoteGroupDeletionData,
)
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
def get_admin(
    request: Request,
    response: Response,
    user_name: Annotated[str, Depends(get_logged_in_user)],
    ballot: int | None = None,
    danger: bool | None = None,
) -> HTMLResponse:
    selected_ballot = Ballot.get_or_none(Ballot.id == ballot)

    response = templates.TemplateResponse(
        request=request,
        name="admin.jinja",
        context={
            "user_name": user_name,
            "ballots": Ballot.select(),
            "access_code_count": RegistrationToken.select().count(),
            "selected_ballot": selected_ballot,
            "vote_groups": VoteGroup.select(
                VoteGroup,
                fn.EXISTS(
                    BallotVoteGroup.select().where(
                        (BallotVoteGroup.ballot == selected_ballot)
                        & (BallotVoteGroup.votegroup == VoteGroup.id)
                    )
                ).alias("is_selected"),
            ),
            "danger_mode": danger,
        },
    )
    expiry_time = (
        int(os.environ.get("ADMIN_TOKEN_EXPIRY"))
        if "ADMIN_TOKEN_EXPIRY" in os.environ
        else 20
    )
    response.set_cookie(
        key="session_token",
        value=create_access_token({"sub": user_name}, expiry_time),
        secure=True,
        httponly=True,
    )

    return response


@router.get("/logout")
async def logout(response: Response):
    response = RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="session_token")
    return response


@router.post("/votegroup")
async def create_vote_group(creation_data: VoteGroupCreationData) -> None:
    vote_group = VoteGroup(title=creation_data.title)
    vote_group.save()


@router.delete("/votegroup")
async def delete_vote_group(deletion_data: VoteGroupDeletionData) -> None:
    VoteGroup.delete_by_id(deletion_data.id)


@router.post("/beamer/text")
async def set_beamer_text(text_data: BeamerTextData) -> None:
    await socket_manager.broadcast_beamer(
        json.dumps({"type": "SETTEXT", "data": text_data.text})
    )


@router.post("/ballot/{id}/activate")
async def activate_ballot(id: int) -> None:
    ballot = Ballot.get_by_id(id)
    ballot.active = True
    ballot.save()
    BallotProtocol.create(ballot=ballot, message="Wahlgang gestartet")
    await broadcast_user_ballots()


@router.post("/ballot/{id}/deactivate")
async def deactivate_ballot(id: int) -> None:
    ballot = Ballot.get_by_id(id)
    ballot.active = False
    ballot.save()
    BallotProtocol.create(
        ballot=ballot, message=f"Wahlgang gestoppt, {len(ballot.votes)} Stimme(n)"
    )
    await broadcast_user_ballots()


@router.post("/ballot/{id}/focus")
async def focus_ballot(id: int) -> None:
    ballot = Ballot.get_by_id(id)
    await socket_manager.broadcast_beamer(
        json.dumps(
            {
                "type": "SETVOTE",
                "data": {
                    "voteTitle": ballot.title,
                    "voteCount": len(ballot.votes),
                    "voteOptions": [{"title": vo.title} for vo in ballot.voteOptions],
                },
            }
        )
    )


@router.post("/ballot/{id}/result")
async def show_result(id: int) -> None:
    ballot = Ballot.get_by_id(id)
    await socket_manager.broadcast_beamer(
        json.dumps(
            {
                "type": "SETRESULT",
                "data": {
                    "voteTitle": ballot.title,
                    "voteCount": len(ballot.votes),
                    "voteOptions": [
                        {"title": vo.title, "votes": len(vo.votes)}
                        for vo in ballot.voteOptions
                    ],
                },
            }
        )
    )


@router.get("/ballot/{id}/protocol")
def get_ballot_protocol(id: int):
    ballot = Ballot.get_by_id(id)
    vote_options = ballot.voteOptions
    votes = [vote for vo in vote_options for vote in vo.votes]

    pdf = generate_ballot_protocol(
        ballot.title,
        [(vo.title, len(vo.votes)) for vo in vote_options],
        [(ev.timestamp, ev.message) for ev in ballot.protocol],
        sorted(
            [(v.vote_option.title, v.custom_id) for v in votes],
            key=lambda el: el[1].lower(),
        ),
    )

    headers = {"Content-Disposition": 'inline; filename="registration_sheets.pdf"'}
    return Response(bytes(pdf.output()), media_type="application/pdf", headers=headers)


@router.get("/registrationTokens/")
def get_registration_tokens():
    tokens = RegistrationToken.select()

    pdf = generate_registration_pdf(
        "Wahlschein",
        "DLRG Vollversammlung",
        "15.03.2025",
        "Ihr Wahlcode",
        os.environ.get("URL"),
        [
            (t.token, [membership.voteGroup.title for membership in t.memberships])
            for t in tokens
        ],
    )

    headers = {"Content-Disposition": 'inline; filename="registration_sheets.pdf"'}
    return Response(bytes(pdf.output()), media_type="application/pdf", headers=headers)


@router.post("/registrationToken/reset")
def reset_registration_token(reset_data: RegistrationTokenResetData):
    registration_token = RegistrationToken.get(
        RegistrationToken.token == reset_data.token
    )
    for voter_token in registration_token.voterToken:
        voter_token.delete_instance()


@router.post("/registrationTokens/")
def generate_registration_tokens(
    access_code_creation_data: RegistrationTokenCreationData,
):
    with db.atomic():
        for i in range(access_code_creation_data.amount):
            secret = "".join(secrets.choice(string.digits) for i in range(15))
            splitted_secret = " - ".join([secret[i : i + 5] for i in range(3)])
            token = RegistrationToken(
                token=splitted_secret, issueDate=datetime.datetime.now()
            )
            token.save()

            VoteGroupMembership.insert_many(
                [
                    {"voteGroup": vg, "registrationToken": token}
                    for vg in access_code_creation_data.vote_groups
                ]
            ).execute()


@router.post("/ballot/")
async def create_ballot(ballot_data: BaseBallotData) -> int:
    if ballot_data.id:
        ballot, _ = Ballot.get_or_create(
            id=ballot_data.id, defaults={"title": ballot_data.title}
        )
    else:
        ballot = Ballot()

    # do not allow changes if votes for the ballot exist
    if len(ballot.votes) > 0:
        raise ballot_protexted_exception(
            "The ballot cannot be changed as there are already existing votes!"
        )

    if ballot.active:
        raise ballot_protexted_exception(
            "The ballot cannot be changed as it is currently active!"
        )

    if min(ballot_data.maximum_votes, ballot_data.minimum_votes) < 1:
        raise invalid_ballot_configuration(
            "The number of minimum- or maximum votes cannot be lower than 1!"
        )

    ballot.title = ballot_data.title
    ballot.maximum_votes = max(ballot_data.maximum_votes, ballot_data.minimum_votes)
    ballot.minimum_votes = min(ballot_data.maximum_votes, ballot_data.minimum_votes)
    ballot.vote_stacking = ballot_data.vote_stacking
    ballot.active = ballot_data.active
    ballot.save()

    for vo_idx, vote_option in enumerate(ballot_data.vote_options):
        option, new_created = VoteOption.get_or_create(
            ballot=ballot.id, optionIndex=vo_idx, defaults={"title": vote_option}
        )
        if not new_created:
            option.title = vote_option
        option.save()

    VoteOption.delete().where(
        (VoteOption.ballot == ballot.id)
        & (VoteOption.option_index >= len(ballot_data.vote_options))
    ).execute()

    print(ballot_data.vote_groups)
    BallotVoteGroup.delete().where(
        (BallotVoteGroup.ballot == ballot)
        & (BallotVoteGroup.votegroup.not_in(ballot_data.vote_groups))
    ).execute()

    for vg in ballot_data.vote_groups:
        BallotVoteGroup.get_or_create(ballot=ballot, votegroup=VoteGroup.get_by_id(vg))

    if ballot_data.active:
        await broadcast_user_ballots()

    return ballot.id
