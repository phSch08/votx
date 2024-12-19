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

from .security import create_access_token, create_voter_jwt

from .dbModels import Ballot, BallotVoteGroup, UserVote, Vote, VoteGroup, VoteGroupMembership, VoteOption, VoterToken, db, RegistrationToken
from .Models import TokenData

import uvicorn
import secrets
from .routers import admin, beamer, vote

import logging

load_dotenv('.env')
print(os.environ)

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
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
        token = RegistrationToken.get(RegistrationToken.token == registrationToken)
    except DoesNotExist:
        return (False, "Registration Token does not exist!")
    
    # check if registrationToken is in use already
    if len(token.voterToken) > 0:
        return (False, "Registration Token already used!")
    
    # create voterToken
    voterToken = VoterToken.create(token = secrets.token_hex(64), registrationToken=token)
    
    expiry_time = int(os.environ.get('TOKEN_EXPIRY')) if 'TOKEN_EXPIRY' in os.environ else 60*24
    
    response =  RedirectResponse("/vote/")
    response.set_cookie(
        key="voter_token",
        value=create_voter_jwt(voterToken.token, expiry_time),
        secure=True,
        httponly=True,
        expires=expiry_time * 60
    )
    return response

@app.get("/login/", response_class=HTMLResponse)
def getLogin(request: Request):
    return templates.TemplateResponse(request=request, name="login.jinja")

@app.post("/login/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> TokenData:
    if not (form_data.username == "admin" and form_data.password == "admin"):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password!",
            headers={"WWW-Authenticate": "Bearer"})
    access_token = create_access_token({"sub": form_data.username}, 20)
    response =  RedirectResponse("/admin/")
    response.set_cookie(key="session_token", value=access_token, secure=True, httponly=True)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)