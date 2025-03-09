import logging
import os
import secrets
from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn
from fastapi import Cookie, Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from peewee import DoesNotExist

from .db_models import (
    Ballot,
    BallotProtocol,
    BallotVoteGroup,
    RegistrationToken,
    UserVote,
    Vote,
    VoteGroup,
    VoteGroupMembership,
    VoteOption,
    VoterToken,
    db,
)
from .exceptions.admin_unauthorized_exception import AdminUnauthorizedException
from .exceptions.voter_unauthorized_exception import VoterUnauthorizedException
from .models import TokenData
from .routers import admin, beamer, vote
from .security import (
    check_password,
    create_access_token,
    create_voter_jwt,
    get_voter_token_from_jwt,
)

logger = logging.getLogger("peewee")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init(os.environ.get("POSTGRES_DB"))
    db.connect()
    db.create_tables(
        [
            RegistrationToken,
            VoterToken,
            VoteGroup,
            VoteGroupMembership,
            Ballot,
            VoteOption,
            UserVote,
            Vote,
            BallotVoteGroup,
            BallotProtocol,
        ]
    )
    yield
    db.close()


app = FastAPI(lifespan=lifespan, host="0.0.0.0", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="votx/static"), name="static")
templates = Jinja2Templates(directory="votx/templates")

app.include_router(admin.router)
app.include_router(beamer.router)
app.include_router(vote.router)


@app.get("/", response_class=HTMLResponse)
def index(request: Request, voter_token: Annotated[str | None, Cookie()] = None):
    try:
        get_voter_token_from_jwt(voter_token)
        response = RedirectResponse("/vote/")
        return response

    except Exception:
        return templates.TemplateResponse(
            request=request, name="index.jinja", context={"alert_message": ""}
        )


@app.get("/datenschutz")
def get_privacy(request: Request):
    return templates.TemplateResponse(request=request, name="privacy.jinja")


@app.get("/impressum")
def get_imprint(request: Request):
    return templates.TemplateResponse(request=request, name="imprint.jinja")


@app.post("/register")
def register_voter(request: Request, registration_token: Annotated[str, Form()]):
    # check if registrationToken is in db
    try:
        token = RegistrationToken.get(RegistrationToken.token == registration_token)
    except DoesNotExist:
        return templates.TemplateResponse(
            request=request,
            name="index.jinja",
            context={"alert_message": "Ungültiges Registrierungstoken!"},
        )

    # check if registrationToken is in use already
    if len(token.voterToken) > 0:
        return templates.TemplateResponse(
            request=request,
            name="index.jinja",
            context={"alert_message": "Registrierungstoken bereits genutzt!"},
        )

    # create voterToken
    voter_token = VoterToken.create(
        token=secrets.token_hex(64), registration_token=token
    )

    expiry_time = (
        int(os.environ.get("VOTER_TOKEN_EXPIRY"))
        if "VOTER_TOKEN_EXPIRY" in os.environ
        else 60 * 24
    )

    response = RedirectResponse("/vote/")
    response.set_cookie(
        key="voter_token",
        value=create_voter_jwt(voter_token.token, expiry_time),
        secure=True,
        httponly=True,
        expires=expiry_time * 60,
    )
    return response


@app.post("/login/", response_class=HTMLResponse)
@app.get("/login/", response_class=HTMLResponse)
def get_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.jinja")


@app.post("/login/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenData:
    if not (form_data.username == "admin" and check_password(form_data.password)):
        raise AdminUnauthorizedException()

    expiry_time = (
        int(os.environ.get("ADMIN_TOKEN_EXPIRY"))
        if "ADMIN_TOKEN_EXPIRY" in os.environ
        else 20
    )

    access_token = create_access_token({"sub": form_data.username}, expiry_time)
    response = RedirectResponse("/admin/")
    response.set_cookie(
        key="session_token", value=access_token, secure=True, httponly=True
    )
    return response


@app.exception_handler(AdminUnauthorizedException)
async def admin_unauthorized_exception_handler(request, e: AdminUnauthorizedException):
    return RedirectResponse(url="/login")


@app.exception_handler(VoterUnauthorizedException)
async def voter_unauthorized_exception_handler(request, e: VoterUnauthorizedException):
    return RedirectResponse(url="/")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
