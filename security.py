from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import jwt

SECRET_KEY = "e2e103d93c55748c3acc2c25ed1d1d5ac8e667f05d56e1785833fdf43027b950"
ALGORITHM = "HS256"

def get_voter_token_from_jwt(voter_token: Annotated[str | None, Cookie()]) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate voter token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(voter_token, SECRET_KEY, algorithms=[ALGORITHM])
        voter_token: str = payload.get("token")
        if voter_token is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    return voter_token
    
def create_voter_jwt(voter_token: str, expiry_minutes: int):
    return create_access_token({"token": voter_token}, expiry_minutes)
    

def get_logged_in_user(session_token: Annotated[str | None, Cookie()]) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    print(session_token)
    try:
        payload = jwt.decode(session_token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    return username


def create_access_token(data: dict, expiry_minutes: int):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt