from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from ..Models import Token
from ..security import create_access_token

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/login",
    tags=["login"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    if not (form_data.username == "admin" and form_data.password == "admin"):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password!",
            headers={"WWW-Authenticate": "Bearer"})
    access_token = create_access_token({"sub": form_data.username})
    response =  RedirectResponse("/admin/")
    response.set_cookie(key="session_token", value=access_token, secure=True, httponly=True)
    return response

@router.get("/", response_class=HTMLResponse)
def getLogin(request: Request):
    return templates.TemplateResponse(request=request, name="login.jinja")