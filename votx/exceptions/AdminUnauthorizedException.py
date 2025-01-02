from fastapi import HTTPException, status


class AdminUnauthorizedException(HTTPException):
    def __init__(self, detail="Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

