import os
from datetime import datetime, timedelta, timezone
from hashlib import pbkdf2_hmac
from typing import Annotated

import jwt
from fastapi import Cookie

from .exceptions.admin_unauthorized_exception import AdminUnauthorizedException
from .exceptions.voter_unauthorized_exception import VoterUnauthorizedException

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")


def get_voter_token_from_jwt(
    voter_token: Annotated[str | None, Cookie()] = None,
) -> str:
    try:
        payload = jwt.decode(voter_token, SECRET_KEY, algorithms=[ALGORITHM])
        voter_token: str = payload.get("token")
        if voter_token is None:
            raise VoterUnauthorizedException()
    except jwt.InvalidTokenError as e:
        raise VoterUnauthorizedException() from e
    return voter_token


def create_voter_jwt(voter_token: str, expiry_minutes: int):
    return create_access_token({"token": voter_token}, expiry_minutes)


def get_logged_in_user(session_token: Annotated[str | None, Cookie()] = None) -> str:
    print(session_token)
    try:
        payload = jwt.decode(session_token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        username: str = payload.get("sub")
        if username is None:
            raise AdminUnauthorizedException()
    except jwt.InvalidTokenError as e:
        raise AdminUnauthorizedException() from e
    return username


def create_access_token(data: dict, expiry_minutes: int):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def check_password(password: str) -> bool:
    """Check if the given password is valid.

    Check if the given password matches the password stored in environment variable
    using the salt from environment.

    Args:
        password (str): Password to check validity for.

    Returns:
        bool: wether the password is valid.

    """
    salt = bytes.fromhex(os.environ.get("ADMIN_PASSWORD_SALT"))
    print(salt)
    print(hash_password(password, salt))
    print(bytes.fromhex(os.environ.get("ADMIN_PASSWORD_HASH")).hex())
    return hash_password(password, salt) == os.environ.get("ADMIN_PASSWORD_HASH")


def hash_password(password: str, salt: bytes) -> str:
    """Create a hash of the given password and salt using PBKDF2.

    Args:
        password (str): secret password, len should not exceed 1024 characters
        salt (bytes): random value, should be about 16 or more characters long

    Returns:
        str: the hashed password

    """
    hashed_password = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 500000)
    return hashed_password.hex()
