import os
from typing import Tuple, Annotated
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from peewee import DoesNotExist
from dotenv import load_dotenv

from .exceptions.AdminUnauthorizedException import AdminUnauthorizedException
from .exceptions.VoterUnauthorizedException import VoterUnauthorizedException

from .security import check_password, create_access_token, create_voter_jwt

from .dbModels import Ballot, BallotVoteGroup, UserVote, Vote, VoteGroup, VoteGroupMembership, VoteOption, VoterToken, db, RegistrationToken
from .Models import TokenData

import uvicorn
import secrets
from .routers import admin, beamer, vote

import logging

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init("votix")
    db.connect()
    db.create_tables([
        RegistrationToken,
        VoterToken,
        VoteGroup,
        VoteGroupMembership,
        Ballot,
        VoteOption,
        UserVote,
        Vote,
        BallotVoteGroup])
    yield
    db.close()

app = FastAPI(lifespan=lifespan, host='0.0.0.0')
app.mount("/static", StaticFiles(directory="votx/static"), name="static")
templates = Jinja2Templates(directory="votx/templates")

app.include_router(admin.router)
app.include_router(beamer.router)
app.include_router(vote.router)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.jinja")


@app.post("/register")
def register_voter(registrationToken: Annotated[str, Form()]):
    # check if registrationToken is in db
    try:
        token = RegistrationToken.get(
            RegistrationToken.token == registrationToken)
    except DoesNotExist:
        return (False, "Registration Token does not exist!")

    # check if registrationToken is in use already
    if len(token.voterToken) > 0:
        return (False, "Registration Token already used!")

    # create voterToken
    voterToken = VoterToken.create(
        token=secrets.token_hex(64), registrationToken=token)

    expiry_time = int(os.environ.get('VOTER_TOKEN_EXPIRY')
                      ) if 'VOTER_TOKEN_EXPIRY' in os.environ else 60*24

    response = RedirectResponse("/vote/")
    response.set_cookie(
        key="voter_token",
        value=create_voter_jwt(voterToken.token, expiry_time),
        secure=True,
        httponly=True,
        expires=expiry_time * 60
    )
    return response


@app.post("/login/", response_class=HTMLResponse)
@app.get("/login/", response_class=HTMLResponse)
def getLogin(request: Request):
    return templates.TemplateResponse(request=request, name="login.jinja")


@app.post("/login/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> TokenData:
    if not (form_data.username == "admin" and check_password(form_data.password)):
        raise AdminUnauthorizedException()

    expiry_time = int(os.environ.get('ADMIN_TOKEN_EXPIRY')
                      ) if 'ADMIN_TOKEN_EXPIRY' in os.environ else 20

    access_token = create_access_token(
        {"sub": form_data.username}, expiry_time)
    response = RedirectResponse("/admin/")
    response.set_cookie(key="session_token",
                        value=access_token, secure=True, httponly=True)
    return response


@app.exception_handler(AdminUnauthorizedException)
async def custom_http_exception_handler(request, e: AdminUnauthorizedException):
    return RedirectResponse(url="/login")


@app.exception_handler(VoterUnauthorizedException)
async def custom_http_exception_handler(request, e: VoterUnauthorizedException):
    return RedirectResponse(url="/")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
